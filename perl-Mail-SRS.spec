#
# Conditional build:
%bcond_without	tests	# do not perform "make test"
#
%include	/usr/lib/rpm/macros.perl
%define	pdir	Mail
%define	pnam	SRS
Summary:	Mail::SRS - Perl implementation of SRS
Summary(pl):	Mail::SRS - perlowa implementacja SRS
Name:		perl-Mail-SRS
Version:	0.27
Release:	0.1
# Same as perl
License:	GPL/Artistic
Group:		Development/Languages/Perl
Source0:	http://www.anarres.org/projects/srs/%{pdir}-%{pnam}-%{version}.tar.gz
# Source0-md5:	2edcaddd5c2d54c3b6a05262930864d6
Source1:	srsd.init
URL:		http://www.anarres.org/projects/srs/
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	perl-DB_File 
BuildRequires:	perl-Digest-HMAC
BuildRequires:	perl-MLDBM
BuildRequires:	perl-Storable
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This module implements a library to rewrite sender addresses according to the
SRS rewritign scheme, to let forwarders work in a sender-authenticated SMTP
world

%package -n srsd
Summary:	SRS address rewriting daemon
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}

%description -n srsd
SRS address rewriting daemon, operating as a local process on
UNIX-domain sockets.

%prep
%setup -q -n %{pdir}-%{pnam}-%{version}

%build
(echo y; echo y) | %{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make}

%{?with_tests:%{__make} test}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/srsd

%clean
rm -rf $RPM_BUILD_ROOT

%post -n srsd
/sbin/chkconfig --add srsd
umask 137
if [ -f /var/lock/subsys/srsd ]; then
        /etc/rc.d/init.d/srsd restart 1>&2
else
        echo "Run \"/etc/rc.d/init.d/srsd start\" to start SRS daemon."
fi
 
%preun -n srsd
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/srsd ]; then
                /etc/rc.d/init.d/srsd stop 1>&2
        fi
        /sbin/chkconfig --del srsd
fi

%files
%defattr(644,root,root,755)
%doc README.pobox  eg  TODO README
%attr(755,root,root) %{_bindir}/srs
%dir %{perl_vendorlib}/Mail/SRS
%{perl_vendorlib}/Mail/SRS/*.pm
%{perl_vendorlib}/Mail/SRS.pm
%{_mandir}/man1/*
%{_mandir}/man3/*

%files -n srsd
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/srsd
%attr(754,root,root) /etc/rc.d/init.d/srsd
%ghost %config /etc/srsd.secret
%ghost %config /etc/srsd.secret.1

%post -n srsd
if [ ! -f /etc/srsd.secret ] ; then
        echo "Generating SRS secret..."
        umask 066
        perl -e 'open R,"/dev/urandom"; read R,$r,16;
                 printf "%02x",ord(chop $r) while($r);' > /etc/srsd.secret
fi
