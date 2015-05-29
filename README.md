Indicator-SysMonitor
===================
A basic Application Indicator showing memory and cpu usage.

Show cpu and memory usage and also various temperature sensors in the topbar; works with gnome-panel and Unity.

Also offers the possibility to run your own command and display its output.

Original Author: Alex Eftimie <alex@rosedu.org>
https://launchpad.net/indicator-sysmonitor

Current fork maintainer: fossfreedom <foss.freedom@gmail.com>

v0.6.3: SteveGuo <steveguo@outlook.com>
https://github.com/SteveGuo

----

Installation - v0.6.3 stable

on Ubuntu and derivatives - manual installation


    sudo apt-get install python3-psutil git
    git clone https://github.com/fossfreedom/indicator-sysmonitor.git
    cd indicator-sysmonitor
    sudo make install
    nohup indicator-sysmonitor &
    
To remove:

    cd indicator-sysmonitor
    sudo make uninstall
        
To install via PPA:

    sudo add-apt-repository ppa:fossfreedom/indicator-sysmonitor
    sudo apt-get update
    sudo apt-get install indicator-sysmonitor
    
    Search in the dash for "indicator-sysmonitor" to run

Changelog
 
 - v0.6.3 - fixed the bug when display multiple CPU cores it always display the later ones as 0%
 - v0.6.2 - bug fix to stop crash for custom sensors
 - v0.6.1 - fix the debian packaging
 - v0.6 - stable release - reworked to be easier to maintain
 - v0.5 - GTK3 & Python3 based including bug-fix to display errors on using Test button
     together with fixing crash reports when incorrect sensor values used
 - v0.4.6 - bug fixes for battery indicator and for spurious overwrite when adding new sensor
 - v0.4.5 - removed indicator icon since not needed
 - v0.4.4 - fix dependencies and corrected shown indicator icon
 - v0.4.3 - fork from original author
