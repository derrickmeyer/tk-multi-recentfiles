"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import tank
import os
import sys
import datetime
import threading 


from PySide import QtCore, QtGui
from .browser_widget import BrowserWidget
from .browser_widget import ListItem
from .browser_widget import ListHeader

class WorkFileBrowserWidget(BrowserWidget):

    history_item_action = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        BrowserWidget.__init__(self, parent)
        self._user_thumb_mapping = {}

    def open_history_file(self):
        try:
            path = self.sender().path
        except:
            QtGui.QMessageBox.critical(self, "Cannot Resolve Path!", "Cannot resolve this path!")            
            return
        self.history_item_action.emit(path)    

    def get_file_owner(self, path):
        try:
            import pwd # wont work on windows
            owner = pwd.getpwuid(os.stat(path).st_uid).pw_name
            return owner
        except Exception, e:
            return None

    def get_file_owner_thumb_url(self, path):
        # return the thumbnail url of the owner of the file
        # may fall back to None if owner cannot be determined
        # or if the user in shotgun cannot be resolve/has no image
        
        owner = self.get_file_owner(path)        
        if owner is None:
            return None
        
        if owner in self._user_thumb_mapping:
            result = self._user_thumb_mapping[owner]
        else:
            result = self._app.shotgun.find_one("HumanUser", [["login", "is", owner]], ["image"])
            self._user_thumb_mapping[owner] = result  
        
        if result is None:
            return None
        
        # yay!
        return result["image"]
    

    def get_data(self, data):
    
        # add recent items to the context menu
        # data structure for organising stuff
        work_items = {}
        
        # now get all work items
        tw = self._app.get_template("template_work")
        ctx_fields = self._app.context.as_template_fields(tw)
        for wi in self._app.tank.paths_from_template(tw, ctx_fields):
            # get the fields
            fields = tw.get_fields(wi)
            name = fields["name"]
            version = fields["version"]
            # group it by name, then by version
            if not name in work_items:
                work_items[name] = {}
            work_items[name][version] = wi
            
        # we now have a dict like this    
        # {"name1": {1:"/path", 2:"/path"}, "name2": {...}}
        # now create menu items
        data = []
        for name in sorted(work_items.keys()):
            max_ver = max(work_items[name].keys())
            path = work_items[name][max_ver]
            data.append({"name": name, 
                         "all_versions": work_items[name],
                         "version": max_ver, 
                         "path": path, 
                         "file_owner": self.get_file_owner(path),
                         "file_owner_thumb": self.get_file_owner_thumb_url(path),
                         "mtime": os.path.getmtime(path)})

        return data
            


    def process_result(self, result):

        # result is a list of dicts on the form:
        # {"name": name, "version": max_ver, "path": path, "mtime": 122312}
        
        if len(result) == 0:
            self.set_message("No items found!")
            return
        
        for r in sorted(result, key=lambda x:x["mtime"], reverse=True):
            
            time_stamp = datetime.datetime.fromtimestamp(r["mtime"])

            i = self.add_item(ListItem)                
            
            details = []
            details.append("<b>%s.nk</b>" % r["name"])
            details.append("Latest version: %03d" % r["version"])
            details.append("Last updated: %s" % time_stamp)
            
            if r["file_owner"] is None:
                details.append("Created by: Unknown User")
            else:
                details.append("Created by: %s" % r["file_owner"])
            
            i.set_details("<br>".join(details))
            if r["file_owner_thumb"] is None:
                # no user thumb. Assign default thumb
                i.set_thumbnail(":/res/work_file.png")
            else:
                i.set_thumbnail(r["file_owner_thumb"])

            # make a context menu where all previous versions can be grabbed too
            i.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
            cnt = 0
            for version in sorted(r["all_versions"].keys(), reverse=True):         
                # max 20 versions on menu
                if cnt > 20:
                    break
                cnt += 1
                i.action = QtGui.QAction("Open previous version %03d" % version, i)
                i.action.path = r["all_versions"][version]                
                i.action.triggered.connect(self.open_history_file)                       
                i.addAction(i.action)
                                
            # assign some data to the object
            i.path = r["path"]
