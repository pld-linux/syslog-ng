Summary:	Syslog-ng - new generation fo the system logger
Summary(pl):	Syslog-ng - zamiennik sysklog'a
Name:		syslog-ng
Version:	1.4.3
Release:	2 
License:	GPL
Group:		Daemons
Group(pl):	Serwery
Source0:	http://www.balabit.hu//downloads/syslog-ng/source/%{name}-%{version}.tar.gz
Source1:	syslog-ng.init
Source2:	syslog-ng.conf
Patch0:		syslog-ng-autoconf.patch
BuildRequires:	libol-static >= 0.2.16
BuildRequires:	flex
Requires:	rc-scripts >= 0.2.0
Obsoletes:	syslog
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc

%description
syslog-ng is a syslogd replacement for unix and unix-like systems. It has
been tested on Solaris, BSDi and Linux, and were found to run reliably.
syslog-ng gives you a much enhanced configuration scheme, which lets you
filter messages based on not only priority/facility pairs, but also on
message content. You can use regexps to direct log stream to different
destinations. A destination can be anything from a simple file to a network
connection. syslog-ng supports TCP logforwarding, together with hashing to
prevent unauthorized modification on the line.

%description -l pl
Syslog-ng jest zamiennikiem dla standartowo u¿ywanych programów typu
sysklog Dzia³a w systemie SunON, BSD, Linux. Daje znacznie wiêksze
mo¿liwosci logowanie i kontrolowanie zbieranych informacji.

%prep
%setup -q
%patch -p1

%build
aclocal
autoconf
LDFLAGS="-s"; export LDFLAGS
%configure
make

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/syslog-ng} \
	$RPM_BUILD_ROOT/var/log/news

make DESTDIR=$RPM_BUILD_ROOT install

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf

gzip -9nf doc/syslog-ng.conf.{demo,sample} doc/sgml/syslog-ng.txt \
	$RPM_BUILD_ROOT%{_mandir}/man[58]/*

touch $RPM_BUILD_ROOT/var/log/syslog

%post
for n in /var/log/{auth.log,syslog,cron.log,daemon.log,kern.log,lpr.log,user.log,uucp.log,ppp.log,mail.log,mail.info,mail.warn,mail.err,debug,messages}
do
	[ -f $n ] && continue
	touch $n
	chmod 640 $n
done

/sbin/chkconfig --add syslog-ng
if [ -f /var/lock/subsys/ ]; then
	/etc/rc.d/init.d/syslog restart &>/dev/null
else
	echo "Run \"/etc/rc.d/init.d/syslog-ng start\" to start syslog-ng daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ ]; then
		/etc/rc.d/init.d/syslog-ng stop >&2
	fi
	/sbin/chkconfig --del syslog-ng
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc doc/*.gz doc/sgml/syslog-ng.txt*
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(640,root,root) %config %verify(not size mtime md5) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%attr(755,root,root) %{_sbindir}/syslog-ng

%{_mandir}/man[58]/*
%attr(640,root,root) %config(noreplace) %verify(not mtime md5 size) /var/log/*
