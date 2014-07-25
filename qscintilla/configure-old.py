# This script configures FakeVim for PyQt v3 and/or v4.
#
# Copyright (c) 2014 Riverbank Computing Limited <info@riverbankcomputing.com>
# 
# This file is part of FakeVim.
# 
# This file may be used under the terms of the GNU General Public
# License versions 2.0 or 3.0 as published by the Free Software
# Foundation and appearing in the files LICENSE.GPL2 and LICENSE.GPL3
# included in the packaging of this file.  Alternatively you may (at
# your option) use any later version of the GNU General Public
# License if such license has been publicly approved by Riverbank
# Computing Limited (or its successors, if any) and the KDE Free Qt
# Foundation. In addition, as a special exception, Riverbank gives you
# certain additional rights. These rights are described in the Riverbank
# GPL Exception version 1.1, which can be found in the file
# GPL_EXCEPTION.txt in this package.
# 
# If you are unsure which license is appropriate for your use, please
# contact the sales department at sales@riverbankcomputing.com.
# 
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


import sys
import os
import glob
import optparse


# Import SIP's configuration module so that we have access to the error
# reporting.  Then try and import the configuration modules for both PyQt3 and
# PyQt4.
try:
    import sipconfig
except ImportError:
    sys.stderr.write("Unable to import sipconfig.  Please make sure SIP is installed.\n")
    sys.exit(1)

try:
    import PyQt4.pyqtconfig as pyqt4
except:
    pyqt4 = None

try:
    import pyqtconfig as pyqt3
except:
    pyqt3 = None

if pyqt4 is not None:
    pyqt = pyqt4.Configuration()
    qt_data_dir = pyqt.qt_data_dir
elif pyqt3 is not None:
    pyqt = pyqt3.Configuration()
    qt_data_dir = pyqt.qt_dir
else:
    sipconfig.error("Unable to find either PyQt v3 or v4.")


# This must be kept in sync with Python/configure.py, fakevim.pro,
# example-Qt4Qt5/application.pro and designer-Qt4Qt5/designer.pro.
FAKEVIM_API_MAJOR = 0


# Initialise the globals.
sip_min_version = 0x040c00

if sys.platform == "win32":
    fakevim_define = "FAKEVIM_DLL"
else:
    fakevim_define = ""


def create_optparser():
    """Create the parser for the command line.
    """

    def store_abspath(option, opt_str, value, parser):
        setattr(parser.values, option.dest, os.path.abspath(value))

    def store_abspath_dir(option, opt_str, value, parser):
        if not os.path.isdir(value):
            raise optparse.OptionValueError("'%s' is not a directory" % value)
        setattr(parser.values, option.dest, os.path.abspath(value))

    p = optparse.OptionParser(usage="python %prog [options]",
            version=None)

    p.add_option("-a", "--apidir", action="callback", default=None,
            type="string", metavar="DIR", dest="fakevimdir",
            callback=store_abspath, help="where FakeVim's API file will be "
            "installed [default: QTDIR/fakevim]")
    p.add_option("-c", "--concatenate", action="store_true", default=False,
            dest="concat", help="concatenate the C++ source files")
    p.add_option("-d", "--destdir", action="callback",
            default=pyqt.pyqt_mod_dir, type="string", metavar="DIR",
            dest="fakevimmoddir", callback=store_abspath, help="where the "
            "FakeVim module will be installed [default: %s]" %
            pyqt.pyqt_mod_dir)
    p.add_option("-j", "--concatenate-split", type="int", default=1,
            metavar="N", dest="split", help="split the concatenated C++ "
            "source files into N pieces [default: 1]")
    p.add_option("-k", "--static", action="store_true", default=False,
            dest="static", help="build the FakeVim module as a static "
            "library")
    p.add_option("-n", action="callback", default=None, type="string",
            metavar="DIR", dest="fakevimincdir", callback=store_abspath_dir,
            help="the directory containing the FakeVim FakeVim header file "
            "directory [default: %s]" % pyqt.qt_inc_dir)
    p.add_option("--no-docstrings", action="store_true", default=False,
            dest="no_docstrings", help="disable the generation of docstrings")
    p.add_option("-o", action="callback", default=None, type="string",
            metavar="DIR", dest="fakevimlibdir", callback=store_abspath_dir,
            help="the directory containing the FakeVim library [default: "
            "%s]" % pyqt.qt_lib_dir)
    p.add_option("-p", type="int", default=-1, metavar="3|4", dest="pyqt_major",
            help="specifically configure for PyQt v3 or v4 [default v4, if "
            "found]")
    p.add_option("-r", "--trace", action="store_true", default=False,
            dest="tracing", help="build the FakeVim module with tracing "
            "enabled")
    p.add_option("-s", action="store_true", default=False, dest="not_dll",
            help="FakeVim is a static library and not a DLL (Windows only)")
    p.add_option("-u", "--debug", action="store_true", default=False,
            help="build the FakeVim module with debugging symbols")
    p.add_option("-v", "--sipdir", action="callback", default=None,
            metavar="DIR", dest="fakevimsipdir", callback=store_abspath,
            type="string", help="where the FakeVim .sip files will be "
            "installed [default: %s]" % pyqt.pyqt_sip_dir)
    p.add_option("-T", "--no-timestamp", action="store_true", default=False,
            dest="no_timestamp", help="suppress timestamps in the header "
            "comments of generated code [default: include timestamps]")

    if sys.platform != 'win32':
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            pip_default = True
            pip_default_str = "enabled"
        else:
            pip_default = False
            pip_default_str = "disabled"

        p.add_option("--protected-is-public", action="store_true",
                default=pip_default, dest="prot_is_public",
                help="enable building with 'protected' redefined as 'public' "
                        "[default: %s]" % pip_default_str)
        p.add_option("--protected-not-public", action="store_false",
                dest="prot_is_public",
                help="disable building with 'protected' redefined as 'public'")

    return p


def inform_user():
    """Tell the user the option values that are going to be used.
    """
    sipconfig.inform("PyQt %s is being used." % pyqt.pyqt_version_str)
    sipconfig.inform("Qt v%s %s edition is being used." % (sipconfig.version_to_string(pyqt.qt_version), pyqt.qt_edition))
    sipconfig.inform("SIP %s is being used." % pyqt.sip_version_str)

    sipconfig.inform("The FakeVim module will be installed in %s." % opts.fakevimmoddir)
    sipconfig.inform("The FakeVim API file will be installed in %s." % os.path.join(opts.fakevimdir, "api", "python"))
    sipconfig.inform("The FakeVim .sip files will be installed in %s." % opts.fakevimsipdir)

    if opts.no_docstrings:
        sipconfig.inform("The FakeVim module is being built without generated docstrings.")
    else:
        sipconfig.inform("The FakeVim module is being built with generated docstrings.")

    if opts.prot_is_public:
        sipconfig.inform("The FakeVim module is being built with 'protected' redefined as 'public'.")


def check_fakevim():
    """See if FakeVim can be found and what its version is.
    """


def sip_flags():
    """Return the SIP flags.
    """
    # Get the flags used for the main PyQt module.
    if pyqt.pyqt_version >= 0x040000:
        flags = pyqt.pyqt_sip_flags.split()
    else:
        flags = pyqt.pyqt_qt_sip_flags.split()
        flags.append("-x")
        flags.append("FakeVim_Qt4")

    # Generate the API file.
    flags.append("-a")
    flags.append("FakeVim.api")

    # Add PyQt's .sip files to the search path.
    flags.append("-I")
    flags.append(pyqt.pyqt_sip_dir)

    return flags


def generate_code():
    """Generate the code for the FakeVim module.
    """
    if pyqt.pyqt_version >= 0x040000:
        mname = "FakeVim"
    else:
        mname = "fakevim"

    sipconfig.inform("Generating the C++ source for the %s module..." % mname)

    # Build the SIP command line.
    argv = ['"' + pyqt.sip_bin + '"']

    argv.extend(sip_flags())

    if opts.no_timestamp:
        argv.append("-T")

    if not opts.no_docstrings:
        argv.append("-o");

    if opts.prot_is_public:
        argv.append("-P");

    if opts.concat:
        argv.append("-j")
        argv.append(str(opts.split))

    if opts.tracing:
        argv.append("-r")

    argv.append("-c")
    argv.append(".")

    buildfile = os.path.join("fakevim.sbf")
    argv.append("-b")
    argv.append(buildfile)

    if pyqt.pyqt_version >= 0x040000:
        argv.append("sip/fakevim.sip")
    else:
        argv.append("sip/fakevim.sip")

    os.system(" ".join(argv))

    # Check the result.
    if not os.access(buildfile, os.F_OK):
        sipconfig.error("Unable to create the C++ code.")

    # Generate the Makefile.
    sipconfig.inform("Creating the Makefile for the %s module..." % mname)

    def fix_install(mfile):
        if sys.platform != "darwin" or opts.static:
            return

        mfile.write("\tinstall_name_tool -change libfakevim.%u.dylib %s/libfakevim.%u.dylib $(DESTDIR)%s/$(TARGET)\n" % (FAKEVIM_API_MAJOR, opts.fakevimlibdir, FAKEVIM_API_MAJOR, opts.fakevimmoddir))

    if pyqt.pyqt_version >= 0x040000:
        class Makefile(pyqt4.QtGuiModuleMakefile):
            def generate_target_install(self, mfile):
                pyqt4.QtGuiModuleMakefile.generate_target_install(self, mfile)
                fix_install(mfile)
    else:
        class Makefile(pyqt3.QtModuleMakefile):
            def generate_target_install(self, mfile):
                pyqt3.QtModuleMakefile.generate_target_install(self, mfile)
                fix_install(mfile)

    installs = []
    sipfiles = []

    for s in glob.glob("sip/*.sip"):
        sipfiles.append(os.path.join("sip", os.path.basename(s)))

    installs.append([sipfiles, os.path.join(opts.fakevimsipdir, mname)])

    installs.append(("FakeVim.api", os.path.join(opts.fakevimdir, "api", "python")))

    # PyQt v4.2 and later can handle MacOS/X universal binaries.
    if pyqt.pyqt_version >= 0x040200:
        makefile = Makefile(
            configuration=pyqt,
            build_file="fakevim.sbf",
            install_dir=opts.fakevimmoddir,
            installs=installs,
            static=opts.static,
            debug=opts.debug,
            universal=pyqt.universal,
            arch=pyqt.arch,
            prot_is_public=opts.prot_is_public,
            deployment_target=pyqt.deployment_target
        )
    else:
        makefile = Makefile(
            configuration=pyqt,
            build_file="fakevim.sbf",
            install_dir=opts.fakevimmoddir,
            installs=installs,
            static=opts.static,
            debug=opts.debug
        )

    if fakevim_define:
        makefile.extra_defines.append(fakevim_define)

    makefile.extra_include_dirs.append(opts.fakevimincdir)
    makefile.extra_lib_dirs.append(opts.fakevimlibdir)
    makefile.extra_libs.append("fakevim")

    makefile.generate()


def main(argv):
    """Create the configuration module module.

    argv is the list of command line arguments.
    """
    global pyqt

    # Check SIP is new enough.
    if "snapshot" not in pyqt.sip_version_str:
        if pyqt.sip_version < sip_min_version:
            sipconfig.error("This version of FakeVim requires SIP v%s or later" % sipconfig.version_to_string(sip_min_version))

    # Parse the command line.
    global opts

    p = create_optparser()
    opts, args = p.parse_args()

    if args:
        p.print_help()
        sys.exit(2)

    # Provide defaults for platform-specific options.
    if sys.platform == 'win32':
        opts.prot_is_public = False

    if opts.not_dll:
        global fakevim_define
        fakevim_define = ""

    # Set the version of PyQt explicitly.
    global qt_data_dir

    if opts.pyqt_major == 4:
        if pyqt4 is None:
            sipconfig.error("PyQt v4 was specified with the -p argument but doesn't seem to be installed.")
        else:
            pyqt = pyqt4.Configuration()
            qt_data_dir = pyqt.qt_data_dir
    elif opts.pyqt_major == 3:
        if pyqt3 is None:
            sipconfig.error("PyQt v3 was specified with the -p argument but doesn't seem to be installed.")
        else:
            pyqt = pyqt3.Configuration()
            qt_data_dir = pyqt.qt_dir
    elif opts.pyqt_major >= 0:
        sipconfig.error("Specify either 3 or 4 with the -p argument.")

    # Now we know which version of PyQt to use we can set defaults for those
    # arguments that weren't specified.
    if opts.fakevimmoddir is None:
        opts.fakevimmoddir = pyqt.pyqt_mod_dir

    if opts.fakevimincdir is None:
        opts.fakevimincdir = pyqt.qt_inc_dir

    if opts.fakevimlibdir is None:
        opts.fakevimlibdir = pyqt.qt_lib_dir

    if opts.fakevimsipdir is None:
        opts.fakevimsipdir = pyqt.pyqt_sip_dir

    if opts.fakevimdir is None:
        opts.fakevimdir = os.path.join(qt_data_dir, "fakevim")

    # Check for FakeVim.
    check_fakevim()

    # Tell the user what's been found.
    inform_user()

    # Generate the code.
    generate_code()


###############################################################################
# The script starts here.
###############################################################################

if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        raise
    except:
        sys.stderr.write(
"""An internal error occured.  Please report all the output from the program,
including the following traceback, to .
""")
        raise
