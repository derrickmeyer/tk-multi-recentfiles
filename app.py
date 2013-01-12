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
        self.app_handler = tk_multi_recentfiles.AppHandler(self)

        # add stuff to main menu
        self.engine.register_command("Recent Work Files...", self.app_handler.show_dialog)

        # only launch the dialog once at startup
        # use tank object to store this flag
        if not hasattr(tank, '_tk_multi_recent_files_shown'):
            # very first time we run this app
            tank._tk_multi_recent_files_shown = True
            # show the UI at startup - but only if the engine supports a UI
            if self.get_setting('launch_at_startup') and self.engine.has_ui:
                self.app_handler.show_dialog()
