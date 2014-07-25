#!/bin/bash
# copy QScintilla's Python/configure*.py into this folder before running this

sed -i \
	-e 's/QSCINTILLA/FAKEVIM/g' \
	-e 's/qscintilla2\?/fakevim/g' \
	-e 's/QScintilla2\?/FakeVim/g' \
	-e 's/QSCI/FAKEVIM/g' \
	-e 's/Qsci/FakeVim/g' \
	-e 's/qsci/fakevim/g' \
	-e 's/_API_MAJOR = 11/_API_MAJOR = 0/g' \
	-e "s/version *= *['\"].\..\..*['\"]/version=None/" \
	-e "s/minimum_sip_version *= *'.\...'/minimum_sip_version = '4.15'/" \
	-e "s/support@riverbankcomputing.com//" \
	-e "s/protected_is_public_is_supported = True/protected_is_public_is_supported = False/" \
	-e 's_sip/.*[345]\.sip_sip/fakevim.sip_' \
	configure*.py

sed -i \
	-e '/# Find .* header files/,/target_configuration.fakevim_version = fakevim_version/d' \
	configure.py

sed -i \
	-e '/# Find .* header files/,/sipconfig.error.*global\.h/d' \
	configure-old.py
