# NOTE: only core functionality is available without /usr;
#       some non-trivial extension modules rely in libraries/daemons existing in /usr.
#
# Conditional build:
%bcond_with	dynamic			# link dynamically with glib, eventlog, pcre (modules are always linked dynamically)
%if "%{pld_release}" == "ac"
%bcond_with	sql			# support for logging to SQL DB
%else
%bcond_without	sql			# support for logging to SQL DB
%endif
%bcond_without	tests			# do not perform "make check"
%bcond_with	bpf			# loading eBPF programs support (generates some data from current kernel)
%bcond_without	grpc			# support for GRPC protocols
%bcond_without	http			# support for HTTP destination
%bcond_without	json			# support for JSON template formatting
%bcond_without	mongodb			# support for mongodb destination
%bcond_without	mqtt			# support for MQTT protocol
%bcond_without	redis			# support for Redis destination
%bcond_without	smtp			# support for logging into SMTP
%bcond_without	geoip2			# support for GeoIP2
%bcond_without	kafka			# support for Apache Kafka protocol
%bcond_without	riemann			# support for Riemann monitoring system
%bcond_without	systemd			# systemd (daemon and journal) support
%bcond_without	amqp			# AMQP support
%bcond_without	python			# python module
%bcond_with	java			# java modules and support
%bcond_without	system_libivykis	# use system libivykis
%bcond_without	system_rabbitmq		# use system librabbitmq

%if %{without amqp}
%undefine with_system_rabbitmq
%endif

# as in git submodule
%define	libivykis_version 0.43.2

%define		glib2_ver	1:2.32.0
%define		mver	4.8
Summary:	Syslog-ng - new generation of the system logger
Summary(pl.UTF-8):	Syslog-ng - systemowy demon logujący nowej generacji
Summary(pt_BR.UTF-8):	Daemon de log nova geração
Name:		syslog-ng
Version:	4.8.1
Release:	1
License:	GPL v2+ with OpenSSL exception
Group:		Daemons
#Source0Download: https://github.com/syslog-ng/syslog-ng/releases
Source0:	https://github.com/syslog-ng/syslog-ng/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	6a5852343f9a34449c3812b474728aa7
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Source4:	%{name}-simple.conf
%if 0
# for git archives (release tarballs include ivykis)
#Source5Download: https://github.com/buytenh/ivykis/releases
#Source5:	https://github.com/buytenh/ivykis/archive/v%{libivykis_version}/ivykis-%{libivykis_version}.tar.gz
Source5:	https://downloads.sourceforge.net/libivykis/ivykis-%{libivykis_version}.tar.gz
# Source5-md5:	df51c6d5c52bef1c82ea33eddc997792
%endif
Source7:	syslog-ng.service
Patch0:		%{name}-datadir.patch
Patch2:		%{name}-nolibs.patch
Patch3:		%{name}-systemd.patch
Patch4:		man-paths.patch
Patch5:		%{name}-link.patch
Patch6:		no_shared_ivykis.patch
Patch7:		32bit.patch

Patch9:		glib-static.patch
URL:		https://syslog-ng.org/
BuildRequires:	autoconf >= 2.59
BuildRequires:	automake
BuildRequires:	bison >= 3.7.6
%if %{with tests}
BuildRequires:	criterion-devel >= 2.3.3-5
%endif
%{?with_http:BuildRequires:	curl-devel}
BuildRequires:	docbook-style-xsl
BuildRequires:	eventlog-devel >= 0.2.12
BuildRequires:	flex
BuildRequires:	glib2-devel >= %{glib2_ver}
%{?with_java:BuildRequires:	gradle >= 3.4}
%{?with_grpc:BuildRequires:	grpc-devel >= 1.16.1}
%{?with_redis:BuildRequires:	hiredis-devel >= 0.11.0}
%{?with_java:BuildRequires:	jdk >= 1.8}
%{?with_json:BuildRequires:	json-c-devel >= 0.13}
# bpftool
%{?with_bpf:BuildRequires:	kernel-tools >= 4.15}
%{?with_bpf:BuildRequires:	libbpf-devel >= 1.0.1}
BuildRequires:	libcap-devel
%{?with_sql:BuildRequires:	libdbi-devel >= 0.9.0}
%{?with_smtp:BuildRequires:	libesmtp-devel}
%{?with_system_libivykis:BuildRequires:	libivykis-devel >= %{libivykis_version}}
%{?with_geoip2:BuildRequires:	libmaxminddb-devel}
BuildRequires:	libnet-devel >= 1:1.1.2.1-3
%{?with_kafka:BuildRequires:	librdkafka-devel >= 1.1.0}
BuildRequires:	libtool >= 2:2.0
BuildRequires:	libwrap-devel
BuildRequires:	libxslt-progs
BuildRequires:	lz4-devel >= r131-5
%{?with_mongodb:BuildRequires:	mongo-c-driver-devel >= 1.0.0}
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel >= 0.9.8
%{?with_mqtt:BuildRequires:	paho-mqtt-devel}
BuildRequires:	pcre2-8-devel >= 10.0
BuildRequires:	pkgconfig
%{?with_grpc:BuildRequires:	protobuf-devel >= 3.12.0}
%{?with_system_rabbitmq:BuildRequires:	rabbitmq-c-devel >= 0.5.3}
%{?with_riemann:BuildRequires:	riemann-c-client-devel >= 1.6.0}
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.623
%{?with_systemd:BuildRequires:	systemd-devel >= 1:245}
BuildRequires:	which
%if %{with tests}
BuildRequires:	GeoIP-db-Country
BuildRequires:	pylint
BuildRequires:	python3
%{?with_python:BuildRequires:	python3-devel >= 1:3.2}
BuildRequires:	python3-pep8
BuildRequires:	python3-ply
BuildRequires:	python3-pytest-mock
BuildRequires:	tzdata
%endif
%if %{without dynamic}
BuildRequires:	eventlog-static >= 0.2.12
BuildRequires:	glib2-static >= %{glib2_ver}
%{?with_system_libivykis:BuildRequires:	libivykis-static >= %{libivykis_version}}
BuildRequires:	pcre-static >= 6.1
BuildRequires:	zlib-static
%endif
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name}-libs = %{version}-%{release}
Requires:	psmisc >= 20.1
%{?with_system_rabbitmq:Requires:	rabbitmq-c >= 0.5.3}
Requires:	rc-scripts >= 0.4.3.0
Requires:	systemd-units >= 38
# for afsocket
Requires:	libnet >= 1:1.1.2.1-7
# for afsocket and dbparser
Requires:	openssl >= 0.9.8
Provides:	service(klogd)
Provides:	service(syslog)
Provides:	syslogdaemon
Obsoletes:	syslog-ng-module-afsocket < 3.3.1-4
Obsoletes:	syslog-ng-module-dbparser < 3.3.1-4
Obsoletes:	syslog-ng-systemd < 3.3.4-3
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
Requires:	mongo-c-driver >= 1.0.0

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
Requires:	libdbi >= 0.9.0
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

%package module-cloudauth
Summary:	Cloud Authentication support for syslog-ng: pubsub
Summary(pl.UTF-8):	Moduł sysloga-ng do uwierzytelniania chmurowego na potrzeby pubsub
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description module-cloudauth
Cloud Authentication support for syslog-ng, currently used for Google
PubSub.

%description module-cloudauth -l pl.UTF-8
Moduł sysloga-ng do obsługi uwierzytelniania w chmurze, używany przez
Google PubSub.

%package module-grpc
Summary:	GRPC modules for syslog-ng: bigquery, loki, otel
Summary(pl.UTF-8):	Moduły GRPC dla sysloga-ng: bigquery, loki, otel
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description module-grpc
GRPC protocols support for syslog-ng, currently: bigquery, loki and
otel.

%description module-grpc -l pl.UTF-8
Obsługa protokołów GRPC dla sysloga-ng, obecnie: bigquery, loki i
otel.

%package module-json-plugin
Summary:	JSON formatting template function for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi szablonów z formatowaniem JSON
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	json-c >= 0.9
Obsoletes:	syslog-ng-module-tfjson < 3.4.2

%description module-json-plugin
JSON formatting template function for syslog-ng.

%description module-json-plugin -l pl.UTF-8
Moduł sysloga-ng do obsługi szablonów z formatowaniem JSON.

%package module-kafka
Summary:	Apache Kafka destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów poprzez protokół Apache Kafka
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	librdkafka >= 1.1.0

%description module-kafka
Apache Kafka destination support module for syslog-ng.

%description module-kafka -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów poprzez protokół Apache
Kafka.

%package module-mqtt
Summary:	MQTT protocol support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi protokołu MQTT
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description module-mqtt
MQTT protocol support module for syslog-ng.

%description module-mqtt -l pl.UTF-8
Moduł sysloga-ng do obsługi protokołu MQTT.

%package module-python
Summary:	Python support module for syslog-ng
Summary(pl.UTF-8):	Moduł obsługi Pythona dla sysloga-ng
Group:		Librares
Requires:	%{name} = %{version}-%{release}

%description module-python
Python support module for syslog-ng.

%description module-python -l pl.UTF-8
Moduł obsługi Pythona dla sysloga-ng.

%package module-redis
Summary:	Redis destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów w bazie Redis
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	hiredis >= 0.11.0

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
Requires:	riemann-c-client >= 1.6.0

%description module-riemann
Riemann destination support module for syslog-ng.

%description module-riemann -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów do systemu Riemann.

%package libs
Summary:	Shared library for syslog-ng
Summary(pl.UTF-8):	Biblioteka współdzielona sysloga-ng
Group:		Libraries
%if %{with dynamic}
Requires:	eventlog >= 0.2.12
Requires:	glib2 >= %{glib2_ver}
Requires:	pcre >= 6.1
%endif
%{?with_system_libivykis:Requires:  libivykis >= %{libivykis_version}}
%{?with_systemd:Requires:	systemd-libs >= 1:245}
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
Requires:	pcre-devel >= 6.1
%endif
%{?with_system_libivykis:Requires:  libivykis-devel >= %{libivykis_version}}

%description devel
Header files for syslog-ng modules development.

%description devel -l pl.UTF-8
Pliki nagłówkowe do tworzenia modułów dla sysloga-ng.

%package test-devel
Summary:	syslog-ng test library
Summary(pl.UTF-8):	Biblioteka testowa sysloga-ng
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description test-devel
Test helper package for syslog-ng modules.

%description test-devel -l pl.UTF-8
Pakiet pomocniczy do testowania modułów sysloga-ng.

%prep
%if 1
# release tarball
%setup -q
%else
# git archive
%setup -q -n %{name}-%{name}-%{version} -a 5

rmdir lib/ivykis
%{__mv} ivykis-%{libivykis_version} lib/ivykis
%endif

%patch -P0 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1
%patch -P7 -p1

%patch -P9 -p1
cp -p %{SOURCE4} contrib/syslog-ng.conf.simple

%{__sed} -i -e 's|/usr/bin/awk|/bin/awk|' scl/syslogconf/convert-syslogconf.awk
%{__sed} -i -e '1s,/usr/bin/env python3$,%{__python3},' lib/merge-grammar.py

%build
for i in . ; do
cd $i
	%{__libtoolize}
	%{__aclocal} `[ -d m4 ] && echo '-I m4'`
	%{__autoconf}
	%{__autoheader}
	%{__automake}
cd -
done
%configure \
	PYTHON="%{__python3}" \
	--sysconfdir=%{_sysconfdir}/syslog-ng \
	--disable-silent-rules \
	%{__enable_disable amqp} \
%if %{with dynamic}
	--enable-dynamic-linking \
%else
	--enable-mixed-linking \
%endif
	--enable-ebpf%{!?with_bpf:=no} \
	%{__enable_disable geoip2} \
	--enable-grpc%{!?with_grpc:=no} \
	--enable-http%{!?with_http:=no} \
	--enable-ipv6 \
	--enable-java%{!?with_java:=no} \
	--enable-java-modules%{!?with_java:=no} \
	--enable-json%{!?with_json:=no} \
	--enable-linux-caps \
	--enable-kafka%{!?with_kafka:=no} \
	--enable-manpages \
%if %{with mongodb}
	--enable-mongodb \
	--with-mongoc=system \
%else
	--disable-mongodb \
%endif
	--enable-mqtt%{!?with_mqtt:=no} \
	--enable-pacct \
	--enable-pcre \
	--enable-python%{!?with_python:=no} \
	--enable-redis%{!?with_redis:=no} \
	--enable-riemann%{!?with_riemann:=no} \
	--enable-smtp%{!?with_smtp:=no} \
	--enable-spoof-source \
	--enable-ssl \
	--enable-systemd%{!?with_systemd:=no} \
	--with-systemd-journal=auto \
	--enable-tcp-wrapper \
%if %{with sql}
	--enable-sql \
%endif
	--with-default-modules=affile,afprog,afsocket,afuser,basicfuncs,csvparser,dbparser,syslogformat \
	--with-docbook=%{xsl_stylesheets_dir}/manpages/docbook.xsl \
%if %{with system_libivykis}
	--with-ivykis=system \
%else
	--with-ivykis=internal \
%endif
	%{?with_system_rabbitmq:--with-librabbitmq-client=system} \
	--with-module-dir=%{moduledir} \
	--with-pidfile-dir=/var/run \
	--with-python-packages=none \
	--with-systemdsystemunitdir=%{systemdunitdir} \
	--with-timezone-dir=%{_datadir}/zoneinfo

%{__make}

%if %{with tests}
LD_LIBRARY_PATH=$(find $PWD -name '*.so*' -printf "%h:")
PYTHONPATH=$(pwd)/tests/functional
export LD_LIBRARY_PATH PYTHONPATH
if ! %{__make} check; then
	cat test-suite.log
	exit 1
fi
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{syslog-ng.d,sysconfig,logrotate.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/patterndb.d \
	$RPM_BUILD_ROOT/var/{log,lib/%{name}/xsd}

%{__make} -j1 install \
	pkgconfigdir=%{_pkgconfigdir} \
	DESTDIR=$RPM_BUILD_ROOT

%if "%{slibdir}" != "%{_libdir}"
install -d $RPM_BUILD_ROOT%{slibdir}
%{__mv} $RPM_BUILD_ROOT%{_libdir}/libsyslog-ng-%{mver}.so.* $RPM_BUILD_ROOT%{slibdir}
ln -snf %{slibdir}/$(basename $RPM_BUILD_ROOT%{slibdir}/libsyslog-ng-%{mver}.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libsyslog-ng.so

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libevtlog-%{mver}.so.* $RPM_BUILD_ROOT%{slibdir}
ln -snf %{slibdir}/$(basename $RPM_BUILD_ROOT%{slibdir}/libevtlog-%{mver}.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libevtlog.so

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libloggen_helper-%{mver}.so.* $RPM_BUILD_ROOT%{slibdir}
ln -snf %{slibdir}/$(basename $RPM_BUILD_ROOT%{slibdir}/libloggen_helper-%{mver}.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libloggen_helper.so

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libloggen_plugin-%{mver}.so.* $RPM_BUILD_ROOT%{slibdir}
ln -snf %{slibdir}/$(basename $RPM_BUILD_ROOT%{slibdir}/libloggen_plugin-%{mver}.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libloggen_plugin.so

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libsecret-storage.so.* $RPM_BUILD_ROOT%{slibdir}
ln -snf %{slibdir}/$(basename $RPM_BUILD_ROOT%{slibdir}/libsecret-storage.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libsecret-storage.so
%endif

%{__sed} -e 's|@@SBINDIR@@|%{_sbindir}|g' %{SOURCE1} > $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
sed -e 's,#VERSION#,%{mver},' < %{SOURCE2} > $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/syslog-ng
cp -p %{SOURCE7} $RPM_BUILD_ROOT%{systemdunitdir}

for n in cron daemon debug iptables kernel lpr maillog messages secure spooler syslog user xferlog; do
	> $RPM_BUILD_ROOT/var/log/$n
done
touch $RPM_BUILD_ROOT/etc/sysconfig/%{name}
ln -s "%{name}" $RPM_BUILD_ROOT/etc/sysconfig/%{name}@default

%{__rm} $RPM_BUILD_ROOT%{_sbindir}/syslog-ng-debun
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man1/syslog-ng-debun.1
%{__rm} $RPM_BUILD_ROOT%{moduledir}/libexamples.so
%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la
%{__rm} $RPM_BUILD_ROOT%{moduledir}/*.la
%{__rm} $RPM_BUILD_ROOT%{moduledir}/loggen/*.la

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

%systemd_post syslog-ng@.service syslog-ng.service

%preun
if [ "$1" = "0" ]; then
	%service syslog-ng stop
	/sbin/chkconfig --del syslog-ng
fi
%systemd_preun syslog-ng@.service syslog-ng.service

%postun
%systemd_reload

%triggerpostun -- syslog-ng < 3.3.4-3
%systemd_trigger syslog-ng@.service syslog-ng.service

%triggerun -- syslog-ng < 3.19.1
grep -q '^@include "/etc/syslog-ng\.d/\*\.conf"' /etc/syslog-ng/syslog-ng.conf || echo '@include "/etc/syslog-ng.d/*.conf"' >> /etc/syslog-ng/syslog-ng.conf
# 3.0
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

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%post	module-grpc -p /sbin/ldconfig
%postun	module-grpc -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS NEWS.md contrib/relogger.pl
%doc contrib/syslog-ng.conf.{doc,simple,RedHat}
%doc contrib/{apparmor,selinux,syslog2ng}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}@default
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng/patterndb.d
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng.d
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/syslog-ng
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%{systemdunitdir}/syslog-ng@.service
%{systemdunitdir}/syslog-ng.service
%dir %{moduledir}
%attr(755,root,root) %{moduledir}/libadd-contextual-data.so
%if %{with amqp}
%attr(755,root,root) %{moduledir}/libafamqp.so
%endif
%attr(755,root,root) %{moduledir}/libaffile.so
%attr(755,root,root) %{moduledir}/libafprog.so
%attr(755,root,root) %{moduledir}/libafsnmp.so
%attr(755,root,root) %{moduledir}/libafsocket.so
%attr(755,root,root) %{moduledir}/libafstomp.so
%attr(755,root,root) %{moduledir}/libafuser.so
%attr(755,root,root) %{moduledir}/libappmodel.so
%attr(755,root,root) %{moduledir}/libazure-auth-header.so
%attr(755,root,root) %{moduledir}/libbasicfuncs.so
%attr(755,root,root) %{moduledir}/libcef.so
%attr(755,root,root) %{moduledir}/libconfgen.so
%attr(755,root,root) %{moduledir}/libcorrelation.so
%attr(755,root,root) %{moduledir}/libcryptofuncs.so
%attr(755,root,root) %{moduledir}/libcsvparser.so
#%attr(755,root,root) %{moduledir}/libdbparser.so
%attr(755,root,root) %{moduledir}/libdisk-buffer.so
%if %{with geoip2}
%attr(755,root,root) %{moduledir}/libgeoip2-plugin.so
%endif
%attr(755,root,root) %{moduledir}/libgraphite.so
%attr(755,root,root) %{moduledir}/libhook-commands.so
%attr(755,root,root) %{moduledir}/libkvformat.so
%attr(755,root,root) %{moduledir}/liblinux-kmsg-format.so
%attr(755,root,root) %{moduledir}/libmap-value-pairs.so
%attr(755,root,root) %{moduledir}/libmetrics-probe.so
%attr(755,root,root) %{moduledir}/libpacctformat.so
%attr(755,root,root) %{moduledir}/libpseudofile.so
%attr(755,root,root) %{moduledir}/librate-limit-filter.so
%attr(755,root,root) %{moduledir}/libregexp-parser.so
%attr(755,root,root) %{moduledir}/libsecure-logging.so
%attr(755,root,root) %{moduledir}/libstardate.so
%attr(755,root,root) %{moduledir}/libtags-parser.so
%attr(755,root,root) %{moduledir}/libtfgetent.so
%attr(755,root,root) %{moduledir}/libtimestamp.so
%attr(755,root,root) %{moduledir}/libxml.so
%if %{with systemd}
%attr(755,root,root) %{moduledir}/libsdjournal.so
%endif
%attr(755,root,root) %{moduledir}/libsyslogformat.so
%attr(755,root,root) %{moduledir}/libsystem-source.so
%dir %{moduledir}/loggen
%attr(755,root,root) %{moduledir}/loggen/libloggen_socket_plugin.so
%attr(755,root,root) %{moduledir}/loggen/libloggen_ssl_plugin.so
%attr(755,root,root) %{_sbindir}/syslog-ng
%attr(755,root,root) %{_sbindir}/syslog-ng-ctl
%attr(755,root,root) %{_bindir}/dqtool
%attr(755,root,root) %{_bindir}/loggen
%attr(755,root,root) %{_bindir}/pdbtool
%attr(755,root,root) %{_bindir}/persist-tool
%attr(755,root,root) %{_bindir}/slogencrypt
%attr(755,root,root) %{_bindir}/slogkey
%attr(755,root,root) %{_bindir}/slogverify
%attr(755,root,root) %{_bindir}/syslog-ng-update-virtualenv
%attr(755,root,root) %{_bindir}/update-patterndb

%{_datadir}/syslog-ng/smart-multi-line.fsm
%dir %{_datadir}/syslog-ng/include
%{_datadir}/syslog-ng/include/scl.conf
%dir %{_datadir}/syslog-ng/include/scl
%{_datadir}/syslog-ng/include/scl/apache
%{_datadir}/syslog-ng/include/scl/arr
%{_datadir}/syslog-ng/include/scl/checkpoint
%{_datadir}/syslog-ng/include/scl/cisco
# R: basicfuncs
%{_datadir}/syslog-ng/include/scl/collectd
%{_datadir}/syslog-ng/include/scl/darwinosl
%{_datadir}/syslog-ng/include/scl/default-network-drivers
%{_datadir}/syslog-ng/include/scl/fortigate
%{_datadir}/syslog-ng/include/scl/graphite
%{_datadir}/syslog-ng/include/scl/hdfs
%{_datadir}/syslog-ng/include/scl/kafka
%{_datadir}/syslog-ng/include/scl/iptables
%{_datadir}/syslog-ng/include/scl/jellyfin
%{_datadir}/syslog-ng/include/scl/junos
%{_datadir}/syslog-ng/include/scl/linux-audit
%dir %{_datadir}/syslog-ng/include/scl/loadbalancer
%attr(755,root,root) %{_datadir}/syslog-ng/include/scl/loadbalancer/gen-loadbalancer.sh
%{_datadir}/syslog-ng/include/scl/loadbalancer/plugin.conf
%{_datadir}/syslog-ng/include/scl/logscale
%{_datadir}/syslog-ng/include/scl/mariadb
%{_datadir}/syslog-ng/include/scl/mbox
%{_datadir}/syslog-ng/include/scl/nodejs
%{_datadir}/syslog-ng/include/scl/openobserve
%{_datadir}/syslog-ng/include/scl/opensearch
%{_datadir}/syslog-ng/include/scl/osquery
%{_datadir}/syslog-ng/include/scl/pacct
%{_datadir}/syslog-ng/include/scl/paloalto
%{_datadir}/syslog-ng/include/scl/pgsql
%{_datadir}/syslog-ng/include/scl/pihole
%{_datadir}/syslog-ng/include/scl/python
%{_datadir}/syslog-ng/include/scl/qbittorrent
%{_datadir}/syslog-ng/include/scl/rewrite
%{_datadir}/syslog-ng/include/scl/snmptrap
%{_datadir}/syslog-ng/include/scl/solaris
%{_datadir}/syslog-ng/include/scl/splunk
%{_datadir}/syslog-ng/include/scl/sudo
%{_datadir}/syslog-ng/include/scl/sumologic
%{_datadir}/syslog-ng/include/scl/websense
%{_datadir}/syslog-ng/include/scl/windowseventlog
%dir %{_datadir}/syslog-ng/include/scl/syslogconf
%{_datadir}/syslog-ng/include/scl/syslogconf/README
%attr(755,root,root) %{_datadir}/syslog-ng/include/scl/syslogconf/convert-syslogconf.awk
%{_datadir}/syslog-ng/include/scl/syslogconf/plugin.conf
%{_datadir}/syslog-ng/include/scl/system
%{_datadir}/syslog-ng/xsd

%dir %{_var}/lib/%{name}
%dir %{_var}/lib/%{name}/xsd
%{_mandir}/man1/dqtool.1*
%{_mandir}/man1/loggen.1*
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man1/persist-tool.1*
%{_mandir}/man1/slogencrypt.1*
%{_mandir}/man1/slogkey.1*
%{_mandir}/man1/slogverify.1*
%{_mandir}/man1/syslog-ng-ctl.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man7/secure-logging.7*
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
%attr(755,root,root) %{moduledir}/libhttp.so
%{_datadir}/syslog-ng/include/scl/telegram
%endif

%files module-cloudauth
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libcloud_auth.so
%{_datadir}/syslog-ng/include/scl/google/google-pubsub.conf

%files module-grpc
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libgrpc-protos.so.*.*.*
%ghost %{_libdir}/libgrpc-protos.so.0
%{_libdir}/libgrpc-protos.so
%attr(755,root,root) %{moduledir}/libbigquery.so
%attr(755,root,root) %{moduledir}/libloki.so
%attr(755,root,root) %{moduledir}/libotel.so

%if %{with json}
%files module-json-plugin
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libjson-plugin.so
# all below configs require json-plugin
%{_datadir}/syslog-ng/include/scl/cee
# R: basicfuncs http json-plugin
%{_datadir}/syslog-ng/include/scl/discord
%{_datadir}/syslog-ng/include/scl/cim
# R: http json-plugin
%{_datadir}/syslog-ng/include/scl/elasticsearch
%{_datadir}/syslog-ng/include/scl/ewmm
%{_datadir}/syslog-ng/include/scl/graylog2
%{_datadir}/syslog-ng/include/scl/loggly
%{_datadir}/syslog-ng/include/scl/logmatic
%{_datadir}/syslog-ng/include/scl/netskope
# R: basicfuncs http json-plugin
%{_datadir}/syslog-ng/include/scl/slack
%endif

%if %{with kafka}
%files module-kafka
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libkafka.so
%endif

%if %{with mqtt}
%files module-mqtt
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libmqtt.so
%endif

%if %{with python}
%files module-python
%defattr(644,root,root,755)
%attr(755,root,root) %{moduledir}/libmod-python.so
%{moduledir}/python
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

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{slibdir}/libevtlog-%{mver}.so.*.*.*
%attr(755,root,root) %{slibdir}/libevtlog-%{mver}.so.0
%attr(755,root,root) %{slibdir}/libloggen_helper-%{mver}.so.*.*.*
%attr(755,root,root) %{slibdir}/libloggen_helper-%{mver}.so.0
%attr(755,root,root) %{slibdir}/libloggen_plugin-%{mver}.so.*.*.*
%attr(755,root,root) %{slibdir}/libloggen_plugin-%{mver}.so.0
%attr(755,root,root) %{slibdir}/libsecret-storage.so.*.*.*
%attr(755,root,root) %{slibdir}/libsecret-storage.so.0
%attr(755,root,root) %{slibdir}/libsyslog-ng-%{mver}.so.*.*.*
%attr(755,root,root) %ghost %{slibdir}/libsyslog-ng-%{mver}.so.0
%dir %{_datadir}/syslog-ng

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libevtlog.so
%attr(755,root,root) %{_libdir}/libloggen_helper.so
%attr(755,root,root) %{_libdir}/libloggen_plugin.so
%attr(755,root,root) %{_libdir}/libsecret-storage.so
%attr(755,root,root) %{_libdir}/libsyslog-ng.so
%{_libdir}/libsyslog-ng-native-connector.a
%{_includedir}/syslog-ng
%exclude %{_includedir}/syslog-ng/libtest
%{_datadir}/syslog-ng/tools
%{_pkgconfigdir}/syslog-ng.pc
%{_pkgconfigdir}/syslog-ng-native-connector.pc

%if %{with tests}
%files test-devel
%defattr(644,root,root,755)
%if "%{_libdir}/syslog-ng" != "{moduledir}"
%dir %{_libdir}/syslog-ng
%endif
%dir %{_libdir}/syslog-ng/libtest
%{_libdir}/syslog-ng/libtest/libsyslog-ng-test.a
%{_includedir}/syslog-ng/libtest
%{_pkgconfigdir}/syslog-ng-test.pc
%endif
