# target.py
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

"""
# Target Tool

This tool provides the Architecture function, which
tries to configure the environment for the user architecture.
"""

import os

def set_arch_amd64(env):
	env.Info("Building for amd64 arch.")
	env['CCFLAGS'] = [
		"-funsigned-char",
		"-Wall",
		"-Wextra",
		"-Wundef",
		"-ggdb"
	]

def set_arch_method(env, arch):
	available_arch = {'amd64': set_arch_amd64}	# ['amd64', 'cortex-m4']

	arch = arch.lower()
	if arch not in available_arch:
		env.Error("Invalid architecture `{}`. Possible values are {}.".format(arch, available_arch.keys()))
		exit(1)

	# add include path with common pattern
	inc = os.path.abspath(os.path.join(env['OFT_ROOT'], 'architecture', arch))
	if not os.path.isdir(inc):
		env.Error("Include directory `{}` for arch `{}` does not exist!".format(inc, arch))
		exit(1)
	env.Append(CPPPATH = [inc])

	return available_arch[arch](env)

def generate(env):
	env.AddMethod(set_arch_method, 'Architecture')

def exists(env):
	return 1
