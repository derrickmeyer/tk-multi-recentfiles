"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

Hook that loads items into the current scene. 

This hook supports a number of different platforms and the behaviour on each platform is
different. See code comments for details.


"""
import tank
import os
from tank.platform.qt import QtGui

class AddFileToScene(tank.Hook):
    
    def execute(self, engine_name, file_path, **kwargs):
        """
        Hook entry point and app-specific code dispatcher
        """
                
        if self.parent.engine.name == "tk-nuke":
            self.load_item_from_path_nuke(file_path)
        
        elif self.parent.engine.name == "tk-maya":
            self.load_item_from_path_maya(file_path)
        
        elif self.parent.engine.name == "tk-motionbuilder":
            self.load_item_from_path_motionbuilder(file_path)
        
        elif self.parent.engine.name == "tk-3dsmax":
            self.load_item_from_path_3dsmax(file_path)

        elif self.parent.engine.name == "tk-photoshop":
            self.load_item_from_path_photoshop(file_path)

        elif self.parent.engine.name == 'tk-hiero':
            self.load_item_from_path_hiero(file_path)

        else:
            raise tank.TankError("Unsupported engine '%s'!" % engine_name)
                
        
        ##########################################################################################

    def load_item_from_path_hiero(self, path):

        import hiero

        # close open projects
        hiero.core.closeAllProjects(False)

        # fix slashes
        path = path.replace(os.sep, '/')
        # open
        hiero.core.openProject(path)

        
    def load_item_from_path_nuke(self, path):
        
        import nuke
        # fix slashes
        path = path.replace(os.sep, "/")
        # open
        nuke.scriptOpen(path)
        
        
    def load_item_from_path_maya(self, path):
        
        import pymel.core as pm
        import maya.cmds as cmds
        # fix slashes
        path = path.replace(os.sep, "/")
        
        if cmds.file(query=True, modified=True):
            
            # changes have been made to the scene
            res = QtGui.QMessageBox.question(None,
                                             "Save your scene?",
                                             "Your scene has unsaved changes. Save before proceeding?",
                                             QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)
            
            if res == QtGui.QMessageBox.Cancel:
                # return to dialog
                return

            elif res == QtGui.QMessageBox.No:
                # don't save!
                pm.system.openFile(path, force=True)
            
            else:
                # save before!
                
                if pm.sceneName() != "":
                    # scene has a name!
                    # normal save
                    cmds.file(save=True, force=True)
                else:
                    # scene does not have a name. 
                    # save as dialog
                    cmds.SaveSceneAs()
                    # not sure about return value here, so check the scene!
                    if cmds.file(query=True, modified=True):
                        # still unsaved changes
                        # assume user clicked cancel in dialog
                        return
                    
        # okay all good to go. Scene is saved and has a name.
        # now we can safely replace it with the desired scene... :)
        pm.system.openFile(path)
        
        
    def load_item_from_path_motionbuilder(self, path):

        from pyfbsdk import FBApplication
        app = FBApplication()
        app.FileOpen(path)
        
        
    def load_item_from_path_3dsmax(self, path):

        from Py3dsMax import mxs
        
        # there is a file open
        if mxs.getSaveRequired():
            # there are unsaved changes in the scene
            # TODO: handle this for the user!
            
            # the currently opened file has not been saved
            mxs.messageBox("Your current scene has unsaved changes. Please save it before proceeding.")
            return
                    
        else:
            # no need to save any change. load new file.
            mxs.loadMaxFile(path)

    def load_item_from_path_photoshop(self, path):
        import photoshop
        f = photoshop.RemoteObject('flash.filesystem::File', path)
        photoshop.app.load(f)
