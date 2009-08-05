%define	name	rsbac-admin
%define	fname	rsbac
%define	version	1.4.2
%define release %mkrel 1
%define	lib_name_orig lib%{fname}
%define	librsbac_major 1
%define	lib_name %mklibname %{fname} %{librsbac_major}
%define nss_name nss_rsbac
%define libnss_name_orig lib%{nss_name}
%define libnss_major 2
%define	libnss_name %mklibname %{nss_name} %{libnss_major}

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	A set of RSBAC utilities
License:	GPL
Group:		System/Configuration/Other
Url:		http://www.rsbac.org
Source0:	http://download.rsbac.org/code/%{version}/%{name}-%{version}.tar.bz2
Source1:	rklogd.init
Source2:	rklogd.conf
Requires:	dialog
BuildRequires:	libtool pam-devel ncurses-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Obsoletes:	%{name}-doc
Provides:	%{name}-doc

%description
RSBAC administration is done via command line tools or dialog menus.
Please see the online documentation at http://www.rsbac.org/instadm.htm

%package -n	%{lib_name}
Summary:	Main library for %{name}
Group:		System/Libraries
Provides:	%{lib_name_orig} = %{version}-%{release}

%description -n	%{lib_name}
This package contains the library needed to run programs dynamically
linked with %{name}.

%package -n	%{lib_name}-devel
Summary:	Headers for developing programs that will use %{name}
Group:		Development/C
Requires:	kernel-source
Requires:	%{lib_name} = %{version}
Provides:	%{lib_name_orig}-devel = %{version}-%{release}
%ifarch x86_64
Provides:	lib64%{fname}-devel = %{version}-%{release}
%endif

%description -n	%{lib_name}-devel
This package contains the headers that programmers will need to develop
applications which will use %{name}.

%package -n	%{lib_name}-static-devel
Summary:	Static library for developing programs that will use %{name}
Group:		Development/C
Requires:	%{lib_name}-devel = %{version} 
Provides:	%{lib_name_orig}-static-devel = %{version}-%{release}

%description -n	%{lib_name}-static-devel
This package contains the static library that programmers will need to develop
applications which will use %{name}.


%package -n	pam_rsbac
Summary:	RSBAC plugins for PAM
Group:		System/Libraries

%description -n	pam_rsbac
This package contains plugins that enable using RSBAC for authentication
through PAM.


%package -n	rsbac-rklogd
Summary:	Standalone daemon to log RSBAC messages
Group:		System/Kernel and hardware

%description -n	rsbac-rklogd
This is a standalone daemon to log RSBAC messages
to its own facility, by default the file /var/log/rsbac/rsbac.log
To prevent messages to be logged through syslog too,
add the kernel parameter 'rsbac_nosyslog' at boot.
It provides also a log viewer: rklogd-viewer


%package -n	%{libnss_name}
Summary:	RSBAC NSS module to use RSBAC User Management
Group:		System/Libraries
Provides:	%{libnss_name_orig} = %{version}-%{release}

%description -n	%{libnss_name}
This package contains the RSBAC NSS module to use RSBAC User Management.


%package -n	%{libnss_name}-devel
Summary:	Headers for developing programs that will use %{libnss_name}
Group:		Development/C
Requires:	kernel-source
Requires:	%{libnss_name} = %{version}
Provides:	%{libnss_name_orig}-devel = %{version}-%{release}
%ifarch x86_64
Provides:	lib64%{nss_name}-devel = %{version}-%{release}
%endif


%description -n	%{libnss_name}-devel
This package contains the headers that programmers will need to develop
applications which will use %{libnss_name}.


%prep
%setup -q -n %{name}-%{version}

# lib64 fixes
find -name "Makefile" | xargs sed -i -e "s|/lib\b|/%{_lib}|g"

%build

%make PREFIX=%{_prefix} DIR_PAM=/%{_lib}/security 
#DIR_NSS=%_libdir DIR_LIBS=%_libdir build

%install
rm -rf %{buildroot}
find main/tools/src/scripts -type f | xargs chmod a+x 
%makeinstall PREFIX=%{_prefix} DESTDIR=%{buildroot} DIR_PAM=/%_lib/security
#find $RPM_BUILD_ROOT -name '*.la' | xargs sed -i -e "s|-L$RPM_BUILD_DIR/%{name}-%{version}/main/libs||g"
mkdir -p %{buildroot}%{_sysconfdir} && cp debian/rsbac.conf %{buildroot}%{_sysconfdir}
cp debian/man/* %{buildroot}/%{_mandir}/man1/ 
mkdir -p %{buildroot}/%{_initrddir}
install -m 755 %{SOURCE1} %{buildroot}/%{_initrddir}/rklogd
mkdir -p %{buildroot}/%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/sysconfig/rklogd

%find_lang %name --all-name

echo "# RSBAC menu configuration
# "$(date)"
RSBACMOD="GEN MAC PM DAZ FF RC ACL AUTH CAP JAIL RES PAX"
DIALOG="dialog"
# RSBACLANG is not set
TMPDIR="/tmp"
# RSBACPATH is not set
# RSBACLOGFILE is not set
" > %{buildroot}/%{_sysconfdir}/rsbac.conf

# Documentation
rm -rf rsbac-tools
mv %{buildroot}/%{_docdir}/rsbac-tools-%{version} rsbac-tools
find rsbac-tools/examples -type f | xargs chmod a-x
rm -f rsbac-tools/examples/reg/reg_syscall

%clean
rm -rf %{buildroot}

%pre
/usr/sbin/useradd --comment "RSBAC security officer" --home-dir /secoff --create-home --uid 400 --shell /bin/bash secoff
/usr/sbin/useradd --comment "RSBAC security auditor" --home-dir /dev/null --create-home --uid 404 --shell /sbin/nologin audit
/sbin/ldconfig

%postun
%_postun_userdel secoff
%_postun_groupdel secoff
%_postun_userdel audit
%_postun_groupdel audit
/sbin/ldconfig

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%post -n %{libnss_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libnss_name} -p /sbin/ldconfig
%endif

%files -f %name.lang
%defattr(-,root,root,0755)
%doc README rsbac-tools
%config(noreplace) %{_sysconfdir}/rsbac.conf
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
%{_bindir}/rs*
%{_bindir}/switch*
%{_bindir}/user_aci.sh
%{_mandir}/man1/*

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/%{lib_name_orig}.so.%{librsbac_major}*

%files -n %{lib_name}-devel
%defattr(-,root,root)
%{_libdir}/%{lib_name_orig}.so
%{_libdir}/%{lib_name_orig}.la
%{_includedir}/rsbac

%files -n %{lib_name}-static-devel
%defattr(-,root,root)
%{_libdir}/%{lib_name_orig}*.a

%files -n pam_rsbac
%defattr(-,root,root)
/bin/rsbac_login
/%{_lib}/security/pam_rsbac*.so*

%files -n %{libnss_name}
%defattr(-,root,root)
%{_libdir}/libnss_rsbac*.so.%{libnss_major}*

%files -n %{libnss_name}-devel
%defattr(-,root,root)
%{_libdir}/libnss_rsbac*.la
%{_libdir}/libnss_rsbac*.a
%{_libdir}/libnss_rsbac*.so

%files -n rsbac-rklogd
%defattr(-,root,root)
%_bindir/rklogd-viewer
%_sbindir/rklogd
%{_initrddir}/rklogd
%config(noreplace) %{_sysconfdir}/sysconfig/rklogd
%{_mandir}/man8/rklogd*
