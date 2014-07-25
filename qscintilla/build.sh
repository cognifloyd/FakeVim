#!/bin/bash
set -e

# remove previous build
rm -rf build

# build in separate directory
mkdir -p build
cd build
ln -s ../sip

PYTHON=${PYTHON:-`which python`}

# generate files
if [[ `uname -r` == *gentoo* ]]; then
	# detected gentoo installation.
	$PYTHON ../configure.py \
		--fakevim-libdir=../../fakevim \
		--pyqt-sipdir=/usr/share/sip \
		--verbose
else
	$PYTHON ../configure.py \
		--fakevim-libdir=../../fakevim \
		--verbose
fi

# compile
make

# test
export PYTHONPATH=$PWD
echo "PYTHONPATH=$PYTHONPATH"
export LD_LIBRARY_PATH=$PWD/../../fakevim:$LD_LIBRARY_PATH
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
../test.py

