#
# Conditional build:
%bcond_without	tests	# do not perform "make test"
#
%include	/usr/lib/rpm/macros.perl
%define		pdir	Mail
%define		pnam	SRS
Summary:	Mail::SRS - Perl implementation of SRS
Summary(pl):	Mail::SRS - perlowa implementacja SRS
Name:		perl-Mail-SRS
Version:	0.31
Release:	2
# same as perl
License:	GPL v1+ or Artistic
Group:		Development/Languages/Perl
Source0:	http://www.anarres.org/projects/srs/%{pdir}-%{pnam}-%{version}.tar.gz
# Source0-md5:	1440999563a7b25d5fb03204b03e1060
Source1:	srsd.init
URL:		http://www.anarres.org/projects/srs/
BuildRequires:	perl-DB_File
BuildRequires:	perl-Digest-HMAC
BuildRequires:	perl-MLDBM
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.268
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This module implements a library to rewrite sender addresses according
to the SRS rewriting scheme, to let forwarders work in a
sender-authenticated SMTP world.

%description -l pl
Ten modu³ jest implementacj± biblioteki przepisuj±cej adresy nadawcy
zgodnie ze schematem przepisywania SRS, aby pozwoliæ przekazuj±cym
dzia³aæ w ¶wiecie z SMTP z uwierzytelnieniem nadawcy.

%package -n srsd
Summary:	SRS address rewriting daemon
Summary(pl):	Demon przepisuj±cy adresy SRS
Group:		Networking/Daemons
Requires(post):	/usr/bin/perl
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}
Requires:	rc-scripts

%description -n srsd
SRS address rewriting daemon, operating as a local process on
UNIX-domain sockets.

%description -n srsd -l pl
Demon przepisuj±cy adresy SRS, dzia³aj±cy jako lokalny proces na
gniazdach uniksowych.

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
touch $RPM_BUILD_ROOT%{_sysconfdir}/srsd.secret
touch $RPM_BUILD_ROOT%{_sysconfdir}/srsd.secret.1

%clean
rm -rf $RPM_BUILD_ROOT

%post -n srsd
if [ ! -f %{_sysconfdir}/srsd.secret ] ; then
	echo "Generating SRS secret..."
	umask 066
	perl -e 'open R,"/dev/urandom"; read R,$r,16;
		printf "%02x",ord(chop $r) while($r);' > %{_sysconfdir}/srsd.secret
fi
/sbin/chkconfig --add srsd
%service srsd restart "SRS daemon"

%preun -n srsd
if [ "$1" = "0" ]; then
	%service srsd stop
	/sbin/chkconfig --del srsd
fi

%files
%defattr(644,root,root,755)
%doc README.pobox eg TODO README
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
%attr(600,root,root) %ghost %{_sysconfdir}/srsd.secret
%attr(600,root,root) %ghost %{_sysconfdir}/srsd.secret.1
