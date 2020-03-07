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

import kivy
# Minimum supported version; Ignore at your own risk.
kivy.require('1.10.1') # noqa

# Config must be set prior to other imports due to use of Window.
# Config must define the size prior to the Window getting created.
from kivy.config import Config
# Set config.ini setting for this instance of the app.
Config.set('graphics', 'borderless', '0')
Config.set('graphics', 'height', '950')
Config.set('graphics', 'width', '520')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'fullscreen', '0')
Config.set('input', 'mouse', 'mouse,disable_on_activity')
Config.set('graphics', 'window_state', 'visible')
Config.set('kivy', 'desktop', '1')
Config.set('kivy', 'exit_on_escape', '0')
Config.set('kivy', 'window_icon', './images/protonvpn-sign-white.png')

# Standard Libraries
from functools import partial  # noqa
import subprocess  # noqa
from time import time  # noqa

# Kivy Libraries
from kivy.app import App  # noqa
from kivy.clock import Clock  # noqa
from kivy.core.window import Window  # noqa
from kivy.properties import (  # noqa # pylint: disable=no-name-in-module
    AliasProperty,
    BooleanProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout  # noqa
from kivy.uix.image import Image  # noqa
from kivy.uix.label import Label  # noqa
from kivy.uix.screenmanager import (  # noqa
    FadeTransition,
    ScreenManager,
)

# protonvpn-cli-ng Functions
from protonvpn_cli import constants as pvpncli_constants  # noqa
from protonvpn_cli import country_codes as pvpncli_country_codes  # noqa
from protonvpn_cli import logger as pvpncli_logger  # noqa
from protonvpn_cli import utils as pvpncli_utils  # noqa

# Local
from widgets import (  # noqa # pylint: disable=import-error
    ConnectingNotificationPopup,
    DisconnectingNotificationPopup,
    PvpnPopup,
    PvpnTreeView,
    PvpnServerTreeCountryNode,
    PvpnServerTreeServerNode,
    SecureCoreNotificationPopup,
)
from screens import WelcomeScreen  # noqa

# Set version of GUI app
PVPN_CLI_GUI_VERSION = 'ProtonVPN-CLI-GUI v0.1'


class ProtonVpnGui(ScreenManager, BoxLayout):
    """Top-level/root containing the "meat" of the app."""

    vpn_connected = BooleanProperty(False)

    def __init__(self):
        """Initialize the ProtonVPN GUI App."""
        super().__init__()

        # Instantiate Window object for min, max, and close window functions:
        self._app_window = Window

        # Capture cli and gui versions for display on welcome screen.
        welcome_screen = self.ids.welcome_screen
        protonvpn_cli_version = f'ProtonVPN-CLI v{pvpncli_constants.VERSION}'
        welcome_screen.ids.pvpn_cli_version.text = protonvpn_cli_version
        welcome_screen.ids.pvpn_gui_verion.text = PVPN_CLI_GUI_VERSION
        # Indicator that app was just initialized.
        self.app_newly_initialized = True
        # Get default protocol (TCP or UDP) and User's account tier-level.
        self.default_protocol = pvpncli_utils.get_config_value(
            "USER",
            "default_protocol",
        )
        self.tier = int(pvpncli_utils.get_config_value(
            "USER",
            "tier",
        ))
        self.secure_core = self.ids.main_screen.ids.secure_core_switch
        # 0: Free, 1: Basic, 2: Plus, etc.
        if self.tier < 2:
            self.secure_core.disabled = True
        # State of Secure Core Notification Popup
        self.sc_notification_open = False
        # Schedule check for connection change and trigger update if found.
        self.cnxn_check = Clock.schedule_interval(self.check_current_cnxn, 1)
        # Schedule refresh of data trans/recvd.
        self.data_trans = Clock.schedule_interval(self.get_data_up_down, 1)
        # Schedule refresh of connection time
        self.cnxn_time = Clock.schedule_interval(self.get_connection_time, 1)
        # Current connection status
        self.vpn_connected = self.is_connected()
        # Used for detecting connection changes
        self.last_known_connection = None
        # Schedule update of server tree every 5 min
        self.update_server_tree = (
            Clock.schedule_interval(self.update_server_tree_info, 300)
        )
        # Set initial connection window button image based on connection status
        self.cnxn_wndw_btn = self.ids.main_screen.ids.connection_window_button
        if self.vpn_connected:
            self.cnxn_wndw_btn.normal_img = './images/disconnect.png'
            self.cnxn_wndw_btn.hover_img = './images/disconnect_hover.png'
            self.cnxn_wndw_btn.source = './images/disconnect.png'
        else:
            self.cnxn_wndw_btn.normal_img = './images/quick_connect.png'
            self.cnxn_wndw_btn.hover_img = './images/quick_connect_hover.png'
            self.cnxn_wndw_btn.source = './images/quick_connect.png'

    def close_welcome_screen(self, dt):
        """Transition from welcome screen after [n] seconds."""
        self.initialize_application()
        self.transition = FadeTransition()
        self.current = '_main_screen_'

    def initialize_profile(self, dt):
        """Start a new profile for VPN connection."""
        self.transition = FadeTransition()
        self.current = '_init_profile_screen_'

    def initialize_application(self):
        """Initialize root class."""
        # Update current connection info in connection window.
        self.update_current_connection()
        # Start regularly scheduled  status checks on connection state.
        self.cnxn_check()
        # Initialize server tree.
        self.build_server_tree()

    def is_connected(self):
        """
        Local version of CLI function, minus logging, to be used for
        frequent, scheduled connection checks. ProtonVPN-CLI's function
        is still used to connect, disconnect, etc.

        Purpose: Check if a VPN connection already exists.
        """
        ovpn_processes = subprocess.run(
            ["pgrep", "--exact", "openvpn"],
            stdout=subprocess.PIPE
        )
        ovpn_processes = ovpn_processes.stdout.decode("utf-8").split()
        return True if ovpn_processes != [] else False

    def connection_changed(self, *dt):
        """Compare current connection to last known; True = change."""
        # Gather details of current connected server.
        current_connection = pvpncli_utils.get_config_value(
            "metadata",
            "connected_server",
        )
        # Compare curren connection to last known connection.
        if current_connection != self.last_known_connection:
            return True
        else:
            return False

    def check_current_cnxn(self, *dt):
        """Update connection info if change detected."""
        self.vpn_connected = self.is_connected()
        # If VPN is connected:
        if self.vpn_connected:
            if self.connection_changed():
                self.update_current_connection()
        else:
            if self.last_known_connection:
                self.set_disconnected()

    def update_current_connection(self, *dt):
        """Update the current connection info."""
        # Check for active connection
        self.vpn_connected = self.is_connected()
        if self.vpn_connected:
            # Cancel scheduled events, if they exist.
            if self.data_trans:
                self.data_trans.cancel()
            if self.cnxn_time:
                self.cnxn_time.cancel()

            servers = pvpncli_utils.get_servers()

            ip = None
            while not ip:
                try:
                    ip = pvpncli_utils.get_ip_info()[0]
                # except Exception as e:
                except SystemExit:
                    print('Exception from update_current_connection(): SystemExit')  # noqa
                    print('reconnect cmd sent')
                    self.exec_cmd('sudo protonvpn reconnect')

            self.ids.main_screen.ids.exit_server_ip.text = f'IP: {ip}'

            connected_server = pvpncli_utils.get_config_value(
                "metadata",
                "connected_server",
            )
            self.last_known_connection = connected_server

            # Set Secure Core switch if app newly initialized. Otherwise the
            # switch state is determined by User interaction afterwards.
            if self.app_newly_initialized:
                feature = pvpncli_utils.get_server_value(
                    connected_server,
                    "Features",
                    servers,
                )
                if feature == 1:
                    self.secure_core.state = 'down'
                else:
                    self.secure_core.state = 'normal'

            self.app_newly_initialized = False
            country_code = pvpncli_utils.get_server_value(
                connected_server,
                "ExitCountry",
                servers,
            )
            cnxn_window = self.ids.main_screen.ids.connection_window
            flag = f'./images/flags/large/{country_code.lower()}-large.jpg'
            cnxn_window.img_source = flag

            country = pvpncli_utils.get_country_name(country_code)
            exit_server_info = f'{country} >> {connected_server}'
            self.ids.main_screen.ids.exit_server.text = exit_server_info
            self.ids.main_screen.ids.exit_server.color = [1, 1, 1, 1]

            connected_protocol = pvpncli_utils.get_config_value(
                "metadata",
                "connected_proto",
            )
            self.ids.main_screen.ids.protocol.text = (
                f'OpenVPN ({connected_protocol.upper()})'
            )

            load = pvpncli_utils.get_server_value(
                connected_server,
                "Load",
                servers,
            )
            self.ids.main_screen.ids.exit_server_load.text = f'{load}% Load'

            down = self.ids.main_screen.ids.bitrate_down_arrow
            down.source = './images/bitrate-download-arrow.png'
            up = self.ids.main_screen.ids.bitrate_up_arrow
            up.source = './images/bitrate-upload-arrow.png'

            # Make text visible.
            self.ids.main_screen.ids.data_received.color = [1, 1, 1, 1]
            self.ids.main_screen.ids.data_sent.color = [1, 1, 1, 1]

            # Set connection window button as 'Disconnect'
            self.cnxn_wndw_btn.normal_img = './images/disconnect.png'
            self.cnxn_wndw_btn.hover_img = './images/disconnect_hover.png'
            self.cnxn_wndw_btn.source = './images/disconnect.png'

            # Schedule events
            self.data_trans()
            self.cnxn_time()

        else:
            # VPN isn't connected, so clear the conneciton info on screen.
            self.set_disconnected()

    def set_disconnected(self):
        """VPN isn't connected, so clear the conneciton info on screen."""
        self.last_known_connection = None
        not_protected = '[b]You are not protected![/b]'
        self.ids.main_screen.ids.exit_server.text = not_protected
        self.ids.main_screen.ids.exit_server.color = [1, 0, 0, 1]

        cnxn_window = self.ids.main_screen.ids.connection_window
        cnxn_window.img_source = './images/disconnected_window.png'

        self.ids.main_screen.ids.protocol.text = ''
        self.ids.main_screen.ids.exit_server_load.text = ''

        ip = pvpncli_utils.get_ip_info()[0]
        self.ids.main_screen.ids.exit_server_ip.text = f'IP: {ip}'

        down = self.ids.main_screen.ids.bitrate_down_arrow
        down.source = './images/widget-background-transparent.png'
        up = self.ids.main_screen.ids.bitrate_up_arrow
        up.source = './images/widget-background-transparent.png'

        self.ids.main_screen.ids.data_received.color = [1, 1, 1, 0]
        self.ids.main_screen.ids.data_sent.color = [1, 1, 1, 0]

        # Set connection window button as 'Quick Connect'
        self.cnxn_wndw_btn.normal_img = './images/quick_connect.png'
        self.cnxn_wndw_btn.hover_img = './images/quick_connect_hover.png'
        self.cnxn_wndw_btn.source = './images/quick_connect.png'

    def get_data_up_down(self, dt):
        """Get data transferred during session."""
        tx_amount, rx_amount = pvpncli_utils.get_transferred_data()
        try:
            self.ids.main_screen.ids.data_received.text = rx_amount
            self.ids.main_screen.ids.data_sent.text = tx_amount
        except Exception as e:
            print('Exception from get_data_up_down(): ', e)

    def get_connection_time(self, dt):
        """Get duration of current connection."""
        last_connection = pvpncli_utils.get_config_value(
            "metadata",
            "connected_time",
        )
        if self.vpn_connected:
            connection_time = time() - int(last_connection)
            hours, remainder = divmod(connection_time, 3600)
            mins, secs = divmod(remainder, 60)
            self.ids.main_screen.ids.connection_time.text = (
                '{:02}:{:02}:{:02}'.format(int(hours), int(mins), int(secs))
            )
        else:
            if self.ids.main_screen.ids.connection_time.text != '':
                self.ids.main_screen.ids.connection_time.text = ''

    def open_connecting_notification(self, cnxn):
        """Launch popup while a new connection attempt is in progress."""
        notification = f'Connecting to {cnxn}'
        connecting_notification_popup = ConnectingNotificationPopup(
            label_text=notification
        )
        connecting_notification_popup.open()
        self.close_popup = Clock.schedule_interval(partial(
            self.close_popup_notification,
            connecting_notification_popup,
        ), 0.1)

    def open_disconnecting_notification(self):
        """Launch popup while a disconnection attempt is in progress."""
        if not self.sc_notification_open:
            cnxn = self.last_known_connection
            disconnecting_notification_popup = DisconnectingNotificationPopup(
                label_text=f'Disconnecting from {cnxn}'
            )
            disconnecting_notification_popup.open()
            self.close_popup = Clock.schedule_interval(partial(
                self.close_popup_notification,
                disconnecting_notification_popup,
            ), 0.1)

    def secure_core_notification(self, *dt):
        """Launch popup when Secure Core switch is toggled."""
        if self.vpn_connected:
            if self.secure_core.state == 'down':
                action = 'Switching to'
            else:
                action = 'Disabling'
            notification = (
                f'{action} Secure Core mode will disconnect the active VPN ' +
                'connection.\nDo you want to continue?'
            )
            self.secure_core_notification_popup = SecureCoreNotificationPopup(
                label_text=notification
            )
            self.sc_notification_open = True
            self.secure_core_notification_popup.open()
        else:
            self.open_building_servertree_notification()
            Clock.schedule_once(self.update_server_tree_info, 0.15)

    def update_secure_core_notification_text(self, *dt):
        """Indicate when 'Cancel'/'Continue' updates server tree."""
        self.secure_core_notification_popup.label_text = (
            'Rebuilding Server List...'
        )
        Clock.schedule_once(self.close_sc_notification, 0.1)

    def close_sc_notification(self, *dt):
        """Update server list, disconnect VPN, and dismiss notification."""
        self.update_server_tree_info()
        self.disconnect()
        self.set_sc_notification_close()
        self.secure_core_notification_popup.dismiss()

    def open_building_servertree_notification(self):
        """Launch popup while rebuilding server trees in progress."""
        building_servertree_notification = PvpnPopup(title='Loading')
        building_servertree_notification.size_hint_y = 0.2

        notification = Label()
        notification.text = 'Rebuilding Server List...'
        notification.font_size = '23'
        notification.text_size = self.size
        notification.halign = 'center'
        notification.valign = 'center'

        building_servertree_notification.add_widget(notification)
        building_servertree_notification.open()

        self.close_popup = Clock.schedule_interval(partial(
            self.close_popup_notification,
            building_servertree_notification,
        ), 0.1)

    def close_popup_notification(self, instance, dt):
        """Once connection change detected, close notification popup"""
        if self.connection_changed:
            instance.dismiss()
            self.close_popup.cancel()

    def reset_secure_core_switch(self):
        """Set Secure Core switch to the prior position."""
        if self.secure_core.state == 'down':
            self.secure_core.state = 'normal'
        else:
            self.secure_core.state = 'down'

    def set_sc_notification_close(self):
        self.sc_notification_open = False

    def update_server_tree_info(self, *dt):
        """Remove and replace all server tree nodes with latest data."""
        # Cancel scheduled updates, if event exists:
        if self.update_server_tree:
            self.update_server_tree.cancel()
        # Collect data for building server tree nodes.
        country_dict_list = self.build_country_dict_list()
        country_flag_icons = self.get_flag_icons(country_dict_list)
        servers_by_country = self.get_server_list()
        treeview = self.ids.main_screen.ids.countries_panel.children[0]
        # Gather a list of all nodes.
        all_nodes = []
        for country_node in treeview.iterate_all_nodes():
            all_nodes.append(country_node)
            child_nodes = country_node.nodes
            for child_node in child_nodes:
                all_nodes.append(child_node)
        # Remove all current nodes from server tree.
        for node in all_nodes:
            treeview.remove_node(node)
        # Repoopulate server tree with nodes using the latest data.
        self.populate_server_tree(
            treeview,
            servers_by_country,
            country_flag_icons,
        )
        # Update current connection with new info.
        self.update_current_connection()
        # Reschedule server tree updates.
        self.update_server_tree()

    def build_country_dict_list(self):
        """Build list of country dictionaries."""
        country_dict_list = []
        for code, name in pvpncli_country_codes.country_codes.items():
            country_dict = {}
            country_dict['code'] = code.lower()
            country_dict['name'] = name
            country_dict_list.append(country_dict)
        return country_dict_list

    def get_flag_icons(self, country_dict_list):
        """Assign flag icons based on country code or name."""
        country_dict_list = country_dict_list
        for country in country_dict_list:
            code = country.get('code')
            country['small_flag'] = f'./images/flags/small/{code}_flag.png'
        return country_dict_list

    def get_server_list(self):
        """Build list of servers by Country."""
        # Check for latest data.
        pvpncli_utils.pull_server_data(force=True)
        # Get server details from raw server data.
        servers_data = pvpncli_utils.get_servers()
        # Compile dictionary of countries and server details; key=country name.
        unsorted_countries = {}
        for server in servers_data:
            country = pvpncli_utils.get_country_name(server['ExitCountry'])
            if country not in unsorted_countries.keys():
                unsorted_countries[country] = []

            server_details = {}
            server_name = server['Name']
            server_details[server_name] = {}

            for k, v in server.items():
                server_details[server_name][k] = v

            unsorted_countries[country].append(server_details)

        # Alphabetize countries by country name.
        sorted_countries = sorted(unsorted_countries.keys())

        servers_by_country = {}
        for country in sorted_countries:
            servers_by_country[country] = unsorted_countries[country]

        return servers_by_country

    def populate_server_tree(self, server_tree, servers_by_country,
                             country_flag_icons):
        """Add tree nodes of available servers to the server tree."""
        # Define features and tier levels
        features = {
            # 0: "normal",      # no icon applicable
            1: "secure-core",   # no icon applicable
            2: 'tor-onion',
            4: "p2p-arrows",
        }
        server_tiers = {
            # 0: "F",           # no icon applicable
            # 1: "B",           # no icon applicable
            2: "plus-server",
        }

        # If Secure Core, remove SC countries (CH, SE, & IS). Only exit servers
        # are displayed, not entry servers.
        if self.secure_core.state == 'down':
            sc_countries = ['Iceland', 'Switzerland', 'Sweden']
            for country in sc_countries:
                del servers_by_country[country]

        user_tier = self.tier

        # Create Country node
        for country, servers in servers_by_country.items():
            country_node = self.server_tree.add_node(
                PvpnServerTreeCountryNode(is_open=False),
                None,
            )
            country_node.ids.country_node_country_name.text = country
            # Assign small flag icon for country.
            for country_dict in country_flag_icons:
                if country == country_dict['name']:
                    country_node.ids.country_node_flag_icon.source = country_dict['small_flag'] # noqa
                    continue
            # Add feature icon to country node if any server has the feature
            # If Secure Core selected, skip features:
            if self.secure_core.state == 'normal':
                features_possible = list(features.keys())
                features_possible.remove(1)
                features_found = []
                for server in servers:
                    name = list(server)[0]
                    feature = server[name]['Features']
                    # if feature in features_possible and feature not in features_found: # noqa
                    if feature in features_possible:
                        if feature not in features_found:
                            img = Image(
                                source=f'./images/{features[feature]}.png',
                                size_hint=(0.75, 0.75),
                                pos_hint={'x': 0, 'center_y': 0.5},
                            )
                            country_node.ids.country_node_features_layout.add_widget(img) # noqa
                            features_found.append(feature)

            # For each country, add server node for each server.
            for server in servers:
                # Gather server details.
                name = list(server)[0]
                load = str(server[name]['Load']) + '%'
                server_tier = server[name]['Tier']
                city = server[name]['City']
                feature = server[name]['Features']
                # Only retrieve server info commensurate with user's tier.
                if server_tier <= int(user_tier):
                    # If Secure Core is selected, only populate SC servers.
                    if self.secure_core.state == 'down':
                        if features.get(feature) == 'secure-core':
                            # Add server node to country node.
                            server_node = self.server_tree.add_node(
                                PvpnServerTreeServerNode(),
                                country_node,
                            )
                            # Server name
                            server_node.ids.server_node_server_name.text = name
                            # Add server load
                            server_node.ids.server_node_server_load.text = load
                            # Add server tier
                            tier = './images/plus-server.png'
                            server_node.ids.plus_server.source = tier
                            # Add server features
                            feat = './images/widget-background-transparent.png'
                            server_node.ids.tor_or_p2p.source = feat
                            # Add server city
                            if city:
                                server_node.ids.server_node_server_city.text = city # noqa
                    else:
                        if features.get(feature) != 'secure-core':
                            # Add server node to country node.
                            server_node = self.server_tree.add_node(
                                PvpnServerTreeServerNode(),
                                country_node,
                            )
                            # Add server name
                            server_node.ids.server_node_server_name.text = name
                            # Add server load
                            server_node.ids.server_node_server_load.text = load
                            # Add server tier
                            try:
                                tier = f'./images/{server_tiers[server_tier]}.png' # noqa
                            except KeyError:
                                tier = './images/widget-background-transparent.png' # noqa
                            server_node.ids.plus_server.source = tier
                            # Add server features
                            try:
                                feat = f'./images/{features[feature]}.png'
                            except KeyError:
                                feat = './images/widget-background-transparent.png' # noqa
                            server_node.ids.tor_or_p2p.source = feat
                            # Add server city
                            if city:
                                server_node.ids.server_node_server_city.text = city # noqa

    def build_server_tree(self):
        """Create treeview for server list and add it to scrollviewer."""
        # Cancel scheduled updates, if event exists:
        if self.update_server_tree:
            self.update_server_tree.cancel()
        # Gather data for compiling server tree
        country_dict_list = self.build_country_dict_list()
        country_flag_icons = self.get_flag_icons(country_dict_list)
        servers_by_country = self.get_server_list()

        self.server_tree = PvpnTreeView(
            root_options=dict(text='Servers', is_open=True),
            hide_root=True,
        )
        self.server_tree.size_hint_y = None
        self.server_tree.bind(minimum_height=self.server_tree.setter('height'))
        self.populate_server_tree(
            self.server_tree,
            servers_by_country,
            country_flag_icons,
        )
        self.ids.main_screen.ids.countries_panel.add_widget(self.server_tree)
        # Reschedule server tree updates.
        self.update_server_tree()

    def get_country_code(self, country):
        """Return country code for country name provided."""
        country_codes = pvpncli_country_codes.country_codes
        for code, name in country_codes.items():
            if name == country:
                return code

    def exec_cmd(self, cmd, *dt):
        """Send cmd to command shell."""
        self.cmd = cmd
        try:
            subprocess.check_output(self.cmd, shell=True).decode()
        except subprocess.CalledProcessError as e:
            print('Exception from exec_cmd(): ', e)
            print('check_current_cnxn() called: ', self.check_current_cnxn())

    # TODO
    # def quick_connect(self, trigger, country=None):
    #     """Connect to the configured connection profile in User's settings."""  # noqa
    #     if self.secure_core.state == 'down':
    #         pass

    def connect(self, country=None, server_name=None, protocol=None, random=None, *dt): # noqa
        """Call exec_cmd to connect to vpn, per args provided."""
        country = country
        server_name = server_name
        protocol = self.default_protocol
        # If random is provided, connect to random server.
        if random:
            cmd = f'sudo protonvpn c -r -p {protocol}'
            cnxn = 'a random server'
        # If country provided, connect to fastest server in that country.
        if country:
            if self.secure_core.state == 'down':
                cnxn = f'the fastest Secure Core server in {country}'
                self.open_connecting_notification(cnxn)
                self.fastest_sc_by_country(country)
                return
            else:
                cc = self.get_country_code(country)
                cmd = f'sudo protonvpn connect --cc {cc} -p {protocol}'
                cnxn = f'the fastest server in {country}'
        # If server name provided, connect to that server.
        if server_name:
            cmd = f'sudo protonvpn c {server_name} -p {protocol}'
            cnxn = f'server {server_name}'
        # If neither country or server name provided, connect to fastest server. # noqa
        if not country and not server_name and not random:
            cmd = f'sudo protonvpn c -f -p {protocol}'
            cnxn = 'the fastest server'
        self.open_connecting_notification(cnxn)
        Clock.schedule_once(partial(self.exec_cmd, cmd), 0.1)

    def disconnect(self, *dt):
        """Call exec_cmd to disconnect vpn."""
        cmd = 'sudo protonvpn d'
        self.open_disconnecting_notification()
        self.exec_cmd(cmd)

    def fastest_sc_by_country(self, country, protocol=None):
        """Connect to the fastest Secure Core server in a specific country."""
        pvpncli_logger.logger.debug("Starting fastest SC country connect")

        if not protocol:
            protocol = pvpncli_utils.get_config_value(
                "USER",
                "default_protocol"
            )

        country_code = self.get_country_code(country)

        self.exec_cmd('sudo protonvpn d')
        pvpncli_utils.pull_server_data(force=True)

        servers = pvpncli_utils.get_servers()

        # ProtonVPN Features: 1: SECURE-CORE, 2: TOR, 4: P2P
        server_pool = []
        for server in servers:
            if server["Features"] == 1 \
               and server["ExitCountry"] == country_code:
                server_pool.append(server)

        fastest_server = pvpncli_utils.get_fastest_server(server_pool)
        cmd = f'sudo protonvpn c {fastest_server} -p {protocol}'
        Clock.schedule_once(partial(self.exec_cmd, cmd), 0.1)

    def do_quickconnect_or_disconnect(self, *args):
        if self.vpn_connected:
            self.disconnect()
        else:
            if self.secure_core.state == 'down':
                cmd = 'sudo protonvpn connect --sc'
                cnxn = 'the fastest Secure Core server...'
            else:
                cmd = 'sudo protonvpn connect --fastest'
                cnxn = 'the fastest server...'
            self.open_connecting_notification(cnxn)
            Clock.schedule_once(partial(self.exec_cmd, cmd), 0.1)

    def show_app_window(self):
        """Bring minimized and/or hidden App window to the forefront."""
        self._app_window.show()
        self._app_window.raise_window()

    def minimize_app(self):
        """Minimize App window."""
        self._app_window.minimize()

    def maximize_app(self):
        """Maximize App window."""
        self._app_window.maximize()

    def restore_app(self):
        """Restore App window to pre-maximized size."""
        self._app_window.restore()

    def close_app(self):
        """Close App window."""
        self._app_window.close()

    # def menu_popup(self, *args):
    #     """Define popup dialogues for the hamburger menu."""
    #     self.about_popup = PvpnPopup(
    #         title='about-title',
    #         label_text='about-label-text'
    #     )
    #     self.account_popup = PvpnPopup(
    #         title='account-title',
    #         label_text='account-label-text'
    #     )
    #     self.profiles_popup = PvpnPopup(
    #         title='profiles-title',
    #         label_text='profiles-label-text'
    #     )
    #     self.settings_popup = PvpnPopup(
    #         title='settings-title',
    #         label_text='settings-label-text'
    #     )
    #     self.help_popup = PvpnPopup(
    #         title='help-title',
    #         label_text='help-label-text'
    #     )
    #     self.report_bug_popup = PvpnPopup(
    #         title='report_bug-title',
    #         label_text='report_bug-label-text'
    #     )
    #     self.logout_popup = PvpnPopup(
    #         title='logout-title',
    #         label_text='logout-label-text'
    #     )
    #     self.exit_popup = PvpnPopup(
    #         title='exit-title',
    #         label_text='exit-label-text'
    #     )


class ProtonVpnGuiApp(App):
    """
    The app.

    Instantiate the root class.
    """

    def build(self):
        """Instatiate the App class and return an instance to run."""
        pvpn_gui = ProtonVpnGui()
        return pvpn_gui
