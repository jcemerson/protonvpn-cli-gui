#    This file is part of ProtonVPN-CLI-GUI for Linux.

#    Copyright (C) <year>  <name of author>
#
#    ProtonVPN-CLI-GUI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Standard Libraries
import os

# Kivy Libraries
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen  # , CardTransition, NoTransition

# protonvpn-cli-ng Functions
from protonvpn_cli import constants as pvpncli_constants


class WelcomeScreen(Screen):
    """Intro screen. Check for profile & connect or request authentication."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        """Run upon screenload and call subsequent method."""
        app = App.get_running_app()

        # Check for update:
        print("calling app.check_update")
        app.check_update()
        Clock.schedule_once(self.verify_login_credentials)

    def verify_login_credentials(self, dt):
        """Confirm required files for connecting exist, else initialize."""
        app = App.get_running_app()
        # If the config directory doesn't exist, start initialization.
        if not os.path.isdir(pvpncli_constants.CONFIG_DIR):
            # load profile initialization process
            Clock.schedule_once(app.root.initialize_vpn_settings, 3)
        else:
            # If the config directory does exist, check for required files.
            required_files = [
                pvpncli_constants.CONFIG_FILE,
                pvpncli_constants.PASSFILE,
            ]
            try:
                login_files = os.listdir(pvpncli_constants.CONFIG_DIR)
                for i, f in enumerate(login_files):
                    login_files[i] = os.path.join(
                        pvpncli_constants.CONFIG_DIR,
                        f,
                    )
                required_files_found = len(required_files)
                for required_file in required_files:
                    if required_file not in login_files:
                        # print(f'{required_file} not found. Initilize new profile.') # noqa
                        required_files_found -= 1
                        break
                if required_files_found == len(required_files):
                    # print('Required files found, starting app.')
                    Clock.schedule_once(app.root.close_welcome_screen) # noqa
                    # load connection and populate status messages on screen # noqa
                else:
                    # load profile inititalization screen
                    Clock.schedule_once(app.root.initialize_vpn_settings, 3) # noqa
            except Exception as e:
                print('Exception from verify_login_credentials: ', e)
