#!/usr/bin/python3
# coding: utf-8
#
# A simple indicator applet displaying cpu and memory information
#
# Author: Alex Eftimie <alex@eftimie.ro>
# Fork Author: fossfreedom <foss.freedom@gmail.com>
# Original Homepage: http://launchpad.net/indicator-sysmonitor
# Fork Homepage: https://github.com/fossfreedom/indicator-sysmonitor
# License: GPL v3

import json
import time
from threading import Thread
from threading import Event
import subprocess
import copy
import logging
import re
import os
import platform
from gettext import gettext as _
from gi.repository import GLib

import psutil as ps

ps_v1_api = int(ps.__version__.split('.')[0]) <= 1


B_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
cpu_load = []


def bytes_to_human(num):
    for unit in B_UNITS:
        if abs(num) < 1000.0:
            return "%3.2f %s" % (num, unit)
        num /= 1000.0
    return "%.2f %s" % (num, 'YB')

class ISMError(Exception):
    """General exception."""

    def __init__(self, msg):
        Exception.__init__(self, msg)


class SensorManager(object):
    """Singleton"""
    _instance = None

    SETTINGS_FILE = os.getenv("HOME") + '/.indicator-sysmonitor.json'
    digit_regex = re.compile(r'''\d+''')

    class __impl:

        settings = {
            'custom_text': 'cpu: {cpu} mem: {mem}',
            'interval': 2,
            'on_startup': False,
            'sensors': {
                # 'name' => (desc, cmd)
            }
        }

        supported_sensors = None

        def __init__(self):
            self.sensor_instances = [CPUSensor(),
                                     NvGPUSensor(),
                                     MemSensor(),
                                     NetSensor(),
                                     NetCompSensor(),
                                     TotalNetSensor(),
                                     BatSensor(),
                                     FSSensor(),
                                     SwapSensor(),
                                     UporDownSensor(),
                                     PublicIPSensor(),
                                     CPUTemp(),
                                     NvGPUTemp()]

            for sensor in self.sensor_instances:
                self.settings['sensors'][sensor.name] = (sensor.desc, sensor.cmd)

            self._last_net_usage = [0, 0]  # (up, down)
            self._fetcher = None

        # @staticmethod
        @classmethod
        def update_regex(self, names=None):
            if names is None:
                names = list(self.settings["sensors"].keys())

            reg = '|'.join(names)
            reg = "\A({})\Z".format(reg)
            # global supported_sensors
            self.supported_sensors = re.compile("{}".format(reg))

        def get(self, name):
            """
            :param name: of the sensor
            :return: the sensor instance
            """

            for sensor in self.sensor_instances:
                if sensor.check(name) is not None:
                    return sensor

            return None

        # @staticmethod
        def exists(self, name):
            """Checks if the sensor name exists"""
            return bool(self.supported_sensors.match(name))

        # @staticmethod
        def check(self, sensor_string):
            for sensor in self.sensor_instances:
                sensor.check(sensor_string)

        def add(self, name, desc, cmd):
            """Adds a custom sensors."""
            if self.exists(name):
                raise ISMError(_("Sensor name already in use."))

            self.settings["sensors"][name] = (desc, cmd)
            self.update_regex()

        def delete(self, name):
            """Deletes a custom sensors."""
            sensors = self.settings['sensors']
            names = list(sensors.keys())
            if name not in names:
                raise ISMError(_("Sensor is not defined."))

            _desc, default = sensors[name]
            if default is True:
                raise ISMError(_("Can not delete default sensors."))

            del sensors[name]
            self.update_regex()

        def edit(self, name, newname, desc, cmd):
            """Edits a custom sensors."""
            try:
                sensors = self.settings['sensors']
                _desc, default = sensors[name]

            except KeyError:
                raise ISMError(_("Sensor does not exists."))

            if default is True:
                raise ISMError(_("Can not edit default sensors."))
            if newname != name:
                if newname in list(sensors.keys()):
                    raise ISMError(_("Sensor name already in use."))

            sensors[newname] = (desc, cmd)
            del sensors[name]
            self.settings["custom_text"] = self.settings["custom_text"].replace(
                name, newname)
            self.update_regex()

        def load_settings(self):
            """It gets the settings from the config file and
            sets them to the correct vars"""
            try:
                with open(SensorManager.SETTINGS_FILE, 'r') as f:
                    cfg = json.load(f)

                if cfg['custom_text'] is not None:
                    self.settings['custom_text'] = cfg['custom_text']
                if cfg['interval'] is not None:
                    self.settings['interval'] = cfg['interval']
                if cfg['on_startup'] is not None:
                    self.settings['on_startup'] = cfg['on_startup']
                if cfg['sensors'] is not None:
                    # need to merge our current list of sensors with what was previously saved
                    newcopy = self.settings['sensors']
                    newcopy.update(cfg['sensors'])
                    self.settings['sensors'] = newcopy

                self.update_regex()

            except Exception as ex:
                logging.exception(ex)
                logging.error('Reading settings failed')

        def save_settings(self):
            """It stores the current settings to the config file."""
            # TODO: use gsettings
            try:
                with open(SensorManager.SETTINGS_FILE, 'w') as f:
                    f.write(json.dumps(self.settings))

            except Exception as ex:
                logging.exception(ex)
                logging.error('Writing settings failed')

        def get_guide(self):
            """Updates the label guide from appindicator."""

            # foss - I'm doubtful any of this guide stuff works - this needs to be recoded
            # each sensor needs a sensor guide
            data = self._fetcher.fetch()

            for key in data:
                if key.startswith('fs'):
                    data[key] = '000gB'
                    break

            data['mem'] = data['cpu'] = data['bat'] = '000%'
            data['net'] = '↓666kB/s ↑666kB/s'

            self.settings['custom_text'].format(**data)
            return self.settings['custom_text'].format(**data)

        def get_label(self, data):
            """It updates the appindicator text with the the values
            from data"""
            try:
                label = self.settings["custom_text"].format(**data) if len(data) \
                    else _("(no output)")

            except KeyError as ex:
                label = _("Invalid Sensor: {}").format(ex)
            except Exception as ex:
                logging.exception(ex)
                label = _("Unknown error: ").format(ex)

            return label

        def initiate_fetcher(self, parent):
            if self._fetcher is not None:
                self._fetcher.stop()
            self._fetcher = StatusFetcher(parent)
            self._fetcher.start()
            logging.info("Fetcher started")

        def fill_liststore(self, list_store):

            sensors = self.settings['sensors']
            for name in list(sensors.keys()):
                list_store.append([name, sensors[name][0]])

        def get_command(self, name):
            cmd = self.settings["sensors"][name][1]

            return cmd

        def set_custom_text(self, custom_text):
            self.settings["custom_text"] = custom_text

        def get_custom_text(self):
            return self.settings["custom_text"]

        def set_interval(self, interval):
            self.settings["interval"] = interval

        def get_interval(self):
            return self.settings["interval"]

        def get_results(self):
            """Return a dict whose element are the sensors
            and their values"""
            res = {}
            from preferences import Preferences

            # We call this only once per update
            global cpu_load
            cpu_load = ps.cpu_percent(interval=0, percpu=True)

            # print (self.settings["custom_text"]) custom_text is the full visible string seen in Preferences edit field
            for sensor in Preferences.sensors_regex.findall(
                    self.settings["custom_text"]):

                sensor = sensor[1:-1]
                instance = self.get(sensor)

                if instance:
                    value = instance.get_value(sensor)
                    if value:
                        res[sensor] = value

                else:  # custom sensor
                    res[sensor] = BaseSensor.script_exec(self.settings["sensors"][sensor][1])

            return res

    def __init__(self):

        if SensorManager._instance is None:
            SensorManager._instance = SensorManager.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_SensorManager__instance'] = SensorManager._instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)


class BaseSensor(object):
    name = ''
    desc = ''
    cmd = True

    def check(self, sensor):
        '''
        checks to see if the sensor string passed in valid
        :param sensor: string representation of the sensor
        :return: True if the sensor is understood and passes the check or
          an Exception if the format of the sensor string is wrong
          None is returned if the sensor string is nothing to-do with the Sensor name
        '''
        if sensor == self.name:
            return True

    def get_value(self, sensor_data):
        return None

    @staticmethod
    def script_exec(command):
        """Execute a custom command."""
        try:
            output = subprocess.Popen(command, stdout=subprocess.PIPE,
                                      shell=True).communicate()[0].strip()
        except:
            output = _("Error")
            logging.error(_("Error running: {}").format(command))

        return output.decode('utf-8') if output else _("(no output)")


class NvGPUSensor(BaseSensor):
    name = 'nvgpu'
    desc = _('Nvidia GPU utilization')

    def get_value(self, sensor):
        if sensor == 'nvgpu':
            return "{:02.0f}%".format(self._fetch_gpu())

    def _fetch_gpu(self, percpu=False):
        result = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv'])
        perc = result.splitlines()[1]
        perc = perc[:-2]
        return int(perc)


class NvGPUTemp(BaseSensor):
    """Return GPU temperature expressed in Celsius
    """
    name = 'nvgputemp'
    desc = _('Nvidia GPU Temperature')

    def get_value(self, sensor):
        # degrees symbol is unicode U+00B0
        return "{}\u00B0C".format(self._fetch_gputemp())

    def _fetch_gputemp(self):
        result = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv'])
        perc = result.splitlines()[1]
        return int(perc)


class CPUSensor(BaseSensor):
    name = 'cpu\d*'
    desc = _('Average CPU usage')
    cpus = re.compile("\Acpu\d*\Z")
    last = None
    if ps_v1_api:
        cpu_count = ps.NUM_CPUS
    else:
        cpu_count = ps.cpu_count()

    def check(self, sensor):
        if self.cpus.match(sensor):
            if len(sensor) == 3:
                nber = 0
            else:
                nber = int(sensor[3:]) if len(sensor) > 3 else 999

            if nber >= self.cpu_count:
                print(sensor)
                print(self.cpu_count)
                print(len(sensor))
                raise ISMError(_("Invalid number of CPUs."))

            return True

    def get_value(self, sensor):
        if sensor == 'cpu':
            return "{:02.0f}%".format(self._fetch_cpu())
        elif CPUSensor.cpus.match(sensor):
            cpus = self._fetch_cpu(percpu=True)
            return "{:02.0f}%".format(cpus[int(sensor[3:])])

        return None

    def _fetch_cpu(self, percpu=False):
        if percpu:
            return cpu_load

        r = 0.0
        for i in cpu_load:
            r += i

        r /= self.cpu_count

        return r


class MemSensor(BaseSensor):
    name = 'mem'
    desc = _('Physical memory in use.')

    def get_value(self, sensor_data):
        return '{:02.0f}%'.format(self._fetch_mem())

    def _fetch_mem(self):
        """It gets the total memory info and return the used in percent."""

        def grep(pattern, word_list):
            expr = re.compile(pattern)
            arr = [elem for elem in word_list if expr.match(elem)]
            return arr[0]

        with open('/proc/meminfo') as meminfofile:
            meminfo = meminfofile.readlines()

        total = SensorManager.digit_regex.findall(grep("MemTotal", meminfo))[0]
        release = re.split('\.', platform.release())
        major_version = int(release[0])
        minor_version = int(re.search(r'\d+', release[1]).group())
        if (minor_version >= 16 and major_version == 3) or (major_version > 3):
            available = SensorManager.digit_regex.findall(
                grep("MemAvailable", meminfo))[0]
            return 100 - 100 * int(available) / float(total)
        else:
            free = SensorManager.digit_regex.findall(
                grep("MemFree", meminfo))[0]
            cached = SensorManager.digit_regex.findall(
                grep("Cached", meminfo))[0]
            free = int(free) + int(cached)
            return 100 - 100 * free / float(total)


class NetSensor(BaseSensor):
    name = 'net'
    desc = _('Network activity.')
    _last_net_usage = [0, 0]  # (up, down)

    def get_value(self, sensor_data):
        return self._fetch_net()

    def _fetch_net(self):
        """It returns the bytes sent and received in bytes/second"""
        current = [0, 0]
        for _, iostat in list(ps.net_io_counters(pernic=True).items()):
            current[0] += iostat.bytes_recv
            current[1] += iostat.bytes_sent
        dummy = copy.deepcopy(current)

        current[0] -= self._last_net_usage[0]
        current[1] -= self._last_net_usage[1]
        self._last_net_usage = dummy
        mgr = SensorManager()
        current[0] /= mgr.get_interval()
        current[1] /= mgr.get_interval()
        return '↓ {:>9s}/s ↑ {:>9s}/s'.format(bytes_to_human(current[0]), bytes_to_human(current[1]))

class NetCompSensor(BaseSensor):
    name = 'netcomp'
    desc = _('Network activity in Compact form.')
    _last_net_usage = [0, 0]  # (up, down)

    def get_value(self, sensor_data):
        return self._fetch_net()

    def _fetch_net(self):
        """It returns the bytes sent and received in bytes/second"""
        current = [0, 0]
        for _, iostat in list(ps.net_io_counters(pernic=True).items()):
            current[0] += iostat.bytes_recv
            current[1] += iostat.bytes_sent
        dummy = copy.deepcopy(current)

        current[0] -= self._last_net_usage[0]
        current[1] -= self._last_net_usage[1]
        self._last_net_usage = dummy
        mgr = SensorManager()
        current[0] /= mgr.get_interval()
        current[1] /= mgr.get_interval()
        return '⇵ {:>9s}/s'.format(bytes_to_human(current[0] + current[1]))

class TotalNetSensor(BaseSensor):
    name = 'totalnet'
    desc = _('Total Network activity.')

    def get_value(self, sensor_data):
        return self._fetch_net()

    def _fetch_net(self):
        """It returns total number the bytes sent and received"""
        current = [0, 0]
        for _, iostat in list(ps.net_io_counters(pernic=True).items()):
            current[0] += iostat.bytes_recv
            current[1] += iostat.bytes_sent

        mgr = SensorManager()
        current[0] /= mgr.get_interval()
        current[1] /= mgr.get_interval()
        return ' Σ {:>9s}'.format(bytes_to_human(current[0] + current[1]))

class BatSensor(BaseSensor):
    name = 'bat\d*'
    desc = _('Battery capacity.')
    bat = re.compile("\Abat\d*\Z")

    def check(self, sensor):
        if self.bat.match(sensor):
            bat_id = int(sensor[3:]) if len(sensor) > 3 else 0
            if not os.path.exists("/sys/class/power_supply/BAT{}".format(bat_id)):
                raise ISMError(_("Invalid number returned for the Battery sensor."))

            return True

    def get_value(self, sensor):
        if BatSensor.bat.match(sensor):
            bat_id = int(sensor[3:]) if len(sensor) > 3 else 0
            return '{:02.0f}%'.format(self._fetch_bat(bat_id))

        return None

    def _fetch_bat(self, batid):
        """Fetch the the amount of remaining battery"""
        capacity = 0
        try:
            with open("/sys/class/power_supply/BAT{}/capacity".format(batid)) as state:
                while True:
                    capacity = int(state.readline())
                    break

        except IOError:
            return "N/A"

        return capacity


class FSSensor(BaseSensor):
    name = 'fs//.+'
    desc = _('Available space in file system.')

    def check(self, sensor):
        if sensor.startswith("fs//"):
            path = sensor.split("//")[1]
            if not os.path.exists(path):
                raise ISMError(_("Path: {} doesn't exists.").format(path))

            return True

    def get_value(self, sensor):
        if sensor.startswith('fs//'):
            parts = sensor.split('//')
            return self._fetch_fs(parts[1])

        return None

    def _fetch_fs(self, mount_point):
        """It returns the amount of bytes available in the fs in
        a human-readble format."""
        if not os.access(mount_point, os.F_OK):
            return None

        stat = os.statvfs(mount_point)
        bytes_ = stat.f_bavail * stat.f_frsize

        for unit in B_UNITS:
            if bytes_ < 1024:
                return "{} {}".format(round(bytes_, 2), unit)
            bytes_ /= 1024


class SwapSensor(BaseSensor):
    name = 'swap'
    desc = _("Average swap usage")

    def get_value(self, sensor):
        return '{:02.0f}%'.format(self._fetch_swap())

    def _fetch_swap(self):
        """Return the swap usage in percent"""
        usage = 0
        total = 0
        try:
            with open("/proc/swaps") as swaps:
                swaps.readline()
                for line in swaps.readlines():
                    dummy, dummy, total_, usage_, dummy = line.split()
                    total += int(total_)
                    usage += int(usage_)

                if total == 0:
                    return 0
                else:
                    return usage * 100 / total

        except IOError:
            return "N/A"


class UporDownSensor(BaseSensor):
    name = 'upordown'
    desc = _("Display if your internet connection is up or down")

    command = 'if wget -qO /dev/null google.com > /dev/null; then echo "☺"; else echo "☹"; fi'

    current_val = ""
    lasttime = 0  # we refresh this every 10 seconds

    def get_value(self, sensor):
        if self.current_val == "" or self.lasttime == 0 or (time.time() - self.lasttime) > 10:
            self.current_val = self.script_exec(self.command)
            self.lasttime = time.time()

        return self.current_val


class PublicIPSensor(BaseSensor):
    name = 'publicip'
    desc = _("Display your public IP address")

    command = 'curl ipv4.icanhazip.com'

    current_ip = ""
    lasttime = 0  # we refresh this every 10 minutes

    def get_value(self, sensor):
        if self.current_ip == "" or self.lasttime == 0 or (time.time() - self.lasttime) > 600:
            self.current_ip = self.script_exec(self.command)
            self.lasttime = time.time()

        return self.current_ip


class CPUTemp(BaseSensor):
    """Return CPU temperature expressed in Celsius
    """

    name = 'cputemp'
    desc = _('CPU temperature')

    def get_value(self, sensor):
        # degrees symbol is unicode U+00B0
        return "{:02.0f}\u00B0C".format(self._fetch_cputemp())

    def _fetch_cputemp(self):
        # http://www.mjmwired.net/kernel/Documentation/hwmon/sysfs-interface

        # first try the following sys file
        # /sys/class/thermal/thermal_zone0/temp

        # if that fails try various hwmon files

        cat = lambda file: open(file, 'r').read().strip()
        ret = None

        zone = "/sys/class/thermal/thermal_zone0/"
        try:
            ret = int(cat(os.path.join(zone, 'temp'))) / 1000
        except:
            pass

        if ret:
            return ret

        base = '/sys/class/hwmon/'
        ls = sorted(os.listdir(base))
        assert ls, "%r is empty" % base
        for hwmon in ls:
            hwmon = os.path.join(base, hwmon)

            try:
                ret = int(cat(os.path.join(hwmon, 'temp1_input'))) / 1000
                break
            except:
                pass

                # if fahrenheit:
                #    digits = [(x * 1.8) + 32 for x in digits]

        return ret


class StatusFetcher(Thread):
    """It recollects the info about the sensors."""

    def __init__(self, parent):
        Thread.__init__(self)
        self._parent = parent
        self.mgr = SensorManager()
        self.alive = Event()
        self.alive.set()
        GLib.timeout_add_seconds(self.mgr.get_interval(), self.run)

    def fetch(self):
        return self.mgr.get_results()

    def stop(self):
        self.alive.clear()

    def run(self):
        data = self.fetch()
        self._parent.update(data)
        if self.alive.isSet():
            return True
