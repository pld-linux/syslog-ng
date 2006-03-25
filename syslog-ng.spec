#
# Conditional build:
%bcond_with	dynamic		# link dynamically with glib and eventlog
#
%define		mainver		1.9
%define		minorver	9

Summary:	Syslog-ng - new generation of the system logger
Summary(pl):	Syslog-ng - zamiennik syskloga
Summary(pt_BR):	Daemon de log nova geração
Name:		syslog-ng
Version:	%{mainver}.%{minorver}
Release:	2
License:	GPL
Group:		Daemons
Source0:	http://www.balabit.com/downloads/syslog-ng/%{mainver}/src/%{name}-%{version}.tar.gz
# Source0-md5:	76dfb7ea910d1b033031aca2f40bf723
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Patch0:		%{name}-link.patch
Patch1:		%{name}-level.patch
URL:		http://www.balabit.com/products/syslog_ng/
BuildRequires:	autoconf >= 2.53
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libwrap-devel
BuildRequires:	rpmbuild(macros) >= 1.268
%if %{with dynamic}
BuildRequires:	eventlog-devel
BuildRequires:	glib2-devel >= 2.0.0
%else
BuildRequires:	eventlog-static
BuildRequires:	glib2-static >= 2.0.0
%endif
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires:	logrotate
Requires:	psmisc >= 20.1
Requires:	rc-scripts >= 0.2.0
Provides:	syslogdaemon
Obsoletes:	klogd
Obsoletes:	msyslog
Obsoletes:	syslog
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
syslog-ng is a syslogd replacement for unix and unix-like systems. It
has been tested on Solaris, BSDi and Linux, and were found to run
reliably. syslog-ng gives you a much enhanced configuration scheme,
which lets you filter messages based on not only priority/facility
pairs, but also on message content. You can use regexps to direct log
stream to different destinations. A destination can be anything from a
simple file to a network connection. syslog-ng supports TCP
logforwarding, together with hashing to prevent unauthorized
modification on the line.

%description -l pl
Syslog-ng jest zamiennikiem dla standardowo u¿ywanych programów typu
sysklog. Dzia³a w systemie SunOS, BSD, Linux. Daje znacznie wiêksze
mo¿liwo¶ci logowania i kontrolowania zbieranych informacji.

%description -l pt_BR
Syslog-ng é um substituto para o syslog tradicional, mas com diversas
melhorias, como, por exemplo, a habilidade de filtrar mensagens de log
por seu conteúdo (usando expressões regulares) e não apenas pelo par
facility/prioridade como o syslog original.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--sysconfdir=%{_sysconfdir}/syslog-ng \
%if %{with dynamic}
	--enable-dynamic-linking
%endif

%{__make}

tar zxvf doc/reference/syslog-ng.html.tar.gz

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{logrotate.d,rc.d/init.d},%{_sysconfdir}/syslog-ng} \
	$RPM_BUILD_ROOT/var/log/

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/syslog-ng

for n in debug kernel maillog messages secure syslog user spooler lpr daemon
do
	> $RPM_BUILD_ROOT/var/log/$n
done

%clean
rm -rf $RPM_BUILD_ROOT

%post
for n in /var/log/{cron,daemon,debug,kernel,lpr,maillog,messages,ppp,secure,spooler,syslog,user}
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

%files
%defattr(644,root,root,755)
%doc doc/examples/syslog-ng.conf.sample doc/reference/syslog-ng.txt* contrib/syslog-ng.conf.{doc,RedHat}
%doc syslog-ng.html/*
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/syslog-ng
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%attr(755,root,root) %{_sbindir}/syslog-ng
%{_mandir}/man[58]/*

%attr(640,root,root) %ghost /var/log/*
