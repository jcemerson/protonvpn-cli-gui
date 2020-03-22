<h1 align="center">ProtonVPN-CLI-GUI</h1>

<p align="center">
  <img src="https://github.com/jcemerson/protonvpn-cli-gui/blob/package/protonvpn_cli_gui/images/protonvpn-wallpaper-7.jpg" alt="ProtonVPN"></img>
</p>

<p align="center">
  <a href="https://github.com/jcemerson/protonvpn-cli-gui/releases/latest">
      <img alt="Build Status" src="https://img.shields.io/github/release/jcemerson/protonvpn-cli-gui.svg?style=flat" />
  </a>
  <a href="https://pepy.tech/project/protonvpn-cli-gui">
    <img alt="Downloads" src="https://pepy.tech/badge/protonvpn-cli-gui">
  </a>
    <a href="https://pepy.tech/project/protonvpn-linux-cli-gui/week">
      <img alt="Downloads per Week" src="https://pepy.tech/badge/protonvpn-cli-gui/week">
    </a>
</p>
<p align="center">
    <a href="https://actions-badge.atrox.dev/jcemerson/protonvpn-cli-gui/goto?ref=master">
        <img alt="Master Branch Build Status" src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%jcemerson%2Fprotonvpn-cli-gui%2Fbadge%3Fref%3Dmaster&style=flat" />
    </a>
    <a href="https://github.com/jcemerson/protonvpn-cli-gui/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/jcemerson/protonvpn-cli-gui">
    </a>
    <a href="https://actions-badge.atrox.dev/jcemerson/protonvpn-cli-gui/goto?ref=testing">
        <img alt="Testing Branch Build Status" src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fjcemerson%2Fprotonvpn-cli-gui%2Fbadge%3Fref%3Dtesting&style=flat" />
    </a>
</p>

<h3 align="center">A GUI for <a href="https://github.com/ProtonVPN/protonvpn-cli-ng"><b>ProtonVPN-CLI</b></a> on Linux *(Unofficial)*, written entirely in Python.</h3>

ProtonVPN-CLI-GUI is <a href="https://github.com/kivy/kivy"><b>Kivy</b></a>-based GUI built on top of <a href="https://github.com/ProtonVPN/protonvpn-cli-ng"><b>protonvpn-cli-ng</b></a> as the back-end. Wherever possible, the GUI relies on the actual code of the CLI, so ProtonVPN-CLI-GUI will remain up to date with <a href="https://github.com/ProtonVPN/protonvpn-cli-ng"><b>ProtonVPN-CLI</b></a>.



### Installing Dependencies

**Dependencies:**

- <a href="https://github.com/kivy/kivy"><b>Kivy</b></a>
- <a href="https://github.com/OpenVPN/openvpn"><b>OpenVPN</b></a>
- <a href="https://github.com/pypa/pip"><b>pip for Python3 (pip3)</b></a>
- <a href="https://github.com/ProtonVPN/protonvpn-cli-ng"><b>ProtonVPN-CLI</b></a>
- <a href="https://www.python.org/"><b>Python3.6+</b></a>
- <a href="https://pypi.org/project/setuptools/"><b>setuptools for python3 (python3-setuptools)</b></a>

To install <a href="https://github.com/ProtonVPN/protonvpn-cli-ng"><b>ProtonVPN-CLI</b></a>, depending on your distribution, run the appropriate following command to install the necessary dependencies.
For more detailed information on installing, updating and uninstalling, please view the extensive [usage guide](https://github.com/ProtonVPN/protonvpn-cli-ng/blob/master/USAGE.md#installation--updating):

| **Distro**                              | **Command**                                                        |
|:----------------------------------------|:------------------------------------------------                   |
|Fedora/CentOS/RHEL                       | `sudo dnf install -y openvpn dialog python3-pip python3-setuptools`|
|Ubuntu/Linux Mint/Debian and derivatives | `sudo apt install -y openvpn dialog python3-pip python3-setuptools`|
|OpenSUSE/SLES                            | `sudo zypper in -y openvpn dialog python3-pip python3-setuptools`  |
|Arch Linux/Manjaro                       | `sudo pacman -S openvpn dialog python-pip python-setuptools`       |

*Note: This has only been tested on Linux Mint 19.3 Cinnamon.*


Once you've installed <a href="https://github.com/ProtonVPN/protonvpn-cli-ng"><b>protonvpn-cli-ng</b></a>, install <b>ProtonVPN-CLI-GUI</b>.



## Installing ProtonVPN-CLI-GUI

You can either install via <b>PIP</b> (simple) or by cloning this repository (must manually manage dependencies, etc).

*Note: Make sure to run pip with sudo*

`sudo pip3 install protonvpn-cli-gui`



### To update to a new version

`sudo pip3 install protonvpn-cli-gui --upgrade`



## Manual Installation

1. Clone this repository:

    `git clone https://github.com/jcemerson/protonvpn-cli-gui`

2. Navigate to the directory:

   `cd {/path/to/directory/}protonvpn-cli-gui`

3. Install:

    `sudo python3 setup.py install`



### How to use

 `sudo protonvpn-cli-gui`


### Recommendation for Convenience:
For passwordless execution without using a terminal, such as by automated script or .desktop file, <a href="https://www.linux.com/training-tutorials/configuring-linux-sudoers-file/"><b>update your sudoers file</b></a> by using `sudo visudo` and paste the following at the bottom (last line) of your file:

`{your_linux_username} ALL = (root) NOPASSWD: /usr/local/bin/protonvpn-cli-gui`

*Note: The path to your bin might be different. To find, use* `which protonvpn-cli-gui`



## Create .desktop file

To create a desktop application launcher using a .desktop file:

1. Create a new file in `.local/share/applications/` named `protonvpn-cli-gui.desktop` with the following contents:

    ```
    [Desktop Entry]
    Name=ProtonVPN-CLI-GUI
    GenericName=ProtonVPN-CLI-GUI
    Exec=sudo protonvpn-cli-gui
    Icon={path/to/icon}
    Type=Application
    Terminal=False
    Categories=Network;VPN
    ```
    *Note: Be sure to update the Icon with your own path to an image file.*



### This is a pre-release and not all planned features have been implemented.

Some remaining features include:

- Logging (GUI-only. Kivy, OpenVPN, and ProtonVPN-CLI all have logs of their own.)
- Searchable Server List
- Start on Boot
- Connection Profiles (user-configurable connection profiles that can be saved, e.g. "Fastest TOR server with TCP connection", "Fastest P2P server in Iceland", etc.).
- Built-in Connection Speed Test
- System Tray icon with connection status notification



## Screenshots
