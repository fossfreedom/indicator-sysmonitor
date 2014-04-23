DESTDIR=/usr

all:

install:
	cp indicator-sysmonitor ${DESTDIR}/bin/
	cp indicator-sysmonitor.desktop ${DESTDIR}/share/applications/
	
clean:
	rm -rf *.deb *.tar.gz *.changes *.dsc *.upload build *.cdbs-config_list

.PHONY: clean install all
