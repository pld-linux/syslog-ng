Summary:	Syslog-ng - new generation of the system logger
Summary(pl):	Syslog-ng - zamiennik syskloga
Summary(pt_BR):	Daemon de log nova geração
Name:		syslog-ng
Version:	1.5.20
Release:	1
License:	GPL
Group:		Daemons
Source0:	http://www.balabit.hu/downloads/syslog-ng/1.5/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Patch0:		%{name}-ac25x.patch
URL:		http://www.balabit.hu/products/syslog-ng/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	flex
BuildRequires:	libol-static >= 0.3.3
PreReq:		rc-scripts >= 0.2.0
Requires(post,preun):	/sbin/chkconfig
Requires(post):	fileutils
Requires:	logrotate
Requires:	psmisc >= 20.1
Provides:	syslogdaemon
Obsoletes:	syslog
Obsoletes:	klogd
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

%build
rm -f missing
aclocal
%{__autoconf}
%{__automake}
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{logrotate.d,rc.d/init.d},%{_sysconfdir}/syslog-ng}
install -d $RPM_BUILD_ROOT/var/log/{mail,archiv}

%{__make} DESTDIR=$RPM_BUILD_ROOT install

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/syslog-ng/syslog-ng.conf
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/syslog-ng

> $RPM_BUILD_ROOT/var/log/syslog

%clean
rm -rf $RPM_BUILD_ROOT

%post
for n in /var/log/{cron,daemon,debug,kernel,lpr,maillog,messages,ppp,secure,spooler,syslog,user,mail/{info,warn,err}}
do
	[ -f $n ] && continue
	touch $n
	chmod 640 $n
done

/sbin/chkconfig --add syslog-ng
if [ -f /var/lock/subsys/syslog-ng ]; then
	/etc/rc.d/init.d/syslog-ng restart
else
	echo "Run \"/etc/rc.d/init.d/syslog-ng start\" to start syslog-ng daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/syslog-ng ]; then
		/etc/rc.d/init.d/syslog-ng stop
	fi
	/sbin/chkconfig --del syslog-ng
fi

%files
%defattr(644,root,root,755)
%doc doc/syslog-ng.conf.{demo,sample} doc/sgml/syslog-ng.txt*
%attr(750,root,root) %dir %{_sysconfdir}/syslog-ng
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/syslog-ng/syslog-ng.conf
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/syslog-ng
%attr(754,root,root) /etc/rc.d/init.d/syslog-ng
%attr(755,root,root) %{_sbindir}/syslog-ng
%{_mandir}/man[58]/*

%attr(640,root,root) %ghost /var/log/syslog
%dir /var/log/mail
%dir /var/log/archiv
