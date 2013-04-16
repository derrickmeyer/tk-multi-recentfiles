"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

A window which show the latest work files.

"""

import tank

class RecentFiles(tank.platform.Application):

    def init_app(self):
        """
        Called as the application is being initialized
        """
        tk_multi_recentfiles = self.import_module("tk_multi_recentfiles")
        cb = lambda : tk_multi_recentfiles.show_dialog(self)
        # add stuff to main menu
        self.engine.register_command("recent_files", cb, {"title": "Recent Work Files..."})

        # only launch the dialog once at startup
        # use tank object to store this flag
        if not hasattr(tank, '_tk_multi_recent_files_shown'):
            # very first time we run this app
            tank._tk_multi_recent_files_shown = True
            # show the UI at startup - but only if the engine supports a UI
            if self.get_setting('launch_at_startup') and self.engine.has_ui:
                tk_multi_recentfiles.show_dialog(self)
