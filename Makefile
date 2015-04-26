DESTDIR=/usr

all:

install:
	mkdir ${DESTDIR}/lib/indicator-sysmonitor
	cp indicator-sysmonitor ${DESTDIR}/lib/indicator-sysmonitor
	cp preferences.py ${DESTDIR}/lib/indicator-sysmonitor
	cp sensors.py ${DESTDIR}/lib/indicator-sysmonitor
	cp preferences.ui ${DESTDIR}/lib/indicator-sysmonitor
	ln -s ${DESTDIR}/lib/indicator-sysmonitor/indicator-sysmonitor ${DESTDIR}/bin/indicator-sysmonitor 
	cp indicator-sysmonitor.desktop ${DESTDIR}/share/applications/
	
clean:
	rm -rf ../*.xz ../*.deb ../*.tar.gz ../*.changes ../*.dsc ../*.upload ../*.build ../*.cdbs-config_list
	
uninstall:
	rm -rf ${DESTDIR}/lib/indicator-sysmonitor
	rm ${DESTDIR}/bin/indicator-sysmonitor
	rm ${DESTDIR}/share/applications/indicator-sysmonitor.desktop

.PHONY: clean install all
