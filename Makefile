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
	rm -rf *.deb *.tar.gz *.changes *.dsc *.upload build *.cdbs-config_list
	rm -rf ${DESTDIR}/lib/indicator-sysmonitor
	rm ${DESTDIR}/bin/indicator-sysmonitor

.PHONY: clean install all
