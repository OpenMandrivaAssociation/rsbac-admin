%define	name	rsbac-admin
%define	fname	rsbac
%define	version	1.2.8
%define	url	http://www.rsbac.org
%define	lib_name_orig lib%{fname}
%define	lib_major 1
%define	lib_name %mklibname %{fname} %{lib_major}
%define nss_name nss_rsbac
%define libnss_name_orig lib%{nss_name}
%define	libnss_name %mklibname %{nss_name} 2

Name: 		%{name}
Version:	%{version}
Release: 	%mkrel 2
Summary: 	A set of RSBAC utilities
License: 	GPL
Group: 		System/Configuration/Other
Url: 		%{url}
Source0: 	%{url}/download/code/v%{version}/%{name}-%{version}.tar.bz2
Requires(pre):	/usr/sbin/useradd
Requires: 	dialog
BuildRequires:	libtool pam-devel ncurses-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Obsoletes: %{name}-doc
Provides: %{name}-doc

%description
RSBAC administration is done via command line tools or dialog menus.
Please see the online documentation at http://www.rsbac.org/instadm.htm
 or the %{name}-doc package.

%package -n	%{name}-doc
Summary:	RSBAC administration documentation
Group:		System/Configuration/Other

%description -n	%{name}-doc
RSBAC administration documentation.

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

%make PREFIX=%{_prefix} DIR_PAM=/%_lib/security DIR_NSS=%_libdir DIR_LIBS=%_libdir build

%install
rm -rf $RPM_BUILD_ROOT
find main/tools/src/scripts -type f | xargs chmod a+x 
%makeinstall_std PREFIX=%{_prefix} DIR_LIBS=%{_libdir} \
    DIR_PAM=/%_lib/security DIR_NSS=%_libdir DIR_DOC=%{_docdir}/rsbac-tools-%{version}
find $RPM_BUILD_ROOT -name '*.la' | xargs sed -i -e "s|-L$RPM_BUILD_DIR/%{name}-%{version}/main/libs||g"

%find_lang %name --all-name

# Documentation
rm -rf rsbac-tools
mv $RPM_BUILD_ROOT/%{_docdir}/rsbac-tools-%{version} rsbac-tools
find rsbac-tools/examples -type f | xargs chmod a-x
rm -f rsbac-tools/examples/reg/reg_syscall

%clean
rm -rf $RPM_BUILD_ROOT

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
%{_libdir}/%{lib_name_orig}.so.*

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
/%_lib/security/pam_rsbac*.so*

%files -n %{libnss_name}
%defattr(-,root,root)
%_libdir/libnss_rsbac*.so.*

%files -n %{libnss_name}-devel
%defattr(-,root,root)
%_libdir/libnss_rsbac*.la
%_libdir/libnss_rsbac*.a
%_libdir/libnss_rsbac*.so

%files -n rsbac-rklogd
%defattr(-,root,root)
%_bindir/rklogd-viewer
%_sbindir/rklogd
%{_mandir}/man8/rklogd*
