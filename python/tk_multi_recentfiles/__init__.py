"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

"""

def show_dialog(app):
    # defer imports so that the app works gracefully in batch modes
    from .dialog import AppDialog
            
    app.engine.show_dialog("Recent Work Files", app, AppDialog, app)
    