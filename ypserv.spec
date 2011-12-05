%define initdir /etc/rc.d/init.d

Summary: The NIS (Network Information Service) server
Url: http://www.linux-nis.org/nis/ypserv/index.html
Name: ypserv
Version: 2.19
Release: 18%{?dist}
License: GPLv2
Group: System Environment/Daemons
Source0: ftp://ftp.kernel.org/pub/linux/utils/net/NIS/ypserv-%{version}.tar.bz2
Source1: ypserv-ypserv.init
Source2: ypserv-yppasswdd.init
Source3: ypserv-ypxfrd.init

Requires: gawk, make, portmap, bash >= 2.0
Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts
Requires(postun): initscripts

Patch0: ypserv-2.5-redhat.patch
Patch1: ypserv-2.11-path.patch
Patch2: ypserv-2.5-nfsnobody2.patch
Patch3: ypserv-2.11-nomap.patch
Patch4: ypserv-2.11-iface-binding3.patch
Patch6: ypserv-2.13-yplib-memleak.patch
Patch7: ypserv-2.13-ypxfr-zeroresp.patch
Patch8: ypserv-2.19-inval-ports.patch
Patch9: ypserv-2.13-nonedomain.patch
Patch10: ypserv-2.19-quieter.patch
Patch11: ypserv-2.19-debuginfo.patch
Patch12: ypserv-2.19-slp-warning.patch
# Modifies rpc.ypxfrd to create pidfile.
Patch13: ypserv-2.19-pidfile.patch
Patch14: ypserv-2.19-nodbclose.patch
Obsoletes: yppasswd
BuildRequires: gdbm-devel
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
The Network Information Service (NIS) is a system that provides
network information (login names, passwords, home directories, group
information) to all of the machines on a network. NIS can allow users
to log in on any machine on the network, as long as the machine has
the NIS client programs running and the user's password is recorded in
the NIS passwd database. NIS was formerly known as Sun Yellow Pages
(YP).

This package provides the NIS server, which will need to be running on
your network. NIS clients do not need to be running the server.

Install ypserv if you need an NIS server for your network. You also
need to install the yp-tools and ypbind packages on any NIS client
machines.

%prep
%setup -q
%patch0 -p1 -b .redhat
%patch1 -p1 -b .path
%patch2 -p1 -b .nfsnobody
%patch3 -p1 -b .nomap
%patch4 -p1 -b .iface
%patch6 -p1 -b .memleak
%patch7 -p1 -b .respzero
%patch8 -p1 -b .ports
%patch9 -p1 -b .nonedomain
%patch10 -p1 -b .quieter
%patch11 -p1 -b .debuginfo
%patch12 -p1 -b .slp-warning
%patch13 -p1 -b .pidfile
%patch14 -p1 -b .nodbclose

%build
cp etc/README etc/README.etc
%ifarch s390 s390x
export CFLAGS="$RPM_OPT_FLAGS -fPIC"
%else
export CFLAGS="$RPM_OPT_FLAGS -fpic"
%endif
%configure --enable-checkroot --enable-fqdn --libexecdir=%{_libdir}/yp
make

%install
rm -rf $RPM_BUILD_ROOT

#make install ROOT=$RPM_BUILD_ROOT 
%makeinstall libexecdir=$RPM_BUILD_ROOT%{_libdir}/yp INSTALL_PROGRAM=install
mkdir -p $RPM_BUILD_ROOT%{initdir}
install -m644 etc/ypserv.conf $RPM_BUILD_ROOT%{_sysconfdir}
install -m755 %{SOURCE1} $RPM_BUILD_ROOT%{initdir}/ypserv
install -m755 %{SOURCE2} $RPM_BUILD_ROOT%{initdir}/yppasswdd
install -m755 %{SOURCE3} $RPM_BUILD_ROOT%{initdir}/ypxfrd

mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
cat >$RPM_BUILD_ROOT/etc/sysconfig/yppasswdd <<EOF
# The passwd and shadow files are located under the specified
# directory path. rpc.yppasswdd will use these files, not /etc/passwd
# and /etc/shadow.
#ETCDIR=/etc

# This options tells rpc.yppasswdd to use a different source file
# instead of /etc/passwd
# You can't mix usage of this with ETCDIR
#PASSWDFILE=/etc/passwd

# This  options  tells rpc.yppasswdd to use a different source file
# instead of /etc/passwd. 
# You can't mix usage of this with ETCDIR
#SHADOWFILE=/etc/shadow

# Additional arguments passed to yppasswd
YPPASSWDD_ARGS=
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add ypserv
/sbin/chkconfig --add yppasswdd
/sbin/chkconfig --add ypxfrd

%preun
if [ $1 = 0 ]; then
	/sbin/service ypserv stop > /dev/null 2>&1
	/sbin/chkconfig --del ypserv
	/sbin/service yppasswdd stop > /dev/null 2>&1
	/sbin/chkconfig --del yppasswdd
	/sbin/service ypxfrd stop > /dev/null 2>&1
	/sbin/chkconfig --del ypxfrd
fi

%postun
if [ "$1" -ge "1" ]; then
	/sbin/service ypserv condrestart > /dev/null 2>&1
	/sbin/service yppasswdd condrestart > /dev/null 2>&1
	/sbin/service ypxfrd condrestart > /dev/null 2>&1
fi
exit 0
 
%files
%defattr(-,root,root)
%doc AUTHORS README INSTALL ChangeLog TODO NEWS COPYING
%doc etc/ypserv.conf etc/securenets etc/README.etc
%doc etc/netgroup etc/locale etc/netmasks etc/timezone
%config(noreplace) %{_sysconfdir}/ypserv.conf
%config(noreplace) %{_sysconfdir}/sysconfig/yppasswdd
%config(noreplace) /var/yp/*
%dir /var/yp
%config %{initdir}/*
%{_libdir}/yp
%{_sbindir}/*
%{_mandir}/*/*
%{_includedir}/*/*

%changelog
* Thu May 13 2010 Karel Klic <kklic@redhat.com> - 2.19-18
- Rebuild to generate correct dwarf cfi data
  Resolves: #589918

* Fri Feb 26 2010 Karel Klic <kklic@redhat.com> - 2.19-17
- Added COPYING file to the package

* Thu Jan 28 2010 Karel Klic <kklic@redhat.com> - 2.19-16
- Added patch removing invalid ypdb_close call
  Resolves: #559608

* Thu Jan 21 2010 Karel Klic <kklic@redhat.com> - 2.19-15
- Added patch for rpc.ypxfrd to create a pid file
- Rewrote initscripts to become closer to Packaging:SysVInitScript
  Fedora guildeline
- Fixed initscript for ypserv (bug 523438)
- Fixed initscript for yppasswdd (bug 523394)
- Fixed initscript for ypxfrd (bug 523397)

* Thu Jan  7 2010 Karel Klic <kklic@redhat.com> - 2.19-14
- Removed Prereq use in the spec file
- Removed usage of RPM_SOURCE_DIR from the spec file
- Removed --enable-yppasswd from configure, as this option
  is ignored

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 2.19-13.1
- Rebuilt for RHEL 6

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.19-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Mar  3 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.19-12
- Mark apropriate config files as noreplace

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.19-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Sep 25 2008 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.19-10
- Rediff all patches to work with patch --fuzz=0

* Wed Feb 13 2008 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.19-9
- Mark /var/yp/Makefile as %%config(noreplace)
  Resolves: #432582
- Comment "slp" part of ypserv.conf to avoid ypserv warnings
  Resolves: #154806
- Spec file cleanup - remove period from end of Summary,
  fix license, remove macros from Changelog

* Mon Feb  4 2008 Vitezslav Crhonek <vcrhonek@redhat.com> - 2.19-8
- Fix Buildroot
- Fix /var/yp/Makefile
  Resolves: #431008

* Tue Jan  8 2008 Steve Dickson <steved@redhat.com> 2.19-7
- Changed Makefiles.in so binaries are not stripped.

* Sat Sep 15 2007 Steve Dickson <steved@redhat.com> 2.19-6
- Fixed init scripts to return correct exit code on
 'service status' (bz 248097)

* Tue Jul 31 2007 Steve Dickson <steved@redhat.com> 2.19-5
- Changed install process to create an useful debuginfo package (bz 249961)

* Fri Dec 22 2006 Steve Dickson <steved@redhat.com> - 2.19-4
- Made ypserver less verbose on common errors (bz #199236)
- Don't allow a make for empty domainname's or domainname's set to (none)
  (bz #197646)

* Wed Sep 13 2006 Steve Dickson <steved@redhat.com> - 2.19-3
- Added range checks to port values given on command line 
  (bz 205354)

* Tue Jul 25 2006 Steve Dickson <steved@redhat.com> - 2.19-2
- fixed typo in ypxfrd initscript (bz 185403)

* Fri Jul 14 2006 Jesse Keating <jkeating@redhat.com> - 2.19-1
- rebuild

* Mon Feb 13 2006 Chris Feist <cfeist@redhat.com> - 2.19-0
- Rebuilt against latest upstream sources (2.19).

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13-10.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13-10.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan  9 2006 Chris Feist <cfeist@redhat.com> - 2.13-10
- Fix crash with ypxfr caused by failing to zero out data (bz #161217)

* Wed Jan  4 2006 Jesse Keating <jkeating@redhat.com> - 2.13-6.2
- rebuilt for new gcc

* Thu Oct 14 2004 Miloslav Trmac <mitr@redhat.com> - 2.13-5
- Fix crash with -p (#134910, #129676)

* Tue Aug 31 2004 Steve Dickson <SteveD@RedHat.com>
- Zeroed out the ypxfr response buffer so allocated memory
  is not freed with the transfer fails

* Sat Jun 19 2004 Steve Dickson <SteveD@RedHat.com>
- Closed a memory leak in GDBM database routines (bz 120980)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon May 17 2004 Thomas Woerner <twoerner@redhat.com> 2.13-1
- compiling rpc.yppasswdd, rpc.ypxfrd, yppush and ypserv PIE

* Fri Apr 16 2004 Steve Dickson <SteveD@RedHat.com>
- Updated to 2.13

* Fri Apr  2 2004 Steve Dickson <SteveD@RedHat.com>
- Change ypMakefile to create services.byservicename
  maps correctly

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 24 2004 Phil Knirsch <pknirsch@redhat.com> 2.12.1-1
- Updated to latest upstream version.

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jan 19 2004 Phil Knirsch <pknirsch@redhat.com> 2.11-1
- Updated to latest upstream version.
- Dropped ypserv-2.8-echild.patch (not needed anymore).
- Fixed several other patches for new version.

* Mon Sep 15 2003 Steve Dickson <SteveD@RedHat.com>
- updated Release number for QU1

* Mon Sep 15 2003 Steve Dickson <SteveD@RedHat.com>
- Recompiled for AS2.1

* Wed Sep 10 2003 Steve Dickson <SteveD@RedHat.com>
- Added the --iface flag.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Apr 24 2003 Steve Dickson <SteveD@RedHat.com>
- Update to 2.8

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Nov  5 2002 Alexander Larsson <alexl@redhat.com> 2.6-1
- Updated to 2.6, allows you to disable db caching, bug #76618

* Mon Oct  7 2002 Alexander Larsson <alexl@redhat.com> 2.5-2
- Added comments to nfsnobody patch
- Corrected URL
- fixed missing %%doc file, bug #74060

* Thu Aug 15 2002 Alexander Larsson <alexl@redhat.com> 2.5-1
- Update to 2.5, fixes memleak
- remove manpage patch since it was already fixed upstream

* Thu Aug 15 2002 Alexander Larsson <alexl@redhat.com>
- Fix ypserv.conf manpage, bug #69785
- Don't leak nfsnobody into nfs maps, bug #71515

* Thu Aug  8 2002 Alexander Larsson <alexl@redhat.com> 2.3-3
- Remove old broken triggers that are not needed anymore. Fixes #70612

* Fri Jun 21 2002 Tim Powers <timp@redhat.com> 2.3-2
- automated rebuild

* Tue Jun 11 2002 Alex Larsson <alexl@redhat.com> 2.3-1
- Updated to 2.3 from upstream.
- Removed patches that went in upstream.

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Apr 16 2002 Alex Larsson <alexl@redhat.com> 2.2-9
- Removed my ypserv-2.2-services patch. According to thorsten
  (yp maintainer) the key in services.byname actually
  SHOULD be port/protocol.

* Mon Apr  8 2002 Alex Larsson <alexl@redhat.com> 2.2-8
- Change the yppush patch to the patch from thorsten.

* Fri Apr  5 2002 Alex Larsson <alexl@redhat.com> 2.2-7
- Added patch to fix yppush timeout errors (#62429)

* Wed Mar 27 2002 Alex Larsson <alexl@redhat.com> 2.2-6
- Make yppasswdd source /etc/sysconf/yppasswd for options (#52253) 

* Mon Mar 25 2002 Alex Larsson <alexl@redhat.com> 2.2-5
- Add patch that fixes generation of services.byname. (#41851)
- Actually apply patch #5, seems like it got left out by misstake

* Fri Mar 22 2002 Alex Larsson <alexl@redhat.com> 2.2-4
- Changed Copyright from GNU to GPL

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sat Dec 08 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- fix restart initscript option #57129
- add a "gawk" requires #57002
- fix printcap bug #56993
- fix ypxfrd init script #55234

* Wed Dec 05 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 2.2 plus first official bug-fix

* Sat Nov 17 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to version 2.1, adjust all patches

* Mon Aug 27 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- set domainname if it is not yet set #52514

* Tue Jul 24 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add gdbm-devel BuildReq #49767
- add ypxfrd init script #44845
- fix #44805
- fix #20042, adding option to yppasswdd startup
- own /var/yp

* Mon Jul  9 2001 Tim Powers <timp@redhat.com>
- added reload entry to initscript (same as restart)

* Fri Jun 29 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.3.12

* Wed Mar 28 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- do not require tcp_wrappers anymore

* Thu Mar 15 2001 Philipp Knirsch <pknirsch@redhat.com>
- Added missing make requirement

* Tue Feb 27 2001 Preston Brown <pbrown@redhat.com>
- don't own dir /var/yp

* Wed Jan 24 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- prepare for startup script translation

* Thu Jan 11 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Start after netfs (#23527)

* Wed Aug 16 2000 Than Ngo <than@redhat.com>
- fix typo in startup script (Bug #15999)

* Wed Jul 19 2000 Than Ngo <than@redhat.de>
- inits back to rc.d/init.d, using service
- fix initscript again

* Mon Jul 17 2000 Bill Nottingham <notting@redhat.com>
- move initscript back
- fix format syslog bug

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Fri Jul  7 2000 Florian La Roche <Florian.LaRoche@redhat.de>
- prereq /etc/init.d

* Tue Jun 27 2000 Than Ngo <than@redhat.de>
- /etc/rc.d/init.d -> /etc/init.d
- fix initscript

* Sun Jun 18 2000 Than Ngo <than@redhat.de>
- FHS fixes,
- fix docdir

* Fri May 19 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- disable "netgrp" target in default all: (/var/yp/Makefile)

* Thu May 18 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- update to 1.3.11

* Mon Mar 06 2000 Cristian Gafton <gafton@redhat.com>
- add patch to avoid potential deadlock on the server (fix #9968)

* Wed Feb  2 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- fix typo in %%triggerpostun

* Mon Oct 25 1999 Bill Nottingham <notting@redhat.com>
- update to 1.3.9
- use gdbm, move back to /usr/sbin

* Tue Aug 17 1999 Bill Nottingham <notting@redhat.com>
- initscript munging
- ypserv goes on root partition

* Fri Aug 13 1999 Cristian Gafton <gafton@redhat.com>
- version 1.3.7

* Thu Jul  1 1999 Bill Nottingham <notting@redhat.com>
- start after network FS

* Tue Jun  1 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.3.6.94.

* Sun May 30 1999 Jeff Johnson <jbj@redhat.com>
- improved daemonization.

* Sat May 29 1999 Jeff Johnson <jbj@redhat.com>
- fix buffer overflow in rpc.yppasswd (#3126).

* Fri May 28 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.3.6.92.

* Fri Mar 26 1999 Cristian Gafton <gafton@redhat.com>
- version 1.3.6.91

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 4)

* Mon Feb  8 1999 Bill Nottingham <notting@redhat.com>
- move to start before ypbind

* Thu Dec 17 1998 Cristian Gafton <gafton@redhat.com>
- build for glibc 2.1
- upgraded to 1.3.5

* Tue Aug  4 1998 Jeff Johnson <jbj@redhat.com>
- yppasswd.init: lock file must have same name as init.d script, not daemon

* Sat Jul 11 1998 Cristian Gafton <gafton@redhat.com>
- upgraded to 1.3.4
- fixed the fubared Makefile
- link against gdbm instead of ndbm (it seems to work better)

* Sat May 02 1998 Cristian Gafton <gafton@redhat.com>
- upgraded to 1.3.1
- enhanced init scripts

* Fri May 01 1998 Jeff Johnson <jbj@redhat.com>
- added triggerpostun
- Use libdb fro dbp_*().

* Fri Apr 24 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Mon Apr 13 1998 Cristian Gafton <gafton@redhat.com>
- updated to 1.3.0

* Wed Dec 03 1997 Cristian Gafton <gafton@redhat.com>
- updated to 1.2.5
- added buildroot; updated spec file
- added yppasswdd init file

* Tue Nov 04 1997 Erik Troan <ewt@redhat.com>
- init script shouldn't set the domain name

* Tue Oct 14 1997 Erik Troan <ewt@redhat.com>
- supports chkconfig
- updated initscript for status and restart
- turned off in all runlevels, by default
- removed postinstall script which didn't do anything

* Thu Oct 09 1997 Erik Troan <ewt@redhat.com>
- added patch to build against later glibc

* Mon Jul 21 1997 Erik Troan <ewt@redhat.com>
- built against glibc

* Wed Apr 23 1997 Erik Troan <ewt@redhat.com>
- updated to 1.1.7.

* Fri Mar 14 1997 Erik Troan <ewt@redhat.com>
- Updated to ypserv 1.1.5, ported to Alpha (glibc).

* Fri Mar 07 1997 Erik Troan <ewt@redhat.com>
- Removed -pedantic which confuses the SPARC :-(
