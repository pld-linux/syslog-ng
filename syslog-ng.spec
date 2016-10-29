# TODO:
# - switch to LTS version??? where???
# - relies on libs in /usr which is wrong
#   (well, for modules bringing additional functionality it's acceptable IMO --q)
# - package python module
#
# Conditional build:
%bcond_with	dynamic			# link dynamically with glib, eventlog, pcre (modules are always linked dynamically)
%if "%{pld_release}" == "ac"
%bcond_with	sql			# support for logging to SQL DB
%else
%bcond_without	sql			# support for logging to SQL DB
%endif
%bcond_without	tests			# do not perform "make check"
%bcond_without	http			# support for HTTP destination
%bcond_without	json			# support for JSON template formatting
%bcond_without	mongodb			# support for mongodb destination
%bcond_without	redis			# support for Redis destination
%bcond_without	smtp			# support for logging into SMTP
%bcond_without	geoip			# support for GeoIP
%bcond_without	riemann			# support for Riemann monitoring system
%bcond_without	systemd			# systemd (daemon and journal) support
%bcond_without	system_libivykis	# use system libivykis
%bcond_with	system_rabbitmq		# use system librabbitmq [not supported yet]

%if "%{pld_release}" == "ac"
%define		glib2_ver	1:2.16.0
%else
%define		glib2_ver	1:2.24.0
%endif
%define		mver	3.8
Summary:	Syslog-ng - new generation of the system logger
Summary(pl.UTF-8):	Syslog-ng - systemowy demon logujący nowej generacji
Summary(pt_BR.UTF-8):	Daemon de log nova geração
Name:		syslog-ng
Version:	3.8.1
Release:	1
License:	GPL v2+ with OpenSSL exception
Group:		Daemons
Source0:	https://github.com/balabit/syslog-ng/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	acf14563cf5ce435db8db35486ce66af
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Source4:	http://www.balabit.com/support/documentation/syslog-ng-ose-%{mver}-guides/en/syslog-ng-ose-v%{mver}-guide-admin/pdf/%{name}-ose-v%{mver}-guide-admin.pdf
# Source4-md5:	ab7f52430e6aca8f377963fcab155a3e
Source5:	%{name}-simple.conf
Patch0:		%{name}-datadir.patch
Patch1:		cap_syslog-vserver-workaround.patch
Patch2:		%{name}-nolibs.patch
Patch3:		%{name}-systemd.patch
Patch4:		man-paths.patch
Patch5:		%{name}-link.patch
URL:		https://www.balabit.com/network-security/syslog-ng/opensource-logging-system
%{?with_geoip:BuildRequires:	GeoIP-devel >= 1.5.1}
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake
BuildRequires:	bison >= 2.4
%{?with_http:BuildRequires:	curl-devel}
BuildRequires:	docbook-style-xsl
BuildRequires:	eventlog-devel >= 0.2.12
%{?with_tests:BuildRequires:	findutils}
BuildRequires:	flex
BuildRequires:	glib2-devel >= %{glib2_ver}
%{?with_redis:BuildRequires:	hiredis-devel}
%{?with_json:BuildRequires:	json-c-devel >= 0.9}
BuildRequires:	libcap-devel
%{?with_sql:BuildRequires:	libdbi-devel >= 0.8.3-2}
%{?with_smtp:BuildRequires:	libesmtp-devel}
%{?with_system_libivykis:BuildRequires:	libivykis-devel >= 0.36.1}
%{?with_mongodb:BuildRequires:	libmongo-client-devel >= 0.1.8}
BuildRequires:	libnet-devel >= 1:1.1.2.1-3
BuildRequires:	libtool >= 2:2.0
BuildRequires:	libwrap-devel
BuildRequires:	libxslt-progs
BuildRequires:	lz4-devel >= r131-5
BuildRequires:	openssl-devel >= 0.9.8
BuildRequires:	pcre-devel >= 6.1
BuildRequires:	pkgconfig
%{?with_system_rabbitmq:BuildRequires:	rabbitmq-c-devel >= 0.0.1}
%{?with_riemann:BuildRequires:	riemann-c-client-devel >= 1.0.0}
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.623
%{?with_systemd:BuildRequires:	systemd-devel >= 1:195}
BuildRequires:	which
%if %{with tests}
BuildRequires:	pylint
BuildRequires:	python
BuildRequires:	python-pep8
BuildRequires:	python-ply
BuildRequires:	tzdata
%endif
%if %{without dynamic}
BuildRequires:	eventlog-static >= 0.2.12
BuildRequires:	glib2-static >= %{glib2_ver}
%{?with_system_libivykis:BuildRequires:	libivykis-static >= 0.36.1}
BuildRequires:	pcre-static >= 6.1
BuildRequires:	zlib-static
%endif
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name}-libs = %{version}-%{release}
Requires:	psmisc >= 20.1
%{?with_system_rabbitmq:Requires:	rabbitmq-c >= 0.0.1}
Requires:	rc-scripts >= 0.4.3.0
Requires:	systemd-units >= 38
# for afsocket
Requires:	libnet >= 1:1.1.2.1-7
# for afsocket and dbparser
Requires:	openssl >= 0.9.8
Provides:	service(klogd)
Provides:	service(syslog)
Provides:	syslogdaemon
Obsoletes:	syslog-ng-module-afsocket
Obsoletes:	syslog-ng-module-dbparser
Obsoletes:	syslog-ng-systemd
Conflicts:	klogd
Conflicts:	msyslog
Conflicts:	rsyslog
Conflicts:	syslog
Conflicts:	cronie < 1.5.0-3
Conflicts:	fcron < 3.1.2-5
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	xsl_stylesheets_dir /usr/share/sgml/docbook/xsl-stylesheets

%if %{without dynamic}
# syslog-ng has really crazy linking rules (see their bugzilla).
# Some rules, according to syslog-ng devs, are like this:
# - libsyslog-ng.so has undefined symbols for third party libraries
#   and these symbols should go via main syslog-ng binary
# - same applies for modules
# In dynamic case tests are forcily linked with dynamic modules, which doesn't work with as-needed.
%define		filterout_ld			-Wl,--as-needed -Wl,--no-copy-dt-needed-entries
%define		no_install_post_check_so	1
%define		_sbindir			/sbin
%define		slibdir				/%{_lib}
%else
%define		slibdir				%{_libdir}
%endif
# or just %{_libdir}? modules seem to be always linked dynamically
%define		moduledir			%{slibdir}/syslog-ng

%description
syslog-ng is a syslogd replacement for Unix and Unix-like systems. It
has been tested on Solaris, BSDi and Linux, and were found to run
reliably. syslog-ng gives you a much enhanced configuration scheme,
which lets you filter messages based on not only priority/facility
pairs, but also on message content. You can use regexps to direct log
stream to different destinations. A destination can be anything from a
simple file to a network connection. syslog-ng supports TCP
logforwarding, together with hashing to prevent unauthorized
modification on the line.

%description -l pl.UTF-8
Syslog-ng jest zamiennikiem dla standardowo używanych programów typu
syslog. Działa w systemie SunOS, BSD, Linux. Daje znacznie większe
możliwości logowania i kontrolowania zbieranych informacji.

%description -l pt_BR.UTF-8
Syslog-ng é um substituto para o syslog tradicional, mas com diversas
melhorias, como, por exemplo, a habilidade de filtrar mensagens de log
por seu conteúdo (usando expressões regulares) e não apenas pelo par
facility/prioridade como o syslog original.

%package module-afmongodb
Summary:	MongoDB destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów w bazie MongoDB
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libmongo-client >= 0.1.8

%description module-afmongodb
MongoDB destination support module for syslog-ng.

%description module-afmongodb -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów w bazie MongoDB.

%package module-afsmtp
Summary:	SMTP output support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi wysyłania logów do serwerów SMTP
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	openssl >= 0.9.8

%description module-afsmtp
SMTP output support module for syslog-ng.

%description module-afsmtp -l pl.UTF-8
Moduł sysloga-ng do obsługi wysyłania logów do serwerów SMTP.

%package module-afsql
Summary:	SQL destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów w bazach SQL
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libdbi >= 0.8.3-2
Requires:	openssl >= 0.9.8

%description module-afsql
SQL destination support module for syslog-ng (via libdbi).

%description module-afsql -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów w bazach SQL (poprzez
libdbi).

%package module-http
Summary:	HTTP destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów poprzez HTTP
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description module-http
HTTP destination support module for syslog-ng (via libcurl).

%description module-http -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów poprzez HTTP (via libcurl).

%package module-json-plugin
Summary:	JSON formatting template function for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi szablonów z formatowaniem JSON
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	json-c >= 0.9
Obsoletes:	syslog-ng-module-tfjson

%description module-json-plugin
JSON formatting template function for syslog-ng.

%description module-json-plugin -l pl.UTF-8
Moduł sysloga-ng do obsługi szablonów z formatowaniem JSON.

%package module-redis
Summary:	Redis destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów w bazie Redis
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description module-redis
Redis destination support module for syslog-ng (via libhiredis).

%description module-redis -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów w bazie Redis (poprzez
libhiredis).

%package module-riemann
Summary:	Riemann destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów do systemu Riemann
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	riemann-c-client >= 1.0.0

%description module-riemann
Riemann destination support module for syslog-ng.

%description module-riemann -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów do systemu Riemann.

%package module-tfgeoip
Summary:	syslog-ng template function module to get GeoIP info from an IPv4 addresses
Summary(pl.UTF-8):	Moduł funkcji szablonu sysloga-ng do pobierania informacji GeoIP z adresów IPv4
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	GeoIP-libs >= 1.5.1

%description module-tfgeoip
syslog-ng template function module to get GeoIP info from an IPv4
addresses.

%description module-tfgeoip -l pl.UTF-8
Moduł funkcji szablonu sysloga-ng do pobierania informacji GeoIP z
adresów IPv4.

%package libs
Summary:	Shared library for syslog-ng
Summary(pl.UTF-8):	Biblioteka współdzielona sysloga-ng
Group:		Libraries
%if %{with dynamic}
Requires:	eventlog >= 0.2.12
Requires:	glib2 >= %{glib2_ver}
%{?with_system_libivykis:Requires:	libivykis >= 0.36.1}
Requires:	pcre >= 6.1
%endif
Conflicts:	syslog-ng < 3.3.1-3

%description libs
Shared library for syslog-ng.

%description libs -l pl.UTF-8
Biblioteka współdzielona sysloga-ng.

%package devel
Summary:	Header files for syslog-ng modules development
Summary(pl.UTF-8):	Pliki nagłówkowe do tworzenia modułów dla sysloga-ng
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
%if %{with dynamic}
Requires:	eventlog-devel >= 0.2.12
Requires:	glib2-devel >= %{glib2_ver}
%{?with_system_libivykis:Requires:	libivykis-devel >= 0.36.1}
Requires:	pcre-devel >= 6.1
%endif

%description devel
Header files for syslog-ng modules development.

%description devel -l pl.UTF-8
Pliki nagłówkowe do tworzenia modułów dla sysloga-ng.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
cp -p %{SOURCE4} doc
cp -p %{SOURCE5} contrib/syslog-ng.conf.simple

%{__sed} -i -e 's|/usr/bin/awk|/bin/awk|' scl/syslogconf/convert-syslogconf.awk

# timestamp paring on x32 confuses glib2 testsuite
%ifarch x32
%{__sed} -i -e '/tests\/unit\/test_msgparse/d' tests/unit/Makefile.am
%endif

%build
for i in . lib/ivykis; do
cd $i
	%{__libtoolize}
	%{__aclocal} `[ -d m4 ] && echo '-I m4'`
	%{__autoconf}
	%{__autoheader}
	%{__automake}
cd -
done
%configure \
	--sysconfdir=%{_sysconfdir}/syslog-ng \
	--disable-silent-rules \
	--with-default-modules=affile,afprog,afsocket,afuser,basicfuncs,csvparser,dbparser,syslogformat \
	--with-docbook=%{xsl_stylesheets_dir}/manpages/docbook.xsl \
%if %{with mongodb}
	--enable-mongodb \
	--with-libmongo-client=system \
%else
	--disable-mongodb \
%endif
%if %{with system_libivykis}
	--with-ivykis=system \
%else
	--with-ivykis=internal \
%endif
	%{?with_system_rabbitmq:--with-librabbitmq-client=system} \
	--with-module-dir=%{moduledir} \
	--with-pidfile-dir=/var/run \
	--with-systemdsystemunitdir=%{systemdunitdir} \
	--with-timezone-dir=%{_datadir}/zoneinfo \
	--enable-amqp \
	--enable-geoip%{!?with_geoip:=no} \
	--enable-http%{!?with_http:=no} \
	--enable-ipv6 \
	--enable-json%{!?with_json:=no} \
	--enable-linux-caps \
	--enable-manpages \
	--enable-pacct \
	--enable-pcre \
	--enable-redis%{!?with_redis:=no} \
	--enable-riemann%{!?with_riemann:=no} \
	--enable-smtp%{!?with_smtp:=no} \
	--enable-spoof-source \
	--enable-ssl \
	--enable-systemd%{!?with_systemd:=no} \
	--enable-tcp-wrapper \
%if %{with sql}
	--enable-sql \
%endif
%if %{with dynamic}
	--enable-dynamic-linking
%else
	--enable-mixed-linking
%endif

%{__make}


%if %{with tests}
LD_LIBRARY_PATH=$(find $PWD -name '*.so*' -printf "%h:")
PYTHONPATH=$(pwd)/tests/functional
export LD_LIBRARY_PATH PYTHONPATH
%{__make} check
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,logrotate.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/patterndb.d \
	$RPM_BUILD_ROOT/var/{log,lib/%{name}/xsd}

%{__make} -j1 install \
	pkgconfigdir=%{_pkgconfigdir} \
	DESTDIR=$RPM_BUILD_ROOT

%if "%{slibdir}" != "%{_libdir}"
install -d $RPM_BUILD_ROOT%{slibdir}
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libsyslog-ng-%{mver}.so.* $RPM_BUILD_ROOT%{slibdir}
ln -snf %{slibdir}/$(basename $RPM_BUILD_ROOT%{slibdir}/libsyslog-ng-%{mver}.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libsyslog-ng.so
%endif

%{__sed} -e 's|@@SBINDIR@@|%{_sbindir}|g' %{SOURCE1} > $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/syslog-ng

for n in cron daemon debug iptables kernel lpr maillog messages secure spooler syslog user xferlog; do
	> $RPM_BUILD_ROOT/var/log/$n
done
touch $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la
%{__rm} $RPM_BUILD_ROOT%{moduledir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = "1" ]; then
	# disable /proc/kmsg from config on first install on vserver
	{
		while read f ctx; do
			[ "$f" = "VxID:" -o "$f" = "s_context:" ] && break
		done </proc/self/status
	} 2>/dev/null
	if [ -z "$ctx" -o "$ctx" = "0" ]; then
		VSERVER=no
	else
		VSERVER=yes
	fi
	if [ "$VSERVER" = "yes" ]; then
		%{__sed} -i -e '/\/proc\/kmsg/ s/^[^#]/#&/' %{_sysconfdir}/%{name}/%{name}.conf
	fi
fi

/sbin/chkconfig --add syslog-ng
%service syslog-ng restart "syslog-ng daemon"

%systemd_post syslog-ng.service

%preun
if [ "$1" = "0" ]; then
	%service syslog-ng stop
	/sbin/chkconfig --del syslog-ng
fi
%systemd_preun syslog-ng.service

%postun
%systemd_reload

%triggerpostun -- syslog-ng < 3.3.4-3
%systemd_trigger syslog-ng.service

%triggerun -- syslog-ng < 3.0
sed -i -e 's#sync(\(.*\))#flush_lines(\1)#g' /etc/syslog-ng/syslog-ng.conf
sed -i -e 's#pipe ("/proc/kmsg"#file ("/proc/kmsg"#g' /etc/syslog-ng/syslog-ng.conf
sed -i -e 's#log_prefix#program_override#g' /etc/syslog-ng/syslog-ng.conf
sed -i -e 's#^destination #destination d_#g' /etc/syslog-ng/syslog-ng.conf
sed -i -e 's#destination(#destination(d_#g' /etc/syslog-ng/syslog-ng.conf
sed -i -e 's,\bstats\b,stats_freq,' /etc/syslog-ng/syslog-ng.conf
sed -i -e 's#match("IN\=\[A-Za-z0-9\]\* OUT=\[A-Za-z0-9\]\*");#match("IN=[A-Za-z0-9]* OUT=[A-Za-z0-9]*" value("MESSAGE"));#g' /etc/syslog-ng/syslog-ng.conf
sed -i -e "1 s#\(.*\)\$#@version: 3.0\n\1#g" /etc/syslog-ng/syslog-ng.conf
rm -f %{_var}/lib/%{name}/syslog-ng.persist
%service -q syslog-ng restart
exit 0

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS NEWS.md debian/syslog-ng.conf* contrib/relogger.pl
%doc contrib/syslog-ng.conf.{doc,simple,RedHat}
%doc contrib/{apparmor,selinux,syslog2ng} doc/syslog-ng-ose-v%{mver}-guide-admin.pdf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng/patterndb.d
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/scl.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/syslog-ng
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%{systemdunitdir}/syslog-ng.service
%dir %{moduledir}
%attr(755,root,root) %{moduledir}/libadd-contextual-data.so
%attr(755,root,root) %{moduledir}/libafamqp.so
%attr(755,root,root) %{moduledir}/libaffile.so
%attr(755,root,root) %{moduledir}/libafprog.so
%attr(755,root,root) %{moduledir}/libafsocket.so
%attr(755,root,root) %{moduledir}/libafstomp.so
%attr(755,root,root) %{moduledir}/libafuser.so
%attr(755,root,root) %{moduledir}/libbasicfuncs.so
%attr(755,root,root) %{moduledir}/libcef.so
%attr(755,root,root) %{moduledir}/libconfgen.so
%attr(755,root,root) %{moduledir}/libcryptofuncs.so
%attr(755,root,root) %{moduledir}/libcsvparser.so
%attr(755,root,root) %{moduledir}/libdate.so
%attr(755,root,root) %{moduledir}/libdbparser.so
%attr(755,root,root) %{moduledir}/libdisk-buffer.so
%attr(755,root,root) %{moduledir}/libgraphite.so
%attr(755,root,root) %{moduledir}/libkvformat.so
%attr(755,root,root) %{moduledir}/liblinux-kmsg-format.so
%attr(755,root,root) %{moduledir}/libpacctformat.so
%attr(755,root,root) %{moduledir}/libpseudofile.so
%if %{with systemd}
%attr(755,root,root) %{moduledir}/libsdjournal.so
%endif
%attr(755,root,root) %{moduledir}/libsyslogformat.so
%attr(755,root,root) %{moduledir}/libsystem-source.so
%attr(755,root,root) %{_sbindir}/syslog-ng
%attr(755,root,root) %{_sbindir}/syslog-ng-ctl
%attr(755,root,root) %{_bindir}/dqtool
%attr(755,root,root) %{_bindir}/loggen
%attr(755,root,root) %{_bindir}/pdbtool
%attr(755,root,root) %{_bindir}/update-patterndb

%dir %{_datadir}/syslog-ng/include
%dir %{_datadir}/syslog-ng/include/scl
%dir %{_datadir}/syslog-ng/include/scl/apache
%{_datadir}/syslog-ng/include/scl/apache/apache.conf
%{_datadir}/syslog-ng/include/scl/elasticsearch
%{_datadir}/syslog-ng/include/scl/hdfs
%dir %{_datadir}/syslog-ng/include/scl/graphite
%{_datadir}/syslog-ng/include/scl/graphite/README
%{_datadir}/syslog-ng/include/scl/graphite/plugin.conf
%{_datadir}/syslog-ng/include/scl/kafka
%dir %{_datadir}/syslog-ng/include/scl/loggly
%{_datadir}/syslog-ng/include/scl/loggly/loggly.conf
%dir %{_datadir}/syslog-ng/include/scl/logmatic
%{_datadir}/syslog-ng/include/scl/logmatic/logmatic.conf
%{_datadir}/syslog-ng/include/scl/mbox
%dir %{_datadir}/syslog-ng/include/scl/nodejs
%{_datadir}/syslog-ng/include/scl/nodejs/plugin.conf
%dir %{_datadir}/syslog-ng/include/scl/pacct
%{_datadir}/syslog-ng/include/scl/pacct/plugin.conf
%dir %{_datadir}/syslog-ng/include/scl/rewrite
%{_datadir}/syslog-ng/include/scl/rewrite/cc-mask.conf
%{_datadir}/syslog-ng/include/scl/solaris
%dir %{_datadir}/syslog-ng/include/scl/syslogconf
%{_datadir}/syslog-ng/include/scl/syslogconf/README
%attr(755,root,root) %{_datadir}/syslog-ng/include/scl/syslogconf/convert-syslogconf.awk
%{_datadir}/syslog-ng/include/scl/syslogconf/plugin.conf
%dir %{_datadir}/syslog-ng/include/scl/system
%{_datadir}/syslog-ng/include/scl/system/plugin.conf
%dir %{_datadir}/syslog-ng/xsd
%{_datadir}/syslog-ng/xsd/patterndb-*.xsd

%dir %{_var}/lib/%{name}
%dir %{_var}/lib/%{name}/xsd
%{_mandir}/man1/loggen.1*
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man1/syslog-ng-ctl.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*

%attr(640,root,logs) %ghost /var/log/cron
%attr(640,root,logs) %ghost /var/log/daemon
%attr(640,root,logs) %ghost /var/log/debug
%attr(640,root,logs) %ghost /var/log/iptables
%attr(640,root,logs) %ghost /var/log/kernel
%attr(640,root,logs) %ghost /var/log/lpr
%attr(640,root,logs) %ghost /var/log/maillog
%attr(640,root,logs) %ghost /var/log/messages
%attr(640,root,logs) %ghost /var/log/secure
%attr(640,root,logs) %ghost /var/log/spooler
%attr(640,root,logs) %ghost /var/log/syslog
%attr(640,root,logs) %ghost /var/log/user
%attr(640,root,logs) %ghost /var/log/xferlog

%if %{with mongodb}
%files module-afmongodb
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libafmongodb.so
%endif

%if %{with smtp}
%files module-afsmtp
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libafsmtp.so
%endif

%if %{with sql}
%files module-afsql
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libafsql.so
%endif

%if %{with http}
%files module-http
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libcurl.so
%endif

%if %{with json}
%files module-json-plugin
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libjson-plugin.so
%{_datadir}/syslog-ng/include/scl/cim
%endif

%if %{with redis}
%files module-redis
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libredis.so
%endif

%if %{with riemann}
%files module-riemann
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libriemann.so
%endif

%if %{with geoip}
%files module-tfgeoip
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libgeoip-plugin.so
%endif

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{slibdir}/libsyslog-ng-%{mver}.so.*.*.*
%attr(755,root,root) %ghost %{slibdir}/libsyslog-ng-%{mver}.so.0
%dir %{_datadir}/syslog-ng

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsyslog-ng.so
%{_libdir}/libsyslog-ng-native-connector.a
%dir %{_includedir}/syslog-ng
%{_includedir}/syslog-ng/*.h
%{_includedir}/syslog-ng/compat
%{_includedir}/syslog-ng/control
%{_includedir}/syslog-ng/debugger
%{_includedir}/syslog-ng/filter
%if %{without system_libivykis}
%{_includedir}/syslog-ng/ivykis
%endif
%{_includedir}/syslog-ng/logmsg
%{_includedir}/syslog-ng/logproto
%{_includedir}/syslog-ng/parser
%{_includedir}/syslog-ng/rewrite
%{_includedir}/syslog-ng/scanner
%{_includedir}/syslog-ng/stats
%{_includedir}/syslog-ng/template
%{_includedir}/syslog-ng/transport
%{_includedir}/syslog-ng/value-pairs
%{_datadir}/syslog-ng/tools
%{_pkgconfigdir}/syslog-ng.pc
%{_pkgconfigdir}/syslog-ng-native-connector.pc

# test-devel ?
%if "%{_libdir}/syslog-ng" != "{moduledir}"
%dir %{_libdir}/syslog-ng
%endif
%dir %{_libdir}/syslog-ng/libtest
%{_libdir}/syslog-ng/libtest/libsyslog-ng-test.a
%{_includedir}/syslog-ng/libtest
%{_pkgconfigdir}/syslog-ng-test.pc
