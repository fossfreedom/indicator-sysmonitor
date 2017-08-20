DESTDIR=/usr
BUDGIELIB=lib/budgie-desktop/plugins/budgiesysmonitor

all:

install:
	mkdir -p ${DESTDIR}/lib/indicator-sysmonitor
	cp indicator-sysmonitor ${DESTDIR}/lib/indicator-sysmonitor
	cp preferences.py ${DESTDIR}/lib/indicator-sysmonitor
	cp sensors.py ${DESTDIR}/lib/indicator-sysmonitor
	cp preferences.ui ${DESTDIR}/lib/indicator-sysmonitor
	ln -s ${DESTDIR}/lib/indicator-sysmonitor/indicator-sysmonitor ${DESTDIR}/bin/indicator-sysmonitor 
	cp indicator-sysmonitor.desktop ${DESTDIR}/share/applications/
	
installbudgie:
	mkdir -p ${DESTDIR}/${BUDGIELIB}
	cp budgiesysmonitor.py ${DESTDIR}/${BUDGIELIB}
	cp preferences.py ${DESTDIR}/${BUDGIELIB}
	cp sensors.py ${DESTDIR}/${BUDGIELIB}
	cp preferences.ui ${DESTDIR}/${BUDGIELIB}
	cp BudgieSysMonitor.plugin ${DESTDIR}/${BUDGIELIB} 
	
clean:
	rm -rf ../*.xz ../*.deb ../*.tar.gz ../*.changes ../*.dsc ../*.upload ../*.build ../*.cdbs-config_list
	
uninstall:
	rm -rf ${DESTDIR}/lib/indicator-sysmonitor
	rm -f ${DESTDIR}/bin/indicator-sysmonitor
	rm -f ${DESTDIR}/share/applications/indicator-sysmonitor.desktop
	rm -rf ${DESTDIR}/${BUDGIELIB}

.PHONY: clean install all
