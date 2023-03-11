This is forked from https://github.com/fossfreedom/indicator-sysmonitor for a private usage.

\* _Use following string to use custom preview that is shown above. (Proprietary Nvidia driver needed, must be running)_:

    {netiso}   |  CPU {cpu}  {cputemp}   |  GPU {nvgpu}  {nvgputemp}  |  MEM {mem}

----

Installation - App Indicator based desktops:

On Ubuntu and derivatives - manual installation

    git clone https://github.com/devkrin/indicator-sysmonitor-enhanced.git
    cd indicator-sysmonitor-enhanced
    sudo make install
    nohup indicator-sysmonitor &
    
To remove:

    cd indicator-sysmonitor-enhanced
    sudo make uninstall

----

Credits:
 
 - [100](https://github.com/fossfreedom/indicator-sysmonitor/pull/100) prateekmedia
 - [87](https://github.com/fossfreedom/indicator-sysmonitor/pull/87) cosmicog
 - [24](https://github.com/fossfreedom/indicator-sysmonitor/pull/24) & [25](https://github.com/fossfreedom/indicator-sysmonitor/pull/25) SteveGuo <steveguo@outlook.com> https://github.com/SteveGuo
 - [19](https://github.com/fossfreedom/indicator-sysmonitor/pull/19) & [37](https://github.com/fossfreedom/indicator-sysmonitor/pull/37) CPU & meminfo bug fixes Jesse Johnson https://github.com/holocronweaver

----

Original Author:
- Alex Eftimie <alex@rosedu.org> https://launchpad.net/indicator-sysmonitor
- fossfreedom <foss.freedom@gmail.com> https://github.com/fossfreedom/indicator-sysmonitor

Current fork maintainer: devkrin <krin-lai@qq.com>

----
