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
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty
)
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.spinner import SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeView, TreeViewNode

# Local
from .custombehaviors import ButtonBehavior, GrabBehavior, HoverBehavior  # noqa # pylint: disable=import-error


class DefaultTextInput(TextInput):
    pass


class PvpnStandardButton(HoverBehavior, Button):
    """Standard Button with HoverBehavior."""

    normal_img = None
    hover_img = None
    normal_cursor = 'arrow'
    hover_cursor = 'hand'
    disabled_cursor = 'no'

    def __init__(self, **kwargs):
        super().__init__()

    def on_enter(self, *args):
        if self.hover_img:
            self.source = self.hover_img
        if self.hover_cursor:
            if self.disabled:
                Window.set_system_cursor(self.disabled_cursor)
            else:
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
    disabled_cursor = 'no'

    def __init__(self, **kwargs):
        super().__init__()

    def on_enter(self, *args):
        if self.hover_img:
            self.source = self.hover_img
        if self.hover_cursor:
            if self.disabled:
                Window.set_system_cursor(self.disabled_cursor)
            else:
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
    disabled_cursor = 'no'

    def __init__(self, **kwargs):
        super().__init__()

    def on_enter(self, *args):
        if self.hover_cursor:
            if self.disabled:
                Window.set_system_cursor(self.disabled_cursor)
            else:
                Window.set_system_cursor(self.hover_cursor)

    def on_leave(self):
        if self.hover_cursor:
            Window.set_system_cursor(self.normal_cursor)


class SecureCoreSwitch(PvpnImageToggleButton):
    """Clickable image with Toggle behavior."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.disabled:
            if self.state == 'down':
                self.source = './images/toggle-switch-on-disabled_150.png'
            else:
                self.source = './images/toggle-switch-off-disabled_150.png'
        else:
            if self.state == 'down':
                self.source = './images/toggle-switch-on_150.png'
            else:
                self.source = './images/toggle-switch-off_150.png'
        self.app = None
        self.register_event_type('on_disabled')

    def on_state(self, widget, value):
        if self.disabled:
            if value == 'down':
                self.source = './images/toggle-switch-on-disabled_150.png'
            else:
                self.source = './images/toggle-switch-off-disabled_150.png'
        else:
            if value == 'down':
                self.source = './images/toggle-switch-on_150.png'
            else:
                self.source = './images/toggle-switch-off_150.png'

    def on_press(self):
        # Get app.root instance
        self.app = App.get_running_app()
        # Update connection status
        self.app.root.vpn_connected = self.app.root.is_connected()
        # Launch Secure Core notification popup
        Clock.schedule_once(self.app.root.secure_core_notification, 0.05)

    def on_disabled(self, *args):
        if self.disabled:
            if self.state == 'down':
                self.source = './images/toggle-switch-on-disabled_150.png'
            else:
                self.source = './images/toggle-switch-off-disabled_150.png'
        else:
            if self.state == 'down':
                self.source = './images/toggle-switch-on_150.png'
            else:
                self.source = './images/toggle-switch-off_150.png'


class PvpnToggleSwitch(PvpnImageToggleButton):
    """Clickable image with Toggle behavior."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = './images/toggle-switch-off_150.png'
        self.app = None
        self.register_event_type('on_disable')

    def on_state(self, widget, value):
        if value == 'down':
            self.source = './images/toggle-switch-on_150.png'
        else:
            self.source = './images/toggle-switch-off_150.png'

    def on_disable(self):
        if self.disabled:
            if self.state == 'down':
                self.source = './images/toggle-switch-on_150-disabled.png'
            else:
                self.source = './images/toggle-switch-off_150-disabled.png'
        else:
            if self.state == 'down':
                self.source = './images/toggle-switch-on_150.png'
            else:
                self.source = './images/toggle-switch-off_150.png'


class PvpnPopupLabel(Label):
    """Custom Lable for PvpnPopup."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = 23
        self.halign = 'center'
        self.valign = 'center'


class PvpnPopup(Popup):
    """Custom popup class themed for this app."""

    title = StringProperty('')
    label_text = StringProperty('')
    auto_close = BooleanProperty(True)
    dt = NumericProperty(1.5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = kwargs['title']
        self.label_text = kwargs['label_text']

    def on_open(self):
        if self.auto_close:
            Clock.schedule_once(self.dismiss, self.dt)

    # def on_touch_down(self, touch):
    #     if self.collide_point(*touch.pos):
    #         return True


class SecureCoreNotificationPopup(PvpnPopup):
    """Notification when Secure Core switch is toggled on."""
    pass


class ExitPopup(PvpnPopup):
    """Confirmation of choice to exit the app."""
    pass


class PvpnScrollView(ScrollView):
    pass


class PvpnGridLayout(GridLayout):
    """GridLayout container for use in PvpnScrollView objects."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = (None)
        self.bind(minimum_height=self.setter('height'))


class PvpnTreeView(TreeView):
    """Custom TreeView class for listing Countries and their servers."""

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
    #     Modified from kivy.uix.widget.collied_point due to issues when working  # noqa
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
    """Custom button class themed for this app."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = './images/dropdown-button-up_underline.png'

    def on_state(self, widget, value):
        if value == 'down':
            self.source = './images/dropdown-button-down.png'
        else:
            self.source = './images/dropdown-button-up_underline.png'

    def on_press(self):
        pass

    def on_release(self):
        pass


class PvpnSpinner(Spinner):
    """Custom spinner class themeed for this app."""
    pass


class PvpnSpinnerOption(SpinnerOption):
    """Custom spinner option class themeed for this app."""
    pass
