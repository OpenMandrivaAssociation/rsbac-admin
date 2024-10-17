%define	lib_name_orig lib%{fname}
%define	librsbac_major 1
%define	lib_name %mklibname %{fname} %{librsbac_major}
%define nss_name nss_rsbac
%define libnss_name_orig lib%{nss_name}
%define libnss_major 2
%define	libnss_name %mklibname %{nss_name} %{libnss_major}
%define	fname	rsbac

Name:		rsbac-admin
Epoch:		2
Version:	1.4.6
Release:	3
Summary:	A set of RSBAC utilities
License:	GPL
Group:		System/Configuration/Other
Url:		https://www.rsbac.org
Source0:	http://download.rsbac.org/code/%{version}/%{name}-%{version}.tar.bz2
Source1:	rklogd.init
Source2:	rklogd.conf
Source3:	update_urpmi
Requires:	dialog
BuildRequires:	libtool pam-devel ncurses-devel
Obsoletes:	%{name}-doc
Provides:	%{name}-doc
# MD these are competitive virtual provides
# maybe some other virtual provides should be thought of
#Provides:	passwd, shadow

%description
RSBAC administration is done via command line tools or dialog menus.
Please see the online documentation at http://www.rsbac.org/instadm.htm

%package -n	%{fname}
Summary:	A hardened linux solution
Group:		System/Base
Requires:	%{name}, kernel-%{fname}
Provides:	%{lib_name} = %{version}-%{release}
Provides:	%{lib_name_orig} = %{version}-%{release}
Provides:	pam_%{fname} = %{version}-%{release}
Provides:	%{fname}-rklogd = %{version}-%{release}
Provides:	%{libnss_name} = %{version}-%{release}
Provides:	%{libnss_name_orig} = %{version}-%{release}
Obsoletes:	%{lib_name} = %{version}-%{release}
Obsoletes:	%{lib_name_orig} = %{version}-%{release}
Obsoletes:	pam_%{fname} = %{version}-%{release}
Obsoletes:	%{fname}-rklogd = %{version}-%{release}
Obsoletes:	%{libnss_name} = %{version}-%{release}
Obsoletes:	%{libnss_name_orig} = %{version}-%{release}

%description -n	%{fname}
RSBAC is a flexible, powerful and fast (low overhead) access control framework
for current Linux kernels: 
 * Free Open Source (GPL) Linux kernel security solution
 * Independent of governments and big companies
 * Several well-known and new security models, like MAC, ACL and RC
 * Detailed control over individual user and program network accesses
 * Virtual User Management, in kernel and fully access controlled
 * On-access virus scanning with the Dazuko interface
 * Any combination of security models possible
 * Easily extensible: write your own model for runtime registration
 * Support for latest kernels and stable for production use

%package -n	%{fname}-devel
Summary:	Headers and libraries for developing programs that will use %{name}
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{lib_name}-devel = %{version}-%{release}
Provides:	%{lib_name_orig}-devel = %{version}-%{release}
Provides:	%{lib_name}-static-devel = %{version}-%{release}
Provides:	%{lib_name_orig}-static-devel = %{version}-%{release}
Provides:	%{libnss_name}-devel = %{version}-%{release}
Provides:	%{libnss_name_orig}-devel = %{version}-%{release}
%ifarch x86_64
Provides:	lib64%{fname}-devel = %{version}-%{release}
Provides:	lib64%{nss_name}-devel = %{version}-%{release}
Obsoletes:	lib64%{fname}-devel = %{version}-%{release}
Obsoletes:	lib64%{nss_name}-devel = %{version}-%{release}
%endif
Obsoletes:	%{lib_name}-devel = %{version}-%{release}
Obsoletes:	%{lib_name_orig}-devel = %{version}-%{release}
Obsoletes:	%{lib_name}-static-devel = %{version}-%{release}
Obsoletes:	%{lib_name_orig}-static-devel = %{version}-%{release}
Obsoletes:	%{libnss_name}-devel = %{version}-%{release}
Obsoletes:	%{libnss_name_orig}-devel = %{version}-%{release}

%description -n	%{fname}-devel
This package contains all files that programmers will need to develop
applications which will use RSBAC.

%prep
%setup -q -n %{name}-%{version}

# lib64 fixes
find -name "Makefile" | xargs sed -i -e "s|/lib\b|/%{_lib}|g"

%build

%make PREFIX=%{_prefix} DIR_PAM=/%{_lib}/security

%install
find main/tools/src/scripts -type f | xargs chmod a+x 
%makeinstall PREFIX=%{_prefix} DESTDIR=%{buildroot} DIR_PAM=/%_lib/security
mkdir -p %{buildroot}%{_sysconfdir} && cp debian/rsbac.conf %{buildroot}%{_sysconfdir}
cp debian/man/* %{buildroot}/%{_mandir}/man1/ 
mkdir -p %{buildroot}/%{_initrddir}
install -m 755 %{SOURCE1} %{buildroot}/%{_initrddir}/rklogd
mkdir -p %{buildroot}/%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/rklogd
install -m 755 %{SOURCE3} %{buildroot}/%{_bindir}/update_urpmi

%find_lang %name --all-name

cat <<EOF > %{buildroot}/%{_sysconfdir}/rsbac.conf
# RSBAC menu configuration
# "$(date)"
RSBACMOD="GEN DAZ FF RC ACL AUTH CAP JAIL RES PAX"
DIALOG="dialog"
# RSBACLANG is not set
TMPDIR="/tmp"
# RSBACPATH is not set
# RSBACLOGFILE is not set
EOF

# Documentation
rm -rf rsbac-tools
mv %{buildroot}/%{_docdir}/rsbac-tools-%{version} rsbac-tools
find rsbac-tools/examples -type f | xargs chmod a-x
rm -f rsbac-tools/examples/reg/reg_syscall

%pre
/usr/sbin/useradd --comment "RSBAC security officer" --home-dir /secoff --create-home --uid 400 --shell /bin/bash secoff
/usr/sbin/useradd --comment "RSBAC security auditor" --home-dir /dev/null --create-home --uid 404 --shell /sbin/nologin audit
/sbin/ldconfig

%post
%_post_service rklogd

%preun
%_preun_service rklogd

%postun
%_postun_userdel secoff
%_postun_groupdel secoff
%_postun_userdel audit
%_postun_groupdel audit
/sbin/ldconfig

%files -f %name.lang
%defattr(-,root,root,0755)
%doc README rsbac-tools
%config(noreplace) %{_sysconfdir}/rsbac.conf
%config(noreplace) %{_sysconfdir}/sysconfig/rklogd
%{_initrddir}/rklogd
/bin/rsbac_login
%_sbindir/rklogd
%{_bindir}/acl*
%{_bindir}/attr*
%{_bindir}/auth*
%{_bindir}/backup*
%{_bindir}/daz*
%{_bindir}/get*
%{_bindir}/linux2acl
%{_bindir}/mac*
%{_bindir}/net*
%{_bindir}/pm*
%{_bindir}/rc*
%{_bindir}/rklogd-viewer
%{_bindir}/rs*
%{_bindir}/switch*
%{_bindir}/update_urpmi
%{_bindir}/user_aci.sh
/%{_lib}/security/pam_rsbac.so
/%{_lib}/security/pam_rsbac_oldpw.so
%{_libdir}/librsbac.so.*
%{_libdir}/libnss_rsbac.so.*
%{_mandir}/man1/*
%{_mandir}/man8/rklogd*

%files -n %{fname}-devel
%{_libdir}/librsbac.so
%{_libdir}/libnss_rsbac.so
%{_includedir}/rsbac

%files -n %{fname}



%changelog
* Tue Feb 28 2012 Lonyai Gergely <aleph@mandriva.org> 2:1.4.6-1mdv2012.0
+ Revision: 781171
- 1.4.6

* Thu Feb 09 2012 Matthew Dawkins <mattydaw@mandriva.org> 2:1.4.5-3
+ Revision: 772231
- removed competitive provides for both passwd and shadow

* Sun Jun 05 2011 Lonyai Gergely <aleph@mandriva.org> 2:1.4.5-2
+ Revision: 682769
- Change the devel dependency

* Wed May 25 2011 Lonyai Gergely <aleph@mandriva.org> 2:1.4.5-1
+ Revision: 678976
- 1.4.5

* Tue Dec 07 2010 Oden Eriksson <oeriksson@mandriva.com> 1.5.0-0.0.git.3mdv2011.0
+ Revision: 614719
- the mass rebuild of 2010.1 packages

* Tue Apr 20 2010 Lonyai Gergely <aleph@mandriva.org> 1.5.0-0.0.git.2mdv2010.1
+ Revision: 536941
- change wrong dependency in -devel

* Fri Apr 09 2010 Lonyai Gergely <aleph@mandriva.org> 1.5.0-0.0.git.1mdv2010.1
+ Revision: 533358
- Update to 1.5.0 git version (2010-04-08)
- 1.4.3

* Fri Aug 14 2009 Lonyai Gergely <aleph@mandriva.org> 1.4.2-4mdv2010.0
+ Revision: 416334
- igraltist create a wrapper to Debian. I modify to Mandriva and provide in this package. TODO: recreate a clean urpmi wrapper.

* Fri Aug 07 2009 Lonyai Gergely <aleph@mandriva.org> 1.4.2-3mdv2010.0
+ Revision: 411241
- fix typo
- meld the packages

* Fri Aug 07 2009 Lonyai Gergely <aleph@mandriva.org> 1.4.2-2mdv2010.0
+ Revision: 411162
- release fix
- add "rsbac" container package

* Wed Aug 05 2009 Lonyai Gergely <aleph@mandriva.org> 1.4.2-1mdv2010.0
+ Revision: 410154
- Update to 1.4.2

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Wed Mar 05 2008 Oden Eriksson <oeriksson@mandriva.com> 1.2.8-2mdv2008.1
+ Revision: 179463
- rebuild

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Aug 29 2007 Oden Eriksson <oeriksson@mandriva.com> 1.2.8-1mdv2008.0
+ Revision: 73373
- Import rsbac-admin



* Wed Aug 30 2006 Arnaud Patard <apatard@mandriva.com> 1.2.8-1mdv2007.0
- 1.2.8
- Drop obselete patches
- Don't build with VERBOSE=1
- Packaging fixes (e.g. call ldconfig)

* Mon Jul 17 2006 Oden Eriksson <oeriksson@mandrakesoft.com> 1.2.6-7mdv2007.0
- rebuild

* Mon Jul 17 2006 Oden Eriksson <oeriksson@mandrakesoft.com> 1.2.6-6mdv2007.0
- rebuild

* Sun Jul 16 2006 Oden Eriksson <oeriksson@mandrakesoft.com> 1.2.6-5mdv2007.0
- don't build it twice (P1)
- added lib64 fixes
- fix docs

* Mon May 29 2006 Thierry Vignaud <tvignaud@mandriva.com> 1.2.6-3mdv2007.0
- add bug reference

* Mon May 22 2006 Thierry Vignaud <tvignaud@mandriva.com> 1.2.6-3mdk
- add buildrequires: ncurses-devel

* Mon May 22 2006 Thierry Vignaud <tvignaud@mandriva.com> 1.2.6-2mdk
- buildrequires: pam-devel
- obsoletes rsbac-admin-doc (dead subpackge since 1 year) (#19057)
- don't package X times the not so usefull README

* Fri May 19 2006 Arnaud Patard <apatard@mandriva.com> 1.2.6-1mdk
- 1.2.6

* Wed May 10 2006 Thierry Vignaud <tvignaud@mandriva.com> 1.2.5-3mdk
- use %%mkrel
- compile everything
- patch 5: fix compiling pam support

* Thu Mar 30 2006 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.2.5-2mdk
- add BuildRequires: libtool

* Wed Jan 18 2006 Arnaud Patard <apatard@mandriva.com> 1.2.5-1mdk
- 1.2.5

* Tue Sep 20 2005 Guillaume Rousse <guillomovitch@mandriva.org> 1.2.4-3mdk
- ship devel man page in devel package in correct place 

* Sat May 21 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.4-2mdk
- use the %%configure2_5x macro

* Thu Mar 31 2005 Arnaud Patard <apatard@mandrakesoft.com> 1.2.4-1mdk
- Update to current stable version (to match kernel version and fix the build)

* Mon Feb 28 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.2.3-4mdk
- run aclocal before automake

* Sat Dec 25 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.2.3-3mdk
- bah, fix buildrequires

* Sat Dec 25 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.2.3-2mdk
- use automake-1.8
- cosmetics

* Mon Jul 19 2004 Nicolas Planel <nplanel@mandrakesoft.com> 1.2.3-1mdk
- Inital release for Mandrakelinux distribution.
