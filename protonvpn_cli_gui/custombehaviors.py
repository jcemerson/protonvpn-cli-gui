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
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (  # noqa # pylint: disable=no-name-in-module
    AliasProperty,
    BooleanProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty
)


class GrabBehavior(object):
    last_touch = ObjectProperty(None)

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        if self.disabled:  # noqa # pylint: disable=no-member
            return False
        if not self.collide_point(touch.x, touch.y):  # noqa # pylint: disable=no-member
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        return super().on_touch_down(touch)  # noqa # pylint: disable=no-member

    def on_touch_move(self, touch):
        if super().on_touch_move(touch):  # noqa # pylint: disable=no-member
            return True
        if touch.grab_current is self:
            return True
        return self in touch.ud

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            result = super().on_touch_up(touch)  # noqa # pylint: disable=no-member
            touch.ungrab(self)
            self.last_touch = touch
            return result


class ButtonBehavior(object):
    '''Button behavior.

    :Events:
        `on_press`
            Fired when the button is pressed.
        `on_release`
            Fired when the button is released (i.e. the touch/click that
            pressed the button goes away).
    '''

    state = OptionProperty('normal', options=('normal', 'down'))
    '''State of the button, must be one of 'normal' or 'down'.
    The state is 'down' only when the button is currently touched/clicked,
    otherwise 'normal'.

    :attr:`state` is an :class:`~kivy.properties.OptionProperty`.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_press')  # noqa # pylint: disable=no-member
        self.register_event_type('on_release')  # noqa # pylint: disable=no-member
        super().__init__()

    def _do_press(self):
        self.state = 'down'

    def _do_release(self):
        self.state = 'normal'

    # TODO: Consider revising to use self.walk() instead of for loop.
    def on_touch_down(self, touch):
        if self in touch.ud:
            if isinstance(self, ButtonBehavior):  # noqa # pylint: disable=no-member
                for child in self.children:  # noqa # pylint: disable=no-member
                    if isinstance(child, ButtonBehavior):  # noqa # pylint: disable=no-member
                        if (self.collide_point(*touch.pos) and  # noqa # pylint: disable=no-member
                                child.collide_point(*touch.pos)):
                            return child.on_touch_down(touch)

            self._do_press()
            self.dispatch('on_press')  # noqa # pylint: disable=no-member
        return super().on_touch_down(touch)  # noqa # pylint: disable=no-member

    def on_touch_move(self, touch):
        return super().on_touch_move(touch)  # noqa # pylint: disable=no-member

    # TODO: Consider revising to use self.walk() instead of for loop.
    def on_touch_up(self, touch):
        if self in touch.ud:
            if isinstance(self, ButtonBehavior):
                for child in self.children:  # noqa # pylint: disable=no-member
                    if isinstance(child, ButtonBehavior):
                        if (self.collide_point(*touch.pos) and  # noqa # pylint: disable=no-member
                                child.collide_point(*touch.pos)):
                            return child.on_touch_up(touch)
            self._do_release()
            self.dispatch('on_release')  # noqa # pylint: disable=no-member
        return super().on_touch_up(touch)  # noqa # pylint: disable=no-member

    def on_press(self):
        pass

    def on_release(self):
        pass

    def trigger_action(self, duration=0.1):
        '''Trigger whatever action(s) have been bound to the button by calling
        both the on_press and on_release callbacks.

        This simulates a quick button press without using any touch events.

        Duration is the length of the press in seconds. Pass 0 if you want
        the action to happen instantly.

        .. versionadded:: 1.8.0
        '''
        self._do_press()
        self.dispatch('on_press')  # noqa # pylint: disable=no-member

        def trigger_release(dt):
            self._do_release()
            self.dispatch('on_release')  # noqa # pylint: disable=no-member
        if not duration:
            trigger_release(0)
        else:
            Clock.schedule_once(trigger_release, duration)


class HoverBehavior(object):
    """
    This mixin class provides hoverable behavior, allowing for various
    triggerable events based on the cursor's position over a widget.

    Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget
    """

    hovered = BooleanProperty(False)
    border_point = ObjectProperty(None)
    """
    Contains the last relevant point received by the Hoverable. This can be
    used in `on_enter` or `on_leave` events in order to know from which point
    the event was dispatched.
    """

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')  # noqa # pylint: disable=no-member
        self.register_event_type('on_leave')  # noqa # pylint: disable=no-member
        Window.bind(mouse_pos=self.on_mouse_pos)
        super().__init__()

    def on_mouse_pos(self, *args):
        if not self.get_root_window():  # noqa # pylint: disable=no-member
            return
        pos = args[1]
        # Allow to compensate for relative layout
        is_inside = self.collide_point(*self.to_widget(*pos))  # noqa # pylint: disable=assignment-from-no-return, no-member
        # If cursor is already hovering over widget, stop and do nothing.
        if self.hovered == is_inside:
            return
        # Otherwise, set hover attributes and dispatch events
        self.hovered = is_inside
        self.border_point = pos
        if is_inside:
            self.dispatch('on_enter')  # noqa # pylint: disable=no-member
        else:
            self.dispatch('on_leave')  # noqa # pylint: disable=no-member

    def on_enter(self, *args):
        pass

    def on_leave(self):
        pass
