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
from kivy.core.window import Window
from kivy.properties import (  # noqa # pylint: disable=no-name-in-module
    AliasProperty,
    BooleanProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty
)
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewNode

# Local
from custombehaviors import ButtonBehavior, GrabBehavior, HoverBehavior  # noqa # pylint: disable=import-error


class PvpnStandardButton(HoverBehavior, Button):
    """Standard Button with HoverBehavior."""

    normal_cursor = 'arrow'
    hover_cursor = 'hand'

    def __init__(self, **kwargs):
        super().__init__()

    def on_enter(self):
        if self.hover_cursor:
            Window.set_system_cursor(self.hover_cursor)

    def on_leave(self):
        if self.hover_cursor:
            Window.set_system_cursor(self.normal_cursor)


class PvpnImageButton(GrabBehavior, ButtonBehavior, HoverBehavior, Image):
    """Clickable/hoverable image with Button behavior."""

    normal_img = None
    hover_img = None
    normal_cursor = 'arrow'
    hover_cursor = 'hand'

    def __init__(self, **kwargs):
        super().__init__()

    def on_enter(self):
        if self.hover_img:
            self.source = self.hover_img
        if self.hover_cursor:
            Window.set_system_cursor(self.hover_cursor)

    def on_leave(self):
        if self.hover_img:
            self.source = self.normal_img
        if self.hover_cursor:
            Window.set_system_cursor(self.normal_cursor)

    def on_press_img(self):
        self.source = self.normal_img

    def on_release_img(self):
        self.source = self.hover_img


class PvpnImageToggleButton(ToggleButtonBehavior, HoverBehavior, Image):
    """Clickable image with Toggle behavior."""

    normal_cursor = 'arrow'
    hover_cursor = 'hand'

    def __init__(self, **kwargs):
        super().__init__()

    def on_enter(self):
        if self.hover_cursor:
            Window.set_system_cursor(self.hover_cursor)

    def on_leave(self):
        if self.hover_cursor:
            Window.set_system_cursor(self.normal_cursor)


class SecureCoreSwitch(PvpnImageToggleButton):
    """Clickable image with Toggle behavior."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = './images/toggle-switch-off_150.png'
        self.app_root = None

    def on_state(self, widget, value):
        if value == 'down':
            self.source = './images/toggle-switch-on_150.png'
        else:
            self.source = './images/toggle-switch-off_150.png'

    def on_press(self):
        # Get app.root instance
        self.app_root = App.get_running_app().root
        # Update connection status
        self.app_root.vpn_connected = self.app_root.is_connected()
        # Launch Secure Core notification popup
        Clock.schedule_once(self.app_root.secure_core_notification, 0.05)


class PvpnToggleSwitch(PvpnImageToggleButton):
    """Clickable image with Toggle behavior."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = './images/toggle-switch-off_150.png'
        self.app_root = None

    def on_state(self, widget, value):
        if value == 'down':
            self.source = './images/toggle-switch-on_150.png'
        else:
            self.source = './images/toggle-switch-off_150.png'


class PvpnPopup(Popup):
    """Custom popup class themed for this app."""
    pass
    # def on_touch_down(self, touch):
    #     if self.collide_point(*touch.pos):
    #         return True


class SecureCoreNotificationPopup(PvpnPopup):
    """Notification when Secure Core switch is toggled on."""

    label_text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__()
        self.label_text = kwargs['label_text']


class ConnectingNotificationPopup(PvpnPopup):
    """Notification when new connection is underway."""

    label_text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__()
        self.label_text = kwargs['label_text']


class DisconnectingNotificationPopup(PvpnPopup):
    """Notification when a disconnection is underway."""

    label_text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__()
        self.label_text = kwargs['label_text']


class PvpnScrollView(ScrollView):
    pass


# TreeView for listing Countries and their servers:
class PvpnTreeView(TreeView):
    """Custom TreeView class."""

    def __init__(self, **kwargs):
        super().__init__()
        self.root_options = kwargs['root_options']
        self.hide_root = kwargs['hide_root']


# # TreeViewNode for listing Countries:
class PvpnServerTreeCountryNode(GrabBehavior, ButtonBehavior,
                                BoxLayout, TreeViewNode):
    """Clickable server tree nodes for displaying available countries."""

    def __init__(self, **kwargs):
        super().__init__()

        self.bind(is_selected=self.unselect_node)
        self.bind(is_selected=self.close_unselected_nodes)

    # def unselect_node(self, dt):
    def unselect_node(self, *args):
        """Deselect selected node upon closing."""
        if self.is_selected and self.is_open:
            self.parent.deselect_node()

    def close_unselected_nodes(self, *args):
        """Close open nodes when another node is opened."""
        for node in self.parent.iterate_open_nodes():
            if node.is_open and node is not self and not node.is_selected:
                self.parent.toggle_node(node)


class PvpnServerTreeServerNode(BoxLayout, TreeViewNode):
    """Server tree nodes for displaying available servers."""
    pass


class PvpnDropDown(DropDown):
    """Custom button class themed for this app."""
    pass

    # TODO: Resolve issues with hovering over dropdowns and/or dropdown buttons
    # hovered = BooleanProperty(False)
    # border_point = ObjectProperty(None)
    # normal_cursor = 'arrow'
    # hover_cursor = 'hand'

    # def __init__(self, **kwargs):
    #     self.register_event_type('on_enter')  # noqa # pylint: disable=no-member
    #     self.register_event_type('on_leave')  # noqa # pylint: disable=no-member
    #     Window.bind(mouse_pos=self.on_mouse_pos)
    #     super().__init__()

    # def collide_point(self, x, y):
    #     """
    #     Modified from kivy.uix.widget.collied_point due to issues when working
    #     with dropdowns.
    #     """
    #     return x <= self.right and y <= self.top

    # def on_mouse_pos(self, *args):
    #     if not self.get_root_window():  # noqa # pylint: disable=no-member
    #         return
    #     pos = args[1]
    #     # Allow to compensate for relative layout
    #     is_inside = self.collide_point(*self.to_widget(*pos))  # noqa # pylint: disable=assignment-from-no-return, no-member

    #     if self.hovered == is_inside:
    #         return
    #     # Otherwise, set hover attributes and dispatch events
    #     print(is_inside)
    #     print(self.hovered)
    #     self.hovered = is_inside
    #     self.border_point = pos
    #     if is_inside:
    #         self.dispatch('on_enter')  # noqa # pylint: disable=no-member
    #     else:
    #         self.dispatch('on_leave')  # noqa # pylint: disable=no-member

    # def on_enter(self):
    #     print('on_enter() fired')
    #     if self.hover_cursor:
    #         Window.set_system_cursor(self.hover_cursor)

    # def on_leave(self):
    #     print('on_leave() fired')
    #     if self.hover_cursor:
    #         Window.set_system_cursor(self.normal_cursor)


class PvpnDropDownButton(Button):
# class PvpnDropDownButton(PvpnImageButton):
    """Custom button class themed for this app."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = './images/dropdown-button-up_underline.png'

    def on_state(self, widget, value):
        if value == 'down':
            print('down')
            # self.source = './images/dropdown-button-down.png'
        else:
            print('normal')
            # self.source = './images/dropdown-button-up_underline.png'

    def on_press(self):
        self.source = './images/dropdown-button-down.png'
        print("I've been pressed", self.state)

    def on_release(self):
        self.source = './images/dropdown-button-up_underline.png'
        print("I've been released", self.state)
