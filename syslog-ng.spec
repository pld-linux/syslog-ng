Summary:	Syslog-ng - new generation fo the system logger
Summary(pl):	Syslog-ng - zamiennik sysklog'a
Name:		syslog-ng
Version:	1.1.28
Release:	1 
Copyright:	GPL
Group:		Daemons
Group(pl):	Demony
#http:		www.balabit.hu
#path:		/downloads/syslog-ng/source
Source0:	%name-%version.tar.gz
Source1:	syslog-ng
Source2:	syslog-ng.conf
BuildRequires:	libol >= 0.2
Requires:	rc-scripts
Obsolotes:	syslog
Buildroot:	/tmp/%{name}-%{version}-root

%define	_prefix	/usr

%description
syslog-ng is a syslogd replacement for unix and unix-like systems. 
It has been tested on Solaris, BSDi and Linux, and were found to run reliably. 

syslog-ng gives you a much enhanced configuration scheme, which lets you filter 
messages based on not only priority/facility pairs, but also on message content. 
You can use regexps to direct log stream to different destinations. 
A destination can be anything from a simple file to a network connection. 
syslog-ng supports TCP logforwarding, together with hashing to prevent unauthorized 
modification on the line.

%description -l pl
Syslog-ng jest zamiennikiem dla standartowo u¿ywanych programów typu sysklog
Dzia³a w systemie SunON, BSD, Linux.

Daje znacznie wiêksze mo¿liwosci logowanie i kontrolowanie zbieranych informacji.

%prep
%setup -q

%build
autoconf
./configure --prefix=%{_prefix}
make RPM_OPT_FLAGS="$RPM_OPT_FLAGS"
make dvi
make info

%install

rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/{syslog-ng,rc.d/init.d}

install -d $RPM_BUILD_ROOT/var/log/news

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/syslog-ng

install %{SOURCE2} $RPM_BUILD_ROOT/etc/syslog-ng

make prefix=$RPM_BUILD_ROOT/usr install

bzip2 -9 doc/syslog-ng.conf.demo
bzip2 -9 doc/syslog-ng.conf.sample
bzip2 -9 doc/*.ps
bzip2 -9 $RPM_BUILD_ROOT%{_mandir}/man[58]/*

touch $RPM_BUILD_ROOT/var/log/syslog

%post
for n in /var/log/{auth.log,syslog,cron.log,daemon.log,kern.log,lpr.log,user.log,uucp.log,ppp.log,mail.log,mail.info,mail.warn,mail.err,debug,messages}
do
	[ -f $n ] && continue
	touch &n
	chmod 640 &n
done

/sbin/checkconfig --add syslog
if [ -f /var/lock/subsys/ ]; then
	/etc/rc.d/init.d/syslog restart &>/dev/null
else
	echo "Run \"/etc/rc.d/init.d/syslog start\" to start syslog-ng daemon."
fi

%preun
if [ "$1" = "0" ]; then
	/etc/rc.d/init.d/syslog stop >&2
	/sbin/checkconfig --del syslog
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644, root, root, 755)
%doc doc/*.bz2 doc/syslog-ng.html.tar.gz

%attr(640,root,root) %config %verify(not size mtime md5)/etc/syslog-ng/syslog-ng.conf

%attr(755,root,root) /etc/rc.d/init.d/syslog

%attr(755,root,root) %{_sbindir}/syslog-ng

%attr(644,root,root) %{_mandir}/man5/syslog-ng.conf.5.bz2
%attr(644,root,root) %{_mandir}/man8/syslog-ng.8.bz2

%attr(640,root,root) %config(noreplace) %verify(not mtime md5 size) /var/log/*

%changelog
* Tue Jul 20 1999 Wojciech "Sas" Ciêciwa <cieciwa@alpha.zarz.agh.edu.pl>
  [1.1.27-1]
- update to last version.

* Tue May  4 1999 Wojciech "Sas" Ciêciwa <cieciwa@alpha.zarz.agh.edu.pl>
- building RPM.
