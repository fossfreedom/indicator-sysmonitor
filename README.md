![indicator-sysmonitor](https://user-images.githubusercontent.com/9158844/37069705-90f272a2-21c5-11e8-806f-92b20cbf47ae.png)
![image](https://user-images.githubusercontent.com/41370460/98230824-9cfcfd80-1f81-11eb-9a68-2ac6e1c8adb9.png)


\* _Use following string to use custom preview that is shown above. (Proprietary Nvidia driver needed, must be running)_:

    CPU {cpu}  {cputemp}   |  GPU {nvgpu}  {nvgputemp}  |  MEM {mem}  |  SWAP {swap}  |  Net Speed Compact {netcomp}  |  Total Net Speed {totalnet}

Indicator-SysMonitor - v0.9.0
===================
An Application Indicator showing cpu temperature, memory, network speed, cpu usage, public IP address and internet connection status .

Works with Unity, Xubuntu, Gnome-Shell + app-indicator extension together with any other desktop environments that support AppIndicators.

Also works with the Budgie-Desktop

Offers the possibility to run your own command and display its output.

----

## Custom scripts

Create your own scripts (for example in bash).  Give the script execute permission (chmod +x scriptname)

A script must output one line of text - e.g. using "echo" in bash

The indicator can change the icon being displayed by recognising the output of a sensor "USE_ICON:full_path_to_.svg"

## Set the display order of the indicator

To force the indicator to appear on the left-side of all indicators you must use a override file as described here:

 - http://askubuntu.com/questions/26114/is-it-possible-to-change-the-order-of-icons-in-the-indicator-applet

----

Installation - Budgie-Desktop:

On budgie-desktop based installation  - manual installation

    sudo apt-get install python3-psutil curl git
    git clone https://github.com/fossfreedom/indicator-sysmonitor.git
    cd indicator-sysmonitor
    sudo make installbudgie
    budgie-panel --replace &
    
    Then use Raven to add the "Panel Sys Monitor" applet

Installation - App Indicator based desktops:

On Ubuntu and derivatives - manual installation


    sudo apt-get install python3-psutil curl git gir1.2-appindicator3-0.1
    git clone https://github.com/fossfreedom/indicator-sysmonitor.git
    cd indicator-sysmonitor
    sudo make install
    nohup indicator-sysmonitor &
    
To remove:

    cd indicator-sysmonitor
    sudo make uninstall
        
To install the AppIndicator via PPA:

    sudo add-apt-repository ppa:fossfreedom/indicator-sysmonitor
    sudo apt-get update
    sudo apt-get install indicator-sysmonitor
    
    Search in the dash for "indicator-sysmonitor" to run

To install the Budgie Applet via PPA:

    open budgie-welcome - Install Software - Budgie Applets

Changelog:
 
 - v0.9.0 - NetSpeed Compact and Total NetSpeed, NVidia GPU sensors
 - v0.8.3 - Rework fetch thread, README updates
 - v0.8.2 - fix budgie-desktop crash and release debian package
 - v0.8.1 - development - support budgie-desktop
 - v0.8.0 - development - new sensor - cputemp, ability to use and change icons via a custom script
 - v0.7.1 - bug fix to allow non-ubuntu kernels to be used
 - v0.7.0 - new sensors - publicip and upordown.
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
 
Credits:
 
 - [100](https://github.com/fossfreedom/indicator-sysmonitor/pull/100) prateekmedia
 - [87](https://github.com/fossfreedom/indicator-sysmonitor/pull/87) cosmicog
 - [24](https://github.com/fossfreedom/indicator-sysmonitor/pull/24) & [25](https://github.com/fossfreedom/indicator-sysmonitor/pull/25) SteveGuo <steveguo@outlook.com> https://github.com/SteveGuo
 - [19](https://github.com/fossfreedom/indicator-sysmonitor/pull/19) & [37](https://github.com/fossfreedom/indicator-sysmonitor/pull/37) CPU & meminfo bug fixes Jesse Johnson https://github.com/holocronweaver

----

Original Author: Alex Eftimie <alex@rosedu.org>
https://launchpad.net/indicator-sysmonitor

Current fork maintainer: fossfreedom <foss.freedom@gmail.com>

----
