%define	name	rsbac-admin
%define	fname	rsbac
%define	version	1.5.0
%define release %mkrel 0.0.git.3

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
Source3:	update_urpmi
Requires:	dialog
BuildRequires:	libtool pam-devel ncurses-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Obsoletes:	%{name}-doc
Provides:	%{name}-doc
Provides:	passwd, shadow

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
Obsoletes:       %{lib_name} = %{version}-%{release}
Obsoletes:       %{lib_name_orig} = %{version}-%{release}
Obsoletes:       pam_%{fname} = %{version}-%{release}
Obsoletes:       %{fname}-rklogd = %{version}-%{release}
Obsoletes:       %{libnss_name} = %{version}-%{release}
Obsoletes:       %{libnss_name_orig} = %{version}-%{release}

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
Summary:	Headers, libraries and includes for developing programs that will use %{name}
Group:		Development/C
Requires:	kernel-%{fname}-devel
Requires:	%{name} = %{version}
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
Obsoletes:      lib64%{fname}-devel = %{version}-%{release}
Obsoletes:       lib64%{nss_name}-devel = %{version}-%{release}
%endif
Obsoletes:       %{lib_name}-devel = %{version}-%{release}
Obsoletes:       %{lib_name_orig}-devel = %{version}-%{release}
Obsoletes:       %{lib_name}-static-devel = %{version}-%{release}
Obsoletes:       %{lib_name_orig}-static-devel = %{version}-%{release}
Obsoletes:       %{libnss_name}-devel = %{version}-%{release}
Obsoletes:       %{libnss_name_orig}-devel = %{version}-%{release}

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
rm -rf %{buildroot}
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

%clean
rm -rf %{buildroot}

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
%defattr(-,root,root)
%{_libdir}/librsbac.so
%{_libdir}/librsbac.la
%{_libdir}/librsbac.a
%{_libdir}/libnss_rsbac.la
%{_libdir}/libnss_rsbac.a
%{_libdir}/libnss_rsbac.so
%{_includedir}/rsbac

%files -n %{fname}

