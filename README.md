Indicator-SysMonitor
===================
A basic Application Indicator showing memory and cpu usage.

Show cpu and memory usage and also various temperature sensors in the topbar; works with gnome-panel and Unity.

Also offers the possibility to run your own command and display its output.

Original Author: Alex Eftimie <alex@rosedu.org>
https://launchpad.net/indicator-sysmonitor

Current fork maintainer: fossfreedom <foss.freedom@gmail.com>

----

Installation

on Ubuntu and derivatives

    sudo apt-get install python-psutil git
    git clone https://github.com/fossfreedom/indicator-sysmonitor.git
    cd indicator-sysmonitor
    nohup indicator-sysmonitor &

Changelog

 - v0.5 - in development - GTK3 based
 - v0.4.6 - bug fixes for battery indicator and for spurious overwrite when adding new sensor
 - v0.4.5 - removed indicator icon since not needed
 - v0.4.4 - fix dependencies and corrected shown indicator icon
 - v0.4.3 - fork from original author
