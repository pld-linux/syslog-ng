#
# Conditional build:
%bcond_with	dynamic		# link dynamically with glib, eventlog, pcre, openssl
%bcond_without	sql		# build without support for logging to SQL DB
#
Summary:	Syslog-ng - new generation of the system logger
Summary(pl.UTF-8):	Syslog-ng - zamiennik syskloga
Summary(pt_BR.UTF-8):	Daemon de log nova geração
Name:		syslog-ng
Version:	3.0.1
Release:	5
License:	GPL v2
Group:		Daemons
Source0:	http://www.balabit.com/downloads/files/syslog-ng/sources/3.0.1/source/%{name}_%{version}.tar.gz
# Source0-md5:	14e13519bad47d0a6308905292385321
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Source4:	http://www.balabit.com/dl/guides/syslog-ng-v3.0-guide-admin-en.pdf
# Source4-md5:	d85266ac9155ad6df9844aadf830b379
Patch0:		%{name}-link.patch
Patch1:		%{name}-datadir.patch
Patch2:		%{name}-fixes.patch
URL:		http://www.balabit.com/products/syslog_ng/
BuildRequires:	autoconf >= 2.53
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.268
%if %{with dynamic}
BuildRequires:	eventlog-devel >= 0.2
BuildRequires:	glib2-devel >= 1:2.10.1
BuildRequires:	libcap-devel
%if %{with sql}
BuildRequires:	libdbi-devel >= 0.8.3-2
%endif
BuildRequires:	libnet-devel >= 1:1.1.2.1-3
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel >= 0.9.8
BuildRequires:	pcre-devel
%else
BuildRequires:	eventlog-static >= 0.2
BuildRequires:	glib2-static >= 1:2.2.0
BuildRequires:	glibc-static
BuildRequires:	libcap-static
%if %{with sql}
BuildRequires:	libdbi-static >= 0.8.3-2
%endif
BuildRequires:	libnet-static >= 1:1.1.2.1-3
BuildRequires:	libwrap-static
BuildRequires:	openssl-static >= 0.9.8
BuildRequires:	pcre-static
BuildRequires:	zlib-static
%endif
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires:	logrotate
Requires:	psmisc >= 20.1
Requires:	rc-scripts >= 0.2.0
Provides:	syslogdaemon
Conflicts:	klogd
Conflicts:	msyslog
Conflicts:	syslog
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

install %{SOURCE4} doc/

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--sysconfdir=%{_sysconfdir}/syslog-ng \
	--with-timezone-dir=%{_datadir}/zoneinfo \
	--with-pidfile-dir=/var/run \
	--enable-ssl \
	--enable-ipv6 \
	--enable-tcp-wrapper \
	--enable-spoof-source \
	--enable-linux-caps \
	--enable-pcre \
%if %{with sql}
	--enable-sql \
%endif
%if %{with dynamic}
	--enable-dynamic-linking
%endif

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,logrotate.d,rc.d/init.d},%{_sysconfdir}/syslog-ng} \
	$RPM_BUILD_ROOT/var/{log,lib/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/syslog-ng

for n in daemon debug iptables kernel lpr maillog messages secure spooler syslog user xferlog
do
	> $RPM_BUILD_ROOT/var/log/$n
done
touch $RPM_BUILD_ROOT/etc/sysconfig/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
for n in /var/log/{daemon,debug,iptables,kernel,lpr,maillog,messages,secure,spooler,syslog,user,xferlog}
do
	[ -f $n ] && continue
	touch $n
	chmod 640 $n
done

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
sed -i -e 's#match("IN\=\[A-Za-z0-9\]\* OUT=\[A-Za-z0-9\]\*");#match("IN=[A-Za-z0-9]* OUT=[A-Za-z0-9]*" value("MESSAGE"));#g' /etc/syslog-ng/syslog-ng.conf
sed -i -e "1 s#\(.*\)\$#@version: 3.0\n\1#g" /etc/syslog-ng/syslog-ng.conf
rm -f %{_var}/lib/%{name}/syslog-ng.persist
%service syslog-ng restart "syslog-ng daemon"
exit 0

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS debian/syslog-ng.conf* contrib/{relogger.pl,syslog-ng.vim}
%doc doc/examples/syslog-ng.conf.sample contrib/syslog-ng.conf.{doc,RedHat}
%doc contrib/{apparmor,selinux} doc/syslog-ng-v3.0-guide-admin-en.pdf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/syslog-ng
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%attr(755,root,root) %{_bindir}/loggen
%attr(755,root,root) %{_sbindir}/syslog-ng
%dir %{_var}/lib/%{name}
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*

%attr(640,root,root) %ghost /var/log/*
