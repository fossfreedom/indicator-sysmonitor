PREFIX=/usr
BUDGIELIB=lib/budgie-desktop/plugins/budgiesysmonitor

all:

install:
	mkdir -p "$(DESTDIR)$(PREFIX)/lib/indicator-sysmonitor"
	cp indicator-sysmonitor "$(DESTDIR)$(PREFIX)/lib/indicator-sysmonitor"
	cp preferences.py "$(DESTDIR)$(PREFIX)/lib/indicator-sysmonitor"
	cp sensors.py "$(DESTDIR)$(PREFIX)/lib/indicator-sysmonitor"
	cp preferences.ui "$(DESTDIR)$(PREFIX)/lib/indicator-sysmonitor"
	mkdir -p "$(DESTDIR)$(PREFIX)/bin/"
	ln -s ../lib/indicator-sysmonitor/indicator-sysmonitor "$(DESTDIR)$(PREFIX)/bin/indicator-sysmonitor"
	mkdir -p "$(DESTDIR)$(PREFIX)/share/applications"
	cp indicator-sysmonitor.desktop "$(DESTDIR)$(PREFIX)/share/applications/"
	
installbudgie:
	mkdir -p "$(DESTDIR)$(PREFIX)/$(BUDGIELIB)"
	cp budgiesysmonitor.py "$(DESTDIR)$(PREFIX)/$(BUDGIELIB)"
	cp preferences.py "$(DESTDIR)$(PREFIX)/$(BUDGIELIB)"
	cp sensors.py "$(DESTDIR)$(PREFIX)/$(BUDGIELIB)"
	cp preferences.ui "$(DESTDIR)$(PREFIX)/$(BUDGIELIB)"
	cp BudgieSysMonitor.plugin "$(DESTDIR)$(PREFIX)/$(BUDGIELIB)"
	
clean:
	rm -rf ../*.xz ../*.deb ../*.tar.gz ../*.changes ../*.dsc ../*.upload ../*.build ../*.cdbs-config_list
	
uninstall:
	rm -rf "$(DESTDIR)$(PREFIX)/lib/indicator-sysmonitor"
	rm -f "$(DESTDIR)$(PREFIX)/bin/indicator-sysmonitor"
	rm -f "$(DESTDIR)$(PREFIX)/share/applications/indicator-sysmonitor.desktop"
	rm -rf "$(DESTDIR)$(PREFIX)/$(BUDGIELIB)"

.PHONY: clean install all
