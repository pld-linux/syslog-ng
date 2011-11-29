#
# TODO:
# - relies on libs in /usr which is wrong
#   (well, for modules bringing additional functionality it's acceptable IMO --q)
# - use external libivykis [>= 0.18+syslog-ng updates]
#
# Conditional build:
%bcond_with	dynamic		# link dynamically with glib, eventlog, pcre (modules are always linked dynamically)
%if "%{pld_release}" == "ac"
%bcond_with	sql		# build with support for logging to SQL DB
%else
%bcond_without	sql		# build without support for logging to SQL DB
%endif
%bcond_without	tests

%if "%{pld_release}" == "ac"
%define		glib2_ver	1:2.16.0
%else
%define		glib2_ver	1:2.24.0
%endif
Summary:	Syslog-ng - new generation of the system logger
Summary(pl.UTF-8):	Syslog-ng - systemowy demon logujący nowej generacji
Summary(pt_BR.UTF-8):	Daemon de log nova geração
Name:		syslog-ng
Version:	3.3.1
Release:	5
License:	GPL v2+ with OpenSSL exception
Group:		Daemons
Source0:	http://www.balabit.com/downloads/files/syslog-ng/open-source-edition/%{version}/source/%{name}_%{version}.tar.gz
# Source0-md5:	a3dfe8a49aa8ce1aeb7e1ed5b11af378
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Source4:	http://www.balabit.com/support/documentation/syslog-ng-ose-v3.3-guide-admin-en.pdf
# Source4-md5:	bb23e36a8f44956858f2d622f9d1826d
Source5:	%{name}-simple.conf
Source6:	%{name}.upstart
Patch0:		%{name}-datadir.patch
Patch1:		cap_syslog-vserver-workaround.patch
Patch2:		%{name}-nolibs.patch
Patch3:		%{name}-systemd.patch
URL:		http://www.balabit.com/products/syslog_ng/
BuildRequires:	autoconf >= 2.53
BuildRequires:	automake
BuildRequires:	bison >= 2.4
BuildRequires:	eventlog-devel >= 0.2.12
BuildRequires:	flex
BuildRequires:	glib2-devel >= %{glib2_ver}
BuildRequires:	json-c-devel >= 0.7
BuildRequires:	libcap-devel
%{?with_sql:BuildRequires:	libdbi-devel >= 0.8.3-2}
BuildRequires:	libmongo-client-devel >= 0.1.0
BuildRequires:	libnet-devel >= 1:1.1.2.1-3
BuildRequires:	libtool >= 2:2.0
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel >= 0.9.8
BuildRequires:	pcre-devel >= 6.1
BuildRequires:	pkgconfig
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.561
BuildRequires:	which
%if %{with tests}
%{?with_sql:BuildRequires:	libdbi-drivers-sqlite3}
BuildRequires:	python
BuildRequires:	python-modules
BuildRequires:	tzdata
%endif
%if %{without dynamic}
BuildRequires:	eventlog-static >= 0.2.12
BuildRequires:	glib2-static >= %{glib2_ver}
BuildRequires:	pcre-static >= 6.1
BuildRequires:	zlib-static
%endif
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name}-libs = %{version}-%{release}
Requires:	eventlog >= 0.2.12
Requires:	glib2 >= %{glib2_ver}
Requires:	pcre >= 6.1
Requires:	psmisc >= 20.1
Requires:	rc-scripts >= 0.4.3.0
# for afsocket
Requires:	libnet >= 1:1.1.2.1-7
# for afsocket and dbparser
Requires:	openssl >= 0.9.8
Provides:	syslogdaemon
Obsoletes:	syslog-ng-module-afsocket
Obsoletes:	syslog-ng-module-dbparser
Conflicts:	klogd
Conflicts:	msyslog
Conflicts:	syslog
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# syslog-ng has really crazy linking rules (see their bugzilla).
# Some rules, according to syslog-ng devs, are like this:
# - libsyslog-ng.so has undefined symbols for third party libraries
#   and these symbols should go via main syslog-ng binary
# - same applies for modules
# In dynamic case tests are forcily linked with dynamic modules, which doesn't work with as-needed.
%define		filterout_ld			-Wl,--as-needed -Wl,--no-copy-dt-needed-entries
%if %{without dynamic}
%define		no_install_post_check_so	1
%define		_sbindir			/sbin
%define		_libdir				/%{_lib}
%endif

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

%package upstart
Summary:	Upstart job description for syslog-ng
Summary(pl.UTF-8):	Opis zadania Upstart dla demona syslog-ng
Group:		Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	upstart >= 0.6
Conflicts:	avahi-upstart < 0.6.30-2
Conflicts:	openssh-server-upstart < 2:5.8p2-2
Conflicts:	postgresql-upstart < 9.0.4-2

%description upstart
Upstart job description for syslog-ng.

%description upstart -l pl.UTF-8
Opis zadania Upstart dla demona syslog-ng.

%package module-afmongodb
Summary:	MongoDB destination support module for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi zapisu logów w bazie MongoDB
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libmongo-client >= 0.1.0

%description module-afmongodb
MongoDB destination support module for syslog-ng.

%description module-afmongodb -l pl.UTF-8
Moduł sysloga-ng do obsługi zapisu logów w bazie MongoDB.

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

%package module-tfjson
Summary:	JSON formatting template function for syslog-ng
Summary(pl.UTF-8):	Moduł sysloga-ng do obsługi szablonów z formatowaniem JSON
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	json-c >= 0.7

%description module-tfjson
JSON formatting template function for syslog-ng.

%description module-tfjson -l pl.UTF-8
Moduł sysloga-ng do obsługi szablonów z formatowaniem JSON.

%package libs
Summary:	Shared library for syslog-ng
Summary(pl.UTF-8):	Biblioteka współdzielona sysloga-ng
Group:		Libraries
%if %{with dynamic}
Requires:	eventlog >= 0.2.12
Requires:	glib2 >= %{glib2_ver}
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
Requires:	pcre-devel >= 6.1
%endif

%description devel
Header files for syslog-ng modules development.

%description devel -l pl.UTF-8
Pliki nagłówkowe do tworzenia modułów dla sysloga-ng.

%package systemd
Summary:	systemd units for syslog-ng
Group:		Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	systemd

%description systemd
systemd units for syslog-ng

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
cp -a %{SOURCE4} doc
cp -a %{SOURCE5} contrib/syslog-ng.conf.simple

%{__sed} -i -e 's|/usr/bin/awk|/bin/awk|' scl/syslogconf/convert-syslogconf.awk

%build
for i in . lib/ivykis; do
cd $i
	%{__libtoolize}
	%{__aclocal} -I m4
	%{__autoconf}
	%{__autoheader}
	%{__automake}
cd -
done
%configure \
	--sysconfdir=%{_sysconfdir}/syslog-ng \
	--datadir=%{_datadir}/syslog-ng \
	--with-default-modules=affile,afprog,afsocket,afuser,basicfuncs,csvparser,dbparser,syslogformat \
	--with-libmongo-client=system \
	--with-module-dir=%{_libdir}/syslog-ng \
	--with-pidfile-dir=/var/run \
	--with-timezone-dir=%{_datadir}/zoneinfo \
	--enable-systemd \
	--with-systemdsystemunitdir=/lib/systemd/system \
	--enable-ipv6 \
	--enable-linux-caps \
	--enable-pacct \
	--enable-pcre \
	--enable-spoof-source \
	--enable-ssl \
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
LD_LIBRARY_PATH=$PWD/lib/.libs \
%{__make} check
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{init,sysconfig,logrotate.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/patterndb.d \
	$RPM_BUILD_ROOT/var/{log,lib/%{name}/xsd}

%{__make} -j1 install \
	pkgconfigdir=%{_pkgconfigdir} \
	DESTDIR=$RPM_BUILD_ROOT

%{__sed} -e 's|@@SBINDIR@@|%{_sbindir}|g' %{SOURCE1} > $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
cp -a %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf
cp -a %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/syslog-ng

for n in daemon debug iptables kernel lpr maillog messages secure spooler syslog user xferlog; do
	> $RPM_BUILD_ROOT/var/log/$n
done
touch $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%{__rm} $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1}/loggen*
%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la
%{__rm} $RPM_BUILD_ROOT%{_libdir}/syslog-ng/*.la

%if "%{pld_release}" == "th"
%{__sed} -e 's|@@SBINDIR@@|%{_sbindir}|g' %{SOURCE6} > $RPM_BUILD_ROOT/etc/init/%{name}.conf
%endif

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

%preun
if [ "$1" = "0" ]; then
	%service syslog-ng stop
	/sbin/chkconfig --del syslog-ng
fi

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

%post upstart
%upstart_post %{name}

%postun upstart
%upstart_postun %{name}

%triggerun upstart -- syslog-ng-upstart < 3.2.4-3
#  use SERVICE_syslog=y in upstart job environment instead of SERVICE=syslog
%{__sed} -i -e 's,SERVICE=syslog,SERVICE_syslog=y,' /etc/init/*.conf || :

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS debian/syslog-ng.conf* contrib/relogger.pl
%doc contrib/syslog-ng.conf.{doc,simple,RedHat}
%doc contrib/{apparmor,selinux,syslog2ng} doc/syslog-ng-ose-v3.3-guide-admin-en.pdf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng/patterndb.d
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/modules.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/scl.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/syslog-ng
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%dir %{_libdir}/syslog-ng
%attr(755,root,root) %{_libdir}/syslog-ng/libaffile.so
%attr(755,root,root) %{_libdir}/syslog-ng/libafprog.so
%attr(755,root,root) %{_libdir}/syslog-ng/libafsocket.so
%attr(755,root,root) %{_libdir}/syslog-ng/libafsocket-notls.so
%attr(755,root,root) %{_libdir}/syslog-ng/libafsocket-tls.so
%attr(755,root,root) %{_libdir}/syslog-ng/libafuser.so
%attr(755,root,root) %{_libdir}/syslog-ng/libbasicfuncs.so
%attr(755,root,root) %{_libdir}/syslog-ng/libconfgen.so
%attr(755,root,root) %{_libdir}/syslog-ng/libconvertfuncs.so
%attr(755,root,root) %{_libdir}/syslog-ng/libcsvparser.so
%attr(755,root,root) %{_libdir}/syslog-ng/libdbparser.so
%attr(755,root,root) %{_libdir}/syslog-ng/libdummy.so
%attr(755,root,root) %{_libdir}/syslog-ng/libpacctformat.so
%attr(755,root,root) %{_libdir}/syslog-ng/libsyslog-ng-crypto.so
%attr(755,root,root) %{_libdir}/syslog-ng/libsyslogformat.so
%attr(755,root,root) %{_sbindir}/syslog-ng
%attr(755,root,root) %{_sbindir}/syslog-ng-ctl
%attr(755,root,root) %{_bindir}/pdbtool
%attr(755,root,root) %{_bindir}/update-patterndb

%dir %{_datadir}/syslog-ng/include
%dir %{_datadir}/syslog-ng/include/scl
%dir %{_datadir}/syslog-ng/include/scl/pacct
%{_datadir}/syslog-ng/include/scl/pacct/plugin.conf
%dir %{_datadir}/syslog-ng/include/scl/syslogconf
%{_datadir}/syslog-ng/include/scl/syslogconf/README
%attr(755,root,root) %{_datadir}/syslog-ng/include/scl/syslogconf/convert-syslogconf.awk
%{_datadir}/syslog-ng/include/scl/syslogconf/plugin.conf
%dir %{_datadir}/syslog-ng/include/scl/system
%attr(755,root,root) %{_datadir}/syslog-ng/include/scl/system/generate-system-source.sh
%{_datadir}/syslog-ng/include/scl/system/plugin.conf
%dir %{_datadir}/syslog-ng/xsd
%{_datadir}/syslog-ng/xsd/patterndb-*.xsd

%dir %{_var}/lib/%{name}
%dir %{_var}/lib/%{name}/xsd
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man1/syslog-ng-ctl.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*

%attr(640,root,root) %ghost /var/log/daemon
%attr(640,root,root) %ghost /var/log/debug
%attr(640,root,root) %ghost /var/log/iptables
%attr(640,root,root) %ghost /var/log/kernel
%attr(640,root,root) %ghost /var/log/lpr
%attr(640,root,root) %ghost /var/log/maillog
%attr(640,root,root) %ghost /var/log/messages
%attr(640,root,root) %ghost /var/log/secure
%attr(640,root,root) %ghost /var/log/spooler
%attr(640,root,root) %ghost /var/log/syslog
%attr(640,root,root) %ghost /var/log/user
%attr(640,root,root) %ghost /var/log/xferlog

%if "%{pld_release}" == "th"
%files upstart
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/init/%{name}.conf
%endif

%files module-afmongodb
%defattr(644,root,root,755)
%doc modules/afmongodb/TODO
%attr(755,root,root) %{_libdir}/syslog-ng/libafmongodb.so

%files module-afsql
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/syslog-ng/libafsql.so

%files module-tfjson
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/syslog-ng/libtfjson.so

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsyslog-ng-%{version}.so
%dir %{_datadir}/syslog-ng

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libsyslog-ng.so
%{_includedir}/syslog-ng
%{_datadir}/syslog-ng/tools
%{_pkgconfigdir}/syslog-ng.pc

%files systemd
%defattr(644,root,root,755)
/lib/systemd/system/syslog-ng.service
