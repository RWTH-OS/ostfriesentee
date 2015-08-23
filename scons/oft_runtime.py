# oft_runtime.py
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
#
# This file is part of Ostfriesentee.
#
# Ostfriesentee is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ostfriesentee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ostfriesentee.  If not, see <http://www.gnu.org/licenses/>.

import os

"""
# Ostfriesentee Runtime

This tool includes a pseudo builder that describes to scons how to
build the ostfriesentee runtime and returns a list of libraries,
that you need to link.
"""

def ostfriesentee_runtime_method(env, oft_libraries):
	if not isinstance(oft_libraries, list):
		oft_libraries = [oft_libraries]

	libs = env.SConscript(os.path.join(env['OFT_ROOT'], 'vm', 'SConscript'), exports = 'env')

	infusions = []
	for lib in oft_libraries:
		lib_di  = os.path.join(env['OFT_BUILDPATH'], 'lib', lib, '{}.di'.format(lib))
		lib_inc = os.path.join(env['OFT_BUILDPATH'], 'lib', lib)
		lib_a   = os.path.join(env['OFT_BUILDPATH'], 'lib', lib, 'lib{}.a'.format(lib))
		infusions.append(lib_di)
		env.Append(CPPPATH = lib_inc)
		libs.append(env.File(lib_a))

	generated_path = os.path.join(env['OFT_BUILDPATH'], 'generated')
	archive = env.Command(os.path.join(generated_path, 'di_lib_archive.ar'), infusions, "ar rcf $TARGET $SOURCES")
	di_c_array = env.CArray(os.path.join(generated_path, 'di_lib_archive.c'), archive)

	env.Append(CPPPATH = env['OFT_VM_INCLUDE'])

	return [di_c_array] + libs


def generate(env):
	env.AddMethod(ostfriesentee_runtime_method, 'OstfriesenteeRuntime')

def exists(env):
	return 1
