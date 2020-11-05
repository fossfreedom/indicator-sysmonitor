#!/usr/bin/python3
# coding: utf-8
#
# A simple indicator applet displaying cpu and memory information
# for the budgie-desktop
#
# Author: fossfreedom <foss.freedom@gmail.com>
# Original Homepage: http://launchpad.net/indicator-sysmonitor
# Homepage: https://github.com/fossfreedom/indicator-sysmonitor
# License: GPL v3
#
from gettext import gettext as _
from gettext import textdomain, bindtextdomain
import gi
gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, GLib
import sys
import os
import logging
import tempfile
from threading import Event

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from preferences import Preferences
from preferences import VERSION
from sensors import SensorManager

logging.basicConfig(level=logging.INFO)

HELP_MSG = """<span underline="single" size="x-large">{title}</span>

{introduction}

{basic}
• cpu: {cpu_desc}
• mem: {mem_desc}
• bat<i>%d</i>: {bat_desc}
• net: {net_desc}
• netcomp: {netcomp_desc}
• totalnet: {totalnet_desc}
• upordown: {upordown_desc}
• publicip: {publicip_desc}

{compose}
• fs//<i>mount-point</i> : {fs_desc}

<big>{example}</big>
CPU {{cpu}} | MEM {{mem}} | root {{fs///}}
""".format(
    title=_("Help Page"),
    introduction=_("The sensors are the names of the devices you want to \
    retrieve information from. They must be placed between brackets."),
    basic=_("The basics are:"),
    cpu_desc=_("It shows the average of CPU usage."),
    mem_desc=_("It shows the physical memory in use."),
    bat_desc=_("It shows the available battery which id is %d."),
    net_desc=_("It shows the amount of data you are downloading and uploading \
    through your network."),
    netcomp_desc=_("It shows the amount of data you are downloading and uploading \
    through your network in a compact way."),
    totalnet_desc=("It shows the total amount of data you downloaded and uploaded \
    through your network."),
    upordown_desc=_("It shows whether your internet connection is up or down \
     - the sensor is refreshed every 10 seconds."),
    publicip_desc=_("It shows your public IP address \
     - the sensor is refreshed every 10 minutes."),
    compose=_("Also there are the following sensors that are composed with \
    two parts divided by two slashes."),
    fs_desc=_("Show available space in the file system."),
    example=_("Example:"))


class IndicatorSysmonitor(object):
    SENSORS_DISABLED = False

    def __init__(self):
        self._preferences_dialog = None
        self._help_dialog = None

        self.ind = Gtk.Button.new()
        self.ind.set_label("Init...")

        self._create_menu()

        self.alive = Event()
        self.alive.set()

        self.sensor_mgr = SensorManager()
        self.load_settings()

    def _create_menu(self):
        """Creates the main menu and shows it."""
        # create menu {{{
        menu = Gtk.Menu()
        # add System Monitor menu item
        full_sysmon = Gtk.MenuItem(_('System Monitor'))
        full_sysmon.connect('activate', self.on_full_sysmon_activated)
        menu.add(full_sysmon)
        menu.add(Gtk.SeparatorMenuItem())

        # add preferences menu item
        pref_menu = Gtk.MenuItem(_('Preferences'))
        pref_menu.connect('activate', self.on_preferences_activated)
        menu.add(pref_menu)

        # add help menu item
        help_menu = Gtk.MenuItem(_('Help'))
        help_menu.connect('activate', self._on_help)
        menu.add(help_menu)

        menu.show_all()

        self.popup = menu
        self.ind.connect('clicked', self.popup_menu)
        logging.info("Menu shown")
        # }}} menu done!

    def popup_menu(self, *args):
        self.popup.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def update_indicator_guide(self):

        guide = self.sensor_mgr.get_guide()

    def update(self, data):
        # data is the dict of all sensors and their values
        # { name, label }

        # look through data and find out if there are any icons to be set
        for sensor in data:
            test_str = data[sensor].lower()
            if "use_icon" in test_str:
                path = data[sensor].split(":")[1]
                print(path)
                self.ind.set_icon_full(path, "")
                # now strip the icon output from data so that it is not displayed
                remaining = test_str.split("use_icon")[0].strip()
                if not remaining:
                    remaining = " "

                data[sensor] = remaining

            if "clear_icon" in test_str:
                self.ind.set_icon_full(self.tindicator, "")

                remaining = test_str.split("clear_icon")[0].strip()
                if not remaining:
                    remaining = " "

                data[sensor] = remaining

        label = self.sensor_mgr.get_label(data)


        def update_label(label):
            self.ind.set_label(label)
            return False
        if label and self.ind:
            GLib.idle_add(update_label, label.strip())

    def load_settings(self):

        self.sensor_mgr.load_settings()
        self.sensor_mgr.initiate_fetcher(self)
        self.update_indicator_guide()

    # @staticmethod
    def save_settings(self):
        self.sensor_mgr.save_settings()

    def update_settings(self):
        self.sensor_mgr.initiate_fetcher(self)

    # actions raised from menu
    def on_preferences_activated(self, event=None):
        """Raises the preferences dialog. If it's already open, it's
        focused"""
        if self._preferences_dialog is not None:
            self._preferences_dialog.present()
            return

        self._preferences_dialog = Preferences(self)
        self._preferences_dialog.run()
        self._preferences_dialog = None

    def on_full_sysmon_activated(self, event=None):
        os.system('gnome-system-monitor &')

    def on_exit(self, event=None, data=None):
        """Action call when the main programs is closed."""
        # cleanup temporary indicator icon
        os.remove(self.tindicator)
        # close the open dialogs
        if self._help_dialog is not None:
            self._help_dialog.destroy()

        if self._preferences_dialog is not None:
            self._preferences_dialog.destroy()

        logging.info("Terminated")
        self.alive.clear()  # DM: why bother with Event() ???

        try:
            Gtk.main_quit()
        except RuntimeError:
            pass

    def _on_help(self, event=None, data=None):
        """Raise a dialog with info about the app."""
        if self._help_dialog is not None:
            self._help_dialog.present()
            return

        self._help_dialog = Gtk.MessageDialog(
            None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, None)

        self._help_dialog.set_title(_("Help"))
        self._help_dialog.set_markup(HELP_MSG)
        self._help_dialog.run()
        self._help_dialog.destroy()
        self._help_dialog = None

class BudgieSysMonitor(GObject.Object, Budgie.Plugin):
    """ This is simply an entry point into the SysMonitor applet
        Note you must always override Object, and implement Plugin.
    """

    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "BudgieSysMonitor"

    def __init__(self):
        """ Initialisation is important.
        """
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):
        """ This is where the real fun happens. Return a new Budgie.Applet
            instance with the given UUID. The UUID is determined by the
            BudgiePanelManager, and is used for lifetime tracking.
        """
        return BudgieSysMonitorApplet(uuid)

class BudgieSysMonitorApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """

    button = None

    def __init__(self, uuid):
        Budgie.Applet.__init__(self)

        # Add a button to our UI
        logging.info("start")

        if not os.path.exists(SensorManager.SETTINGS_FILE):
            sensor_mgr = SensorManager()
            sensor_mgr.save_settings()

        self.app = IndicatorSysmonitor()
        self.button = self.app.ind
        self.button.set_relief(Gtk.ReliefStyle.NONE)
        self.add(self.button)
        self.show_all()
