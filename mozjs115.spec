#
# Inspired by the Arch Linux equivalent package.....
#
Name     : mozjs115
Version  : 115.3.0
Release  : 6
URL      : https://archive.mozilla.org/pub/firefox/releases/115.3.0esr/source/firefox-115.3.0esr.source.tar.xz
Source0  : https://archive.mozilla.org/pub/firefox/releases/115.3.0esr/source/firefox-115.3.0esr.source.tar.xz
Group    : Development/Tools
Summary  : JavaScript interpreter and libraries
License  : Apache-2.0 BSD-2-Clause BSD-3-Clause BSD-3-Clause-Clear GPL-2.0 LGPL-2.0 LGPL-2.1 MIT MPL-2.0-no-copyleft-exception
Requires: mozjs115-bin = %{version}-%{release}
Requires: mozjs115-lib = %{version}-%{release}
Requires: pypi-psutil
Requires: pypi-pyopenssl
Requires: pypi-pyasn1
Requires: pypi-wheel
BuildRequires : autoconf213
BuildRequires : icu4c-dev
BuildRequires : llvm-dev
BuildRequires : ncurses-dev
BuildRequires : nspr-dev
BuildRequires : pypi-pbr
BuildRequires : pypi-pip
BuildRequires : pkgconfig(libffi)
BuildRequires : pkgconfig(x11)
BuildRequires : pypi-psutil
BuildRequires : python3-core
BuildRequires : python3-dev
BuildRequires : readline-dev
BuildRequires : rustc
BuildRequires : pypi-setuptools
BuildRequires : zlib-dev

Patch1: fix-soname.patch
Patch2: copy-headers.patch
Patch3: init_patch.patch
Patch4: emitter.patch
Patch5: spidermonkey_checks_disable.patch

%description
JavaScript interpreter and libraries - Version 115

%package bin
Summary: bin components for the mozjs115 package.
Group: Binaries

%description bin
bin components for the mozjs115 package.


%package dev
Summary: dev components for the mozjs115 package.
Group: Development
Requires: mozjs115-lib = %{version}-%{release}
Requires: mozjs115-bin = %{version}-%{release}
Provides: mozjs115-devel = %{version}-%{release}

%description dev
dev components for the mozjs115 package.


%package lib
Summary: lib components for the mozjs115 package.
Group: Libraries

%description lib
lib components for the mozjs115 package.


%prep
%setup -q -n firefox-%{version}

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

pushd ..
cp -a firefox-%{version} buildavx2
popd



# use system zlib for perf
rm -rf ../../modules/zlib


%build
export http_proxy=http://127.0.0.1:9/
export https_proxy=http://127.0.0.1:9/
export no_proxy=localhost,127.0.0.1,0.0.0.0
export LANG=C.UTF-8
export SOURCE_DATE_EPOCH=1501084420
export CFLAGS="-Os -falign-functions=4 -fno-semantic-interposition -fno-signed-zeros "
export CXXFLAGS="-Os -falign-functions=4 -fno-semantic-interposition -fno-signed-zeros"
export AUTOCONF="/usr/bin/autoconf213"
CFLAGS+=' -fno-delete-null-pointer-checks -fno-strict-aliasing -fno-tree-vrp '
CXXFLAGS+=' -fno-delete-null-pointer-checks -fno-strict-aliasing -fno-tree-vrp '
export CC=gcc CXX=g++ PYTHON3=/usr/bin/python3

pushd js/src

#autoconf213
%configure --disable-static \
    --prefix=/usr \
    --disable-debug \
    --enable-debug-symbols \
    --disable-strip \
    --disable-jemalloc \
    --enable-optimize="-O3" \
    --enable-posix-nspr-emulation \
    --enable-readline \
    --enable-release \
    --enable-shared-js \
    --enable-tests \
    --with-intl-api \
    --with-system-zlib \
    --with-x \
    --program-suffix=115 \
    --without-system-icu

make %{?_smp_mflags}
popd

pushd ../buildavx2/js/src
export CFLAGS="$CFLAGS -m64 -march=x86-64-v3 -Wl,-z,x86-64-v3 -O3" 
export CXXFLAGS="$CXXFLAGS -m64 -march=x86-64-v3 -Wl,-z,x86-64-v3 " 
export LDFLAGS="$LDFLAGS -m64 -march=x86-64-v3"
#autoconf213
%configure --disable-static \
    --prefix=/usr \
    --disable-debug \
    --enable-debug-symbols \
    --disable-strip \
    --disable-jemalloc \
    --enable-optimize="-O3" \
    --enable-posix-nspr-emulation \
    --enable-readline \
    --enable-release \
    --enable-shared-js \
    --enable-tests \
    --with-intl-api \
    --with-system-zlib \
    --with-x \
    --program-suffix=115 \
    --without-system-icu

make %{?_smp_mflags}
popd


%install
export SOURCE_DATE_EPOCH=1501084420
rm -rf %{buildroot}
pushd js/src
%make_install
popd
pushd ../buildavx2/js/src
%make_install_v3
popd
rm %{buildroot}*/usr/lib64/*.ajs

cp %{buildroot}/usr/lib64/libmozjs-115.so %{buildroot}/usr/lib64/libmozjs-115.so.0
cp %{buildroot}-v3/usr/lib64/libmozjs-115.so %{buildroot}-v3/usr/lib64/libmozjs-115.so.0

/usr/bin/elf-move.py avx2 %{buildroot}-v3 %{buildroot} %{buildroot}/usr/share/clear/filemap/filemap-%{name}

%files
%defattr(-,root,root,-)

%files bin
%defattr(-,root,root,-)
/usr/bin/js115
/usr/bin/js115-config
/V3/usr/bin/js115

%files dev
%defattr(-,root,root,-)
/usr/include/mozjs-115/
/usr/lib64/pkgconfig/mozjs-115.pc

%files lib
%defattr(-,root,root,-)
/usr/lib64/libmozjs-115.so
/usr/lib64/libmozjs-115.so.0
/V3/usr/lib64/libmozjs-115.so
/V3/usr/lib64/libmozjs-115.so.0
