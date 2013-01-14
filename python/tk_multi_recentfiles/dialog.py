"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import tank
import os
import sys
import threading

from tank.platform.qt import QtCore, QtGui, TankQDialog
from .ui.dialog import Ui_Dialog

class AppDialog(TankQDialog):

    def __init__(self, app):
        TankQDialog.__init__(self)
        # set up the UI
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)    
        self._app = app

        # display the context in the title bar of the window
        ctx = self._app.context        
        
        # fallback if no context known
        ctx_name = "Recent Files"
        
        if ctx.project:
            # Ghosts
            ctx_name = "%s" % ctx.project["name"]
        
        if ctx.project and ctx.entity:
            # Ghosts, Shot ABC
            ctx_name = "%s, %s %s" % (ctx.project["name"], ctx.entity["type"], ctx.entity["name"])

        if ctx.step and ctx.project and ctx.entity:
            # Ghosts, Shot ABC, Lighting
            ctx_name = "%s, %s %s, %s" % (ctx.project["name"], ctx.entity["type"], ctx.entity["name"], ctx.step["name"])
        
        self.setWindowTitle(ctx_name)
        
        # set up the browsers
        self.ui.browser.set_app(self._app)
        self.ui.browser.set_label("Tank Recent Work Files")
        
        self.ui.browser.action_requested.connect( self.load_item )
        self.ui.browser.history_item_action.connect( self.load_item_from_path )
        self.ui.browser.selection_changed.connect( self.toggle_load_button_enabled )
        self.ui.load.clicked.connect( self.load_item )
                
        self.toggle_load_button_enabled()
        # load data from shotgun
        self.setup_file_list()        
        
    ########################################################################################
    # make sure we trap when the dialog is closed so that we can shut down 
    # our threads. Nuke does not do proper cleanup on exit.
    
    def _cleanup(self):
        self.ui.browser.destroy()
        
    def closeEvent(self, event):
        self._cleanup()
        # okay to close!
        event.accept()
        
    def accept(self):
        self._cleanup()
        TankQDialog.accept(self)
        
    def reject(self):
        self._cleanup()
        TankQDialog.reject(self)
        
    def done(self, status):
        self._cleanup()
        TankQDialog.done(self, status)
        
    ########################################################################################
    # basic business logic        
        
    def toggle_load_button_enabled(self):
        """
        Control the enabled state of the load button
        """
        curr_selection = self.ui.browser.get_selected_item()
        if curr_selection is None:
            self.ui.load.setEnabled(False)
        else:
            self.ui.load.setEnabled(True)
        
    def setup_file_list(self): 
        self.ui.browser.clear()
        d = {}
        self.ui.browser.load(d)
        
    def load_item(self):
        """
        Load something into the scene
        """
        curr_selection = self.ui.browser.get_selected_item()
        if curr_selection is None:
            return
        
        self.load_item_from_path(curr_selection.path)
        
        
    def load_item_from_path(self, path):

        # call out to our hook for loading.
        self._app.log_debug("Calling load hook for %s" % path)

        self._app.execute_hook("hook_add_file_to_scene", 
                               engine_name=self._app.engine.name, 
                               file_path=path)
        
        # close dialog
        self.done(0)
        
        
        
