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
from kivy.uix.screenmanager import Screen


class InitializeProfileScreen(Screen):
    """Create profile for VPN connection."""
    pass
    # name = StringProperty('_init_profile_screen_')
    # # pass1 = StringProperty('')
    # # pass2 = StringProperty('')

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    #     print(self.ids)
    #     self.pass1 = self.ids
    #     # self.pass2 = self.ids.password2
    #     # print(self)
    #     # self.pass1 = self.ids.password1
    #     # self.pass2 = self.ids.password2

    #     self.bind(pass1=self.confirm_password)

    # def confirm_password(self):
    #     if self.pass1:
    #         self.pass2.disabled = False
