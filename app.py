"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

A window in Nuke which show the latest work files.

"""

import tank

class NukeRecentFiles(tank.platform.Application):

    def init_app(self):
        """
        Called as the application is being initialized
        """
        import tk_nuke_recentfiles
        self.app_handler = tk_nuke_recentfiles.AppHandler(self)

        # add stuff to main menu
        self.engine.register_command("Recent Work Files...", self.app_handler.show_dialog)

        # only launch the dialog once at startup
        # use tank object to store this flag
        if not hasattr(tank, '_tk_nuke_recent_files_shown'):
            # very first time we run this app
            tank._tk_nuke_recent_files_shown = True
            # show the UI
            if self.get_setting('launch_at_startup'):
                self.app_handler.show_dialog()
