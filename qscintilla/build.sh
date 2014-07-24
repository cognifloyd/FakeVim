#!/bin/bash
set -e

# remove previous build
rm -rf build

# build in separate directory
mkdir -p build
cd build
ln -s ../sip

# generate files
python ../configure.py --fakevim-libdir=/mnt/sdb1/git/github/cognifloyd/FakeVim.git/fakevim/ \
	--pyqt-sipdir=/usr/share/sip --verbose
#python ../configure.py

# compile
make

# test
export PYTHONPATH=$PWD
export LD_LIBRARY_PATH=$PWD/../../fakevim:$LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH
../test.py

