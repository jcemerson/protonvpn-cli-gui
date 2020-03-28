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
from functools import partial
from configparser import ConfigParser
import os
import re
import subprocess
from time import time

# Kivy Libraries
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty  # noqa # pylint: disable=no-name-in-module
from kivy.uix.screenmanager import Screen, FallOutTransition

# protonvpn-cli-ng Functions
from protonvpn_cli import constants as pvpncli_constants
from protonvpn_cli import logger as pvpncli_logger
from protonvpn_cli import utils as pvpncli_utils

# Local
from .widgets import (  # noqa # pylint: disable=import-error
    DefaultTextInput,
    PvpnPopup,
    PvpnPopupLabel,
)


class Dns_Input(DefaultTextInput):
    """Only allow valid IP formatted values."""

    name = StringProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_text_validate=self.validate_ip)

    def valid_char(self, substring):
        """Determine if char is digit or period/dot."""
        valid_chars = re.compile(r'([0-9]|\.| )')
        if re.search(valid_chars, substring):
            return True

    def insert_text(self, substring, from_undo=False):
        """Accept valid input or launch popup upon invalid input."""
        if self.valid_char(substring):
            return super().insert_text(substring, from_undo=from_undo)
        else:
            self.invalid_textinput_popup = PvpnPopup(
                title="Attention!",
                label_text=(
                    "You've entered an invalid character.\n"
                    "Enter a digit (0-9), period (dot), or space."
                ),
            )
            self.invalid_textinput_popup_label = PvpnPopupLabel(
                text=self.invalid_textinput_popup.label_text,
                text_size=self.size,
            )
            self.invalid_textinput_popup.add_widget(
                self.invalid_textinput_popup_label
            )
            self.invalid_textinput_popup.open()

    def validate_ip(self, instance, *args):
        """Check for valid IP format."""
        ip_pattern = re.compile(
            r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'
            r'(/(3[0-2]|[12][0-9]|[1-9]))?$'  # Matches CIDR
        )
        ip_list = self.text.split(' ')
        if not self.valid_ip_count(ip_list):
            for ip in ip_list:
                if ip != '':
                    if not re.search(ip_pattern, ip):
                        self.invalid_ip_popup = PvpnPopup(
                            title="Attention!",
                            label_text="Invalid IPv4 address",
                        )
                        self.invalid_ip_popup_label = PvpnPopupLabel(
                            text=self.invalid_ip_popup.label_text,
                            text_size=self.size,
                        )
                        self.invalid_ip_popup.add_widget(
                            self.invalid_ip_popup_label
                        )
                        self.invalid_ip_popup.open()
                        if not self.focus:
                            Clock.schedule_once(self.reset_focus, 0.01)
                        break

    def valid_ip_count(self, ip_list):
        """Validate max number of allwed IP entries."""
        ip_list = ip_list
        if self.name == '_split_tunnel_ip_list_':
            valid_length = 1
        if self.name == '_dns_server_list_':
            valid_length = 3
        if len(ip_list) > valid_length:
            self.too_many_ips_popup = PvpnPopup(
                title='Attention!',
                label_text='Max allowed number of IPs exceeded.',
                auto_close=True,
            )
            self.too_many_ips_popup_label = PvpnPopupLabel(
                text=self.too_many_ips_popup.label_text,
                text_size=self.size,
            )
            self.too_many_ips_popup_label.text_size = self.size
            self.too_many_ips_popup.add_widget(self.too_many_ips_popup_label)
            self.too_many_ips_popup.open()
            if not self.focus:
                Clock.schedule_once(self.reset_focus, 0.01)
            return

    def reset_focus(self, dt):
        """Called with a delay to prevent KeyError when resetting focus."""
        self.focus = True

    def on_focus(self, instance, focused):
        """When field loses focus, validate IP content."""
        if not focused:
            self.validate_ip(instance)


class VpnSettingsScreen(Screen):
    """Create/Maintain user's profile for VPN connection."""

    # Define conversion values from GUI to CLI
    plan_options = {
        'Free': 0,
        'Basic': 1,
        'Plus/Visionary': 2,
    }
    dns_management_options = {
        'Enable Leak Protection': 1,
        'Custom DNS Servers': 0,
        'None': 0,
    }
    kill_switch_options = {
        'Disable': 0,
        'Enable - Block LAN': 1,
        'Enable - Allow LAN': 2,
    }
    split_tunnel_options = {
        'Disable': 0,
        'Enable': 1,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Schedule remainder of init with delay to allow app to fully start.
        # This avoids error referencing App instance before it's ready.
        Clock.schedule_once(self.after_init)

    def after_init(self, dt):
        # Determine if profile has already been initialized
        try:
            self.is_initialized = (
                int(pvpncli_utils.get_config_value("USER", "initialized"))
            )
        except KeyError:
            self.is_initialized = None

        # Get app reference
        self.app = App.get_running_app()

        # Set input field references
        # Username
        self.username = (
            self.app.root.ids.vpn_settings_screen.ids.username
        )
        # Password
        self.password = (
            self.app.root.ids.vpn_settings_screen.ids.password
        )
        self.password_show = (
            self.app.root.ids.vpn_settings_screen.ids.password_show
        )
        self.password_confirm = (
            self.app.root.ids.vpn_settings_screen.ids.password_confirm
        )
        self.password_confirm_show = (
            self.app.root.ids.vpn_settings_screen.ids.password_confirm_show
        )

        # Proton VPN Plan
        self.pvpn_plan = (
            self.app.root.ids.vpn_settings_screen.ids.pvpn_plan
        )

        # Default Protocol
        self.default_protocol = (
            self.app.root.ids.vpn_settings_screen.ids.default_protocol
        )

        # DNS Management
        self.dns_management = (
            self.app.root.ids.vpn_settings_screen.ids.dns_management
        )
        self.dns_selection = (
            self.app.root.ids.vpn_settings_screen.ids.dns_spinner
        )
        self.dns_server_list = Dns_Input(
            hint_text=' Enter DNS IPs (space-separated; max 3)',
            padding=[0, 15, 0, 0]
        )
        self.dns_server_list.name = '_dns_server_list_'
        self.dns_server_list.background_normal = (
            './images/text-input-background-normal-highlight.png'
        )
        self.dns_server_list.background_active = (
            './images/text-input-background-active-highlight.png'
        )

        # Kill Switch & Split Tunneling
        self.kill_switch = (
            self.app.root.ids.vpn_settings_screen.ids.kill_switch
        )
        self.split_tunneling = (
            self.app.root.ids.vpn_settings_screen.ids.split_tunneling
        )
        self.split_tunneling_spinner = (
            self.app.root.ids.vpn_settings_screen.ids.split_tunneling_spinner
        )
        self.split_tunneling_ip_list = Dns_Input(
            hint_text=' Enter IP/CIDR to exclude from VPN',
            padding=[0, 15, 0, 0],
        )
        self.split_tunneling_ip_list.name = '_split_tunnel_ip_list_'
        self.split_tunneling_ip_list.background_normal = (
            './images/text-input-background-normal-highlight.png'
        )
        self.split_tunneling_ip_list.background_active = (
            './images/text-input-background-active-highlight.png'
        )
        self.update_button = (
            self.app.root.ids.vpn_settings_screen.ids.update_button
        )

        # If profile already initialized, load profile values.
        if self.is_initialized:
            self.get_current_values()
            self.set_current_values()
        else:
            if self.is_initialized is None:
                # Create directory if not already there.
                if not os.path.isdir(pvpncli_constants.CONFIG_DIR):
                    os.mkdir(pvpncli_constants.CONFIG_DIR)
                    pvpncli_logger.logger.debug("Config Directory created")
                    pvpncli_utils.change_file_owner(
                        pvpncli_constants.CONFIG_DIR
                    )
                # Initialize config file.
                self.init_config_file()
                # Create OpenVPN template.
                pvpncli_utils.make_ovpn_template()
            # Set values to detect updates
            self.username_val = self.username.text
            self.passwd_val = self.password.text
            self.tier_val = self.pvpn_plan.text
            self.prot_val = self.default_protocol.text
            self.dns_val = self.dns_selection.text
            self.dns_ip_val = self.dns_server_list.text
            self.kill_switch_val = self.kill_switch.text
            self.split_tunl_val = self.split_tunneling_spinner.text
            self.split_tunnel_ips = self.split_tunneling_ip_list.text

        # Set bindings:
        self.password.bind(text=self.enable_confirm_password)
        self.password_confirm.bind(disabled=self.show_password_confirm_disable)
        self.dns_selection.bind(text=self.configure_dns_servers)
        self.kill_switch.bind(text=partial(
            self.split_tunnel_or_kill_switch, self.kill_switch.name
        ))
        self.split_tunneling_spinner.bind(text=partial(
            self.split_tunnel_or_kill_switch, self.split_tunneling_spinner.name
        ))
        self.split_tunneling_spinner.bind(text=self.configure_split_tunnel_ip)

        # Enable Update button upon changes
        self.username.bind(text=self.update_button_enable)
        self.password.bind(text=self.update_button_enable)
        self.pvpn_plan.bind(text=self.update_button_enable)
        self.dns_selection.bind(text=self.update_button_enable)
        self.dns_server_list.bind(text=self.update_button_enable)
        self.default_protocol.bind(text=self.update_button_enable)
        self.kill_switch.bind(text=self.update_button_enable)
        self.split_tunneling_spinner.bind(text=self.update_button_enable)
        self.split_tunneling_ip_list.bind(text=self.update_button_enable)

    def get_current_values(self):
        """Get current VPN Settings values from pvpn-cli.cfg."""
        # Username
        self.username_val = pvpncli_utils.get_config_value("USER", "username")
        # Password
        cmd = f'/bin/cat {pvpncli_constants.PASSFILE}'
        user_passwd = subprocess.check_output(cmd, shell=True).decode()
        self.usr_val, self.passwd_val = user_passwd.split()
        # ProtonVPN Plan/Tier
        self.tier_val = int(pvpncli_utils.get_config_value("USER", "tier"))
        for opt, val in self.plan_options.items():
            if val == self.tier_val:
                self.tier_val = opt
        # Default Protocol
        self.prot_val = pvpncli_utils.get_config_value(
            "USER",
            "default_protocol"
        )
        self.prot_val = self.prot_val.upper()
        # DNS Management
        # Check for custom_dns values.
        self.dns_ip_val = pvpncli_utils.get_config_value(
            "USER",
            "custom_dns"
        )
        # Determine selection for dns_leak_protection
        self.dns_val = int(pvpncli_utils.get_config_value(
            "USER",
            "dns_leak_protection"
        ))
        # If config dns_leak_protection is 0, determine if there's a
        # custom_dns value or not. If yes, set to 'Custom DNS Server'
        # else, set to "None".
        if self.dns_val == 0:
            if self.dns_ip_val != 'None':
                self.dns_val = 'Custom DNS Servers'
            else:
                self.dns_val = 'None'
        else:
            self.dns_val = 'Enable Leak Protection'

        # Kill Switch
        self.kill_switch_val = int(pvpncli_utils.get_config_value(
            "USER",
            "killswitch"
        ))
        for opt, val in self.kill_switch_options.items():
            if val == self.kill_switch_val:
                self.kill_switch_val = opt
        # Split Tunneling
        self.split_tunl_val = int(pvpncli_utils.get_config_value(
            "USER",
            "split_tunnel"
        ))
        for opt, val in self.split_tunnel_options.items():
            if val == self.split_tunl_val:
                self.split_tunl_val = opt

        self.split_tunnel_ips = ''
        if os.path.isfile(pvpncli_constants.SPLIT_TUNNEL_FILE):
            with open(pvpncli_constants.SPLIT_TUNNEL_FILE, "r") as f:
                content = f.readlines()
                for line in content:
                    line = line.rstrip("\n")
                    self.split_tunnel_ips += line
            self.split_tunneling_ip_list.text = self.split_tunnel_ips

    def set_current_values(self):
        """Set GUI fields based on values in pvpn-cli.cfg."""
        self.username.text = self.username_val
        self.password.text = self.passwd_val
        self.password_confirm.text = self.password.text
        self.password_confirm.disabled = False
        self.password_confirm_show.disabled = False
        self.password_confirm_show.source = './images/eye-show.png'
        self.pvpn_plan.text = self.tier_val
        self.default_protocol.text = self.prot_val
        self.dns_selection.text = self.dns_val
        if self.dns_selection.text == 'Custom DNS Servers':
            self.dns_server_list.text = self.dns_ip_val
            self.dns_management.add_widget(self.dns_server_list)
        self.kill_switch.text = self.kill_switch_val
        self.split_tunneling_spinner.text = self.split_tunl_val
        if self.split_tunneling_spinner.text == 'Enable':
            self.split_tunneling_ip_list.text = self.split_tunnel_ips
            self.split_tunneling.add_widget(self.split_tunneling_ip_list)

    def close_button(self):
        """Determine button's function."""
        if self.is_initialized:
            self.app.root.transition = FallOutTransition()
            self.app.root.current = '_main_screen_'
        else:
            self.app.stop()

    def update_button_enable(self, *args):
        """Determine button's function."""
        updates = self.updates_made()
        if len(updates):
            self.update_button.disabled = False
        else:
            self.update_button.disabled = True

    def show_password(self, field):
        """Toggle displaying/hiding the password fields' text."""
        if field.password:
            field.password = False
        else:
            field.password = True

    def toggle_show_hide_password(self, button):
        """Change between show/hide icons."""
        if button.source == './images/eye-show.png':
            button.source = './images/eye-hide.png'
        else:
            button.source = './images/eye-show.png'

    def show_password_confirm_disable(self, *args):
        """Toggle the image set for active/inactive icons."""
        if self.password_confirm.disabled:
            if self.password_confirm_show.source == './images/eye-show.png':  # noqa
                self.password_confirm_show.source = (
                    './images/eye-show-disabled.png'
                )
            elif self.password_confirm_show.source == './images/eye-hide.png':
                self.password_confirm_show.source = (
                    './images/eye-hide-disabled.png'
                )
            self.password_confirm_show.disabled = True
        else:
            if self.password_confirm_show.source == './images/eye-show-disabled.png':  # noqa
                self.password_confirm_show.source = (
                    './images/eye-show.png'
                )
            elif self.password_confirm_show.source == './images/eye-hide-disabled.png':  # noqa
                self.password_confirm_show.source = (
                    './images/eye-hide.png'
                )
            self.password_confirm_show.disabled = False

    def enable_confirm_password(self, *args):
        """Ensure password is entered prior to enabling confirmation field."""
        if self.password.text:
            self.password_confirm.disabled = False
        else:
            self.password_confirm.disabled = True

    def confirm_password_match(self, *args):
        """Valiate password and password_confirm values match."""
        if self.password_confirm.text != '':
            if self.password.text != self.password_confirm.text:
                self.password_mismatch_popup = PvpnPopup(
                    title="Attention!",
                    label_text="Passwords do not match. Try again.",
                )
                self.password_mismatch_popup_label = PvpnPopupLabel(
                    text=self.password_mismatch_popup.label_text,
                    text_size=self.size,
                )
                self.password_mismatch_popup.add_widget(
                    self.password_mismatch_popup_label
                )
                self.password_mismatch_popup.open()
            else:
                return True

    def configure_dns_servers(self, *args):
        """If Configure DNS Servers is selected, open text-input field."""
        if self.dns_selection.text == 'Custom DNS Servers':
            self.dns_management.add_widget(self.dns_server_list)
        else:
            self.dns_server_list.text = ''
            self.dns_management.remove_widget(self.dns_server_list)

    def configure_split_tunnel_ip(self, *args):
        """If Split Tunneling is selected, open text-input field."""
        if self.split_tunneling_spinner.text == 'Enable':
            self.split_tunneling.add_widget(self.split_tunneling_ip_list)
        else:
            self.split_tunneling_ip_list.text = ''
            self.split_tunneling.remove_widget(self.split_tunneling_ip_list)  # noqa

    def split_tunnel_or_kill_switch(self, trigger, *args):
        """Split Tunneling and Kill Switch are mutually exclusive."""
        if trigger == self.split_tunneling_spinner.name and self.kill_switch.text != 'Disable':  # noqa
            if self.split_tunneling_spinner.text != 'Disable':
                self.split_tunnel_popup = PvpnPopup(
                    title='Attention!',
                    label_text=(
                        'By enabling Split Tunneling,\n'
                        'the Kill Switch will be disabled.'
                    )

                )
                self.split_tunnel_popup_label = PvpnPopupLabel(
                    text=self.split_tunnel_popup.label_text,
                    text_size=self.size,
                )
                self.split_tunnel_popup.add_widget(
                    self.split_tunnel_popup_label
                )
                self.split_tunnel_popup.open()
                self.kill_switch.text = 'Disable'

        if trigger == self.kill_switch.name and self.split_tunneling_spinner.text != 'Disable':  # noqa
            if self.kill_switch.text != 'Disable':
                self.kill_switch_popup = PvpnPopup(
                    title='Attention!',
                    label_text=(
                        'By enabling the Kill Switch,\n'
                        'Split Tunneling will be disabled.'
                    )
                )
                self.kill_switch_popup_label = PvpnPopupLabel(
                    text=self.kill_switch_popup.label_text,
                    text_size=self.size,
                )
                self.kill_switch_popup.add_widget(self.kill_switch_popup_label)
                self.kill_switch_popup.open()
                self.split_tunneling_spinner.text = 'Disable'

    def missing_required_fields(self):
        """Check that minimum required fields are populated."""
        missing = []
        if self.username.text == '':
            missing.append('Username')
        if self.password.text == '':
            missing.append('Password')
        if self.password.text != '':
            if self.password_confirm.text == '':
                missing.append('Password Confirmation')
        if self.dns_selection.text == 'Custom DNS Servers':
            if self.dns_server_list.text == '':
                missing.append('Custom DNS Servers')
        if self.split_tunneling_spinner.text == 'Enable':
            if self.split_tunneling_ip_list.text == '':
                missing.append('Split Tunneling IP')
        if len(missing):
            missing_items = '\n'.join(missing)
            self.required_data_missing_popup = PvpnPopup(
                title='Attention!',
                label_text=(
                    'Please enter missing required information:\n\n'
                    f'{missing_items}'
                ),
                auto_close=True,
                dt=3,
                size_hint_y=None,
                height='300dp',
            )
            self.missing_data_label = PvpnPopupLabel(
                text=self.required_data_missing_popup.label_text,
                text_size=(self.size[0], None),
            )
            self.required_data_missing_popup.add_widget(
                self.missing_data_label
            )
            self.required_data_missing_popup.open()
            return True
        else:
            return False

    def init_config_file(self):
        """"Initialize configuration file."""
        config = ConfigParser()
        config["USER"] = {
            "username": "None",
            "tier": "None",
            "default_protocol": "None",
            "initialized": "0",
            "dns_leak_protection": "1",
            "custom_dns": "None",
            "check_update_interval": "3",
        }
        config["metadata"] = {
            "last_api_pull": "0",
            "last_update_check": str(int(time())),
        }

        with open(pvpncli_constants.CONFIG_FILE, "w") as f:
            config.write(f)
        pvpncli_utils.change_file_owner(pvpncli_constants.CONFIG_FILE)
        pvpncli_logger.logger.debug("pvpn-cli.cfg initialized")

    def set_config_value(self, group, key, value):
        """Write a specific value to CONFIG_FILE"""
        config = ConfigParser()
        config.read(pvpncli_constants.CONFIG_FILE)
        config[group][key] = str(value)

        with open(pvpncli_constants.CONFIG_FILE, "w+") as f:
            config.write(f)

    def set_username_password(self):
        """Set the ProtonVPN Username and Password."""
        self.set_config_value("USER", "username", self.username.text)

        with open(pvpncli_constants.PASSFILE, "w") as f:
            f.write(f"{self.username.text}\n{self.password.text}")
            pvpncli_logger.logger.debug("Passfile updated")
            os.chmod(pvpncli_constants.PASSFILE, 0o600)

    def set_split_tunnel(self):
        """Enable or disable split tunneling"""
        with open(pvpncli_constants.SPLIT_TUNNEL_FILE, "a") as f:
            f.write(f'\n{self.split_tunneling_ip_list.text}')

        if os.path.isfile(pvpncli_constants.SPLIT_TUNNEL_FILE):
            pvpncli_utils.change_file_owner(
                pvpncli_constants.SPLIT_TUNNEL_FILE
            )
        else:
            # If no file exists, split tunneling should be disabled again.
            pvpncli_logger.logger.debug("No split tunneling file existing.")
            self.set_config_value("USER", "split_tunnel", 0)
            os.remove(pvpncli_constants.SPLIT_TUNNEL_FILE)
        # Update OpenVPN template.
        pvpncli_utils.make_ovpn_template()

    def updates_made(self):
        """Compare current to initial values to determine if updates made."""
        updates = []
        # if self.is_initialized:
        if self.password.text != self.passwd_val:
            updates.append('userpass')
        else:
            if self.username.text != self.username_val:
                updates.append('username')
        if self.pvpn_plan.text != self.tier_val:
            updates.append('plan')
        if self.default_protocol.text != self.prot_val:
            updates.append('protocol')
        if self.dns_selection.text != self.dns_val:
            updates.append('dns_mgmt')
        if self.dns_selection == 'Custom DNS Servers':
            if self.dns_server_list.text != self.dns_ip_val:
                updates.append('custom_dns')
        if self.kill_switch.text != self.kill_switch_val:
            updates.append('killswitch')
        if self.split_tunneling_spinner.text != self.split_tunl_val:
            updates.append('split_tunnel')
        if self.split_tunneling_ip_list.text != self.split_tunnel_ips:
            updates.append('split_tunnel_ip')
        return updates

    def write_config(self):
        """Write profile info to pvpn-cli config file and init ovpn files."""

        # Set custom_dns value for pvpn-cli.cfg
        if str(self.dns_server_list.text) == '':
            custom_dns_ips = None
        else:
            custom_dns_ips = str(self.dns_server_list.text)

        update_calls = {
            "userpass": self.set_username_password(),
            "username": self.set_config_value(
                "USER",
                "username",
                self.username.text,
            ),
            "plan": self.set_config_value(
                "USER",
                "tier",
                str(self.plan_options[self.pvpn_plan.text]),
            ),
            "protocol": self.set_config_value(
                "USER",
                "default_protocol",
                self.default_protocol.text.lower(),
            ),
            "dns_mgmt": self.set_config_value(
                "USER",
                "dns_leak_protection",
                str(self.dns_management_options[self.dns_selection.text]),
            ),
            "custom_dns": self.set_config_value(
                "USER",
                "custom_dns",
                custom_dns_ips,
            ),
            "killswitch": self.set_config_value(
                "USER",
                "killswitch",
                str(self.kill_switch_options[self.kill_switch.text]),
            ),
            "split_tunnel": self.set_config_value(
                "USER",
                "split_tunnel",
                str(self.split_tunnel_options[
                        self.split_tunneling_spinner.text
                    ]),
            ),
            "split_tunnel_ip": self.set_config_value(
                "USER",
                "split_tunnel",
                str(self.split_tunnel_options[
                        self.split_tunneling_spinner.text
                    ]),
            ),
        }

        if not self.missing_required_fields():
            if self.confirm_password_match():
                updates = self.updates_made()
                for update in updates:
                    update_calls[update]

                # Reset current values for detecting updates.
                self.get_current_values()

                # Reset update button to disabled.
                self.update_button.disabled = True  # noqa

                # Mark profile as initialized
                if not self.is_initialized:
                    self.set_config_value("USER", "initialized", 1)
                    self.is_initialized = 1
                    self.app.root.initialize_application()
                # Check for active connection and notify to reconnect
                try:
                    if self.app.root.vpn_connected:
                        self.vpn_settings_update_popup = PvpnPopup(
                            title='Attention!',
                            label_text=(
                                'To apply these latest updates, disconnect and'
                                ' reconnect the VPN.'
                            ),
                            auto_close=True,
                            dt=2,
                            size_hint_y=0.3,
                        )
                        self.vpn_settings_update_label = PvpnPopupLabel(
                            text=self.vpn_settings_update_popup.label_text,
                            text_size=self.size,
                        )
                        self.vpn_settings_update_popup.add_widget(
                            self.vpn_settings_update_label
                        )
                        self.vpn_settings_update_popup.open()
                except AttributeError:
                    # If vpn_connected doesn't exist, open main screen
                    pass
