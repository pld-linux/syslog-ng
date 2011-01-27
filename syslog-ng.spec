#
# Conditional build:
%bcond_with	dynamic		# link dynamically with glib, eventlog, pcre, openssl
%if "%{pld_release}" == "ac"
%bcond_with		sql		# build with support for logging to SQL DB
%else
%bcond_without	sql		# build without support for logging to SQL DB
%endif
%bcond_without	tests

%if "%{pld_release}" == "ac"
%define		glib2_ver	2.16.0
%else
%define		glib2_ver	2.24.0
%endif
Summary:	Syslog-ng - new generation of the system logger
Summary(pl.UTF-8):	Syslog-ng - zamiennik syskloga
Summary(pt_BR.UTF-8):	Daemon de log nova geração
Name:		syslog-ng
Version:	3.2.2
Release:	0.1
License:	GPL v2
Group:		Daemons
Source0:	http://www.balabit.com/downloads/files/syslog-ng/sources/%{version}/source/%{name}_%{version}.tar.gz
# Source0-md5:	ed8ebe559d52a63fb61e3e2db566643f
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Source4:	http://www.balabit.com/dl/guides/%{name}-v3.0-guide-admin-en.pdf
# Source4-md5:	882f77ad2673e6490099b5393fe26796
Source5:	%{name}-simple.conf
Source6:	%{name}.upstart
Patch0:		%{name}-link.patch
Patch1:		%{name}-datadir.patch
Patch2:		%{name}-pyssl.patch
URL:		http://www.balabit.com/products/syslog_ng/
BuildRequires:	autoconf >= 2.53
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
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
%if %{with dynamic}
BuildRequires:	eventlog-devel >= 0.2
BuildRequires:	glib2-devel >= 1:%{glib2_ver}
BuildRequires:	libcap-devel
%{?with_sql:BuildRequires:	libdbi-devel >= 0.8.3-2}
BuildRequires:	libnet-devel >= 1:1.1.2.1-3
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel
%else
BuildRequires:	eventlog-static >= 0.2
BuildRequires:	glib2-static >= 1:%{glib2_ver}
BuildRequires:	glibc-static
BuildRequires:	libcap-static
%{?with_sql:BuildRequires:	libdbi-static >= 0.8.3-2}
BuildRequires:	libnet-static >= 1:1.1.2.1-3
BuildRequires:	libwrap-static
BuildRequires:	openssl-static
BuildRequires:	pcre-static
BuildRequires:	zlib-static
%endif
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires:	glib2 >= 1:%{glib2_ver}
Requires:	psmisc >= 20.1
Requires:	rc-scripts >= 0.4.3.0
Provides:	syslogdaemon
Conflicts:	klogd
Conflicts:	msyslog
Conflicts:	syslog
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
Summary(pl.UTF-8):	Opis zadania Upstart dla syslog-ng
Group:		Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	upstart >= 0.6

%description upstart
Upstart job description for syslog-ng.

%description upstart -l pl.UTF-8
Opis zadania Upstart dla syslog-ng.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
cp -a %{SOURCE4} doc
cp -a %{SOURCE5} contrib/syslog-ng.conf.simple

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__automake}
%configure \
	--sysconfdir=%{_sysconfdir}/syslog-ng \
	--datadir=%{_datadir}/syslog-ng \
	--with-module-dir=%{_libdir}/syslog-ng \
	--with-timezone-dir=%{_datadir}/zoneinfo \
	--with-pidfile-dir=/var/run \
	--enable-ssl \
	--enable-ipv6 \
	--enable-tcp-wrapper \
	--enable-spoof-source \
	--enable-linux-caps \
	--enable-pcre \
	--enable-pacct \
%if %{with sql}
	--enable-sql \
%endif
%if %{with dynamic}
	--enable-dynamic-linking
%else
	--enable-mixed-linking
%endif

%{__make}

%{?with_tests:%{__make} check}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{init,sysconfig,logrotate.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/patterndb.d \
	$RPM_BUILD_ROOT/var/{log,lib/%{name}}

%{__make} -j1 install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
cp -a %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf
cp -a %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/syslog-ng

for n in daemon debug iptables kernel lpr maillog messages secure spooler syslog user xferlog; do
	> $RPM_BUILD_ROOT/var/log/$n
done
touch $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%{__rm} $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1}/loggen*
%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.{so,la}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/syslog-ng/*.la

%if "%{pld_release}" == "th"
cp -a %{SOURCE6} $RPM_BUILD_ROOT/etc/init/%{name}.conf
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
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

%postun -p /sbin/ldconfig

%post upstart
%upstart_post %{name}

%postun upstart
%upstart_postun %{name}

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

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS debian/syslog-ng.conf* contrib/relogger.pl
%doc doc/examples/syslog-ng.conf.sample contrib/syslog-ng.conf.{doc,simple,RedHat}
%doc contrib/{apparmor,selinux,syslog2ng} doc/syslog-ng-v3.0-guide-admin-en.pdf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng/patterndb.d
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/modules.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/scl.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/syslog-ng
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%attr(755,root,root) %{_libdir}/libsyslog-ng.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libsyslog-ng.so.0
%attr(755,root,root) %{_libdir}/libsyslog-ng-patterndb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libsyslog-ng-patterndb.so.0
%dir %{_libdir}/syslog-ng
%attr(755,root,root) %{_libdir}/syslog-ng/lib*.so
%attr(755,root,root) %{_sbindir}/syslog-ng
%attr(755,root,root) %{_sbindir}/syslog-ng-ctl
%attr(755,root,root) %{_bindir}/pdbtool
%attr(755,root,root) %{_bindir}/update-patterndb
%dir %{_var}/lib/%{name}
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man1/syslog-ng-ctl.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*

%attr(640,root,root) %ghost /var/log/*

%if "%{pld_release}" == "th"
%files upstart
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/init/%{name}.conf
%endif
