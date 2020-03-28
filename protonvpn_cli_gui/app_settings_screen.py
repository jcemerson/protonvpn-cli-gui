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

# Kivy Libraries
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen


class AppSettingsScreen(Screen):
    """Maintain App-specific settings"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Schedule remainder of init with delay to allow app to fully start.
        # This avoids error referencing App instance before it's ready.
        Clock.schedule_once(self.after_init)

    def after_init(self, dt):
        # Get app reference
        self.app = App.get_running_app()

        # For now, Remember Login defaults to 'on' and is disabled.
        # Future release will allow user to always purge profile upon app exit.
        self.remember_login_switch = (
            self.app.root.ids.app_settings_screen.ids.remember_login_switch
        )
        if self.remember_login_switch.disabled:
            if self.remember_login_switch.state == 'down':
                self.remember_login_switch.source = (
                    './images/toggle-switch-on-disabled_150.png'
                )
            else:
                self.remember_login_switch.source == (
                    './images/toggle-switch-off-disabled_150.png'
                )
        # For now, Start on Boot defaults to 'off' and is disabled.
        # Future release will allow user to select this option.
        self.start_on_boot = (
            self.app.root.ids.app_settings_screen.ids.start_on_boot_switch
        )
        if self.start_on_boot.disabled:
            if self.start_on_boot.state == 'down':
                self.start_on_boot.source = (
                    './images/toggle-switch-on-disabled_150.png'
                )
            else:
                self.start_on_boot.source = (
                    './images/toggle-switch-off-disabled_150.png'
                )
        # For now, Auto-Connect on Launch defaults to 'off' and is disabled.
        # Future release will allow user to select this option.
        self.auto_connect = (
            self.app.root.ids.app_settings_screen.ids.auto_connect_switch
        )
        if self.auto_connect.disabled:
            if self.auto_connect.state == 'down':
                self.auto_connect.source = (
                    './images/toggle-switch-on-disabled_150.png'
                )
            else:
                self.auto_connect.source = (
                    './images/toggle-switch-off-disabled_150.png'
                )

        # Define function of Quick Connect button in current connection window.
        # Defaults to 'connect to fastest server', but can be set to any
        # connection profile the User defines.
