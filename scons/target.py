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

def set_arch_common(env):
	env['CCFLAGS'] = [
		"-funsigned-char",
#		"-Wstrict-prototypes",
		"-Wall",
		"-Werror=maybe-uninitialized",
		"-Wformat",
		"-Wextra",
		"-Wundef",
		"-Winit-self",
		"-Wpointer-arith",
		"-Wunused",
		"-std=c11"
	]

	env['CXXFLAGS'] = [
		"-std=c++11"
	]

def set_arch_amd64(env, arch):
	env.Info("Building for amd64 arch.")
	env.AppendUnique(CCFLAGS = ["-ggdb"])

def set_arch_cortexm(env, arch):
	env.Info("Building for {} arch.".format(arch))

	env['PROGSUFFIX'] = ".elf"

	if arch.endswith('f'):
		mcpu = arch[:-1]
	else:
		mcpu = arch

	# use arm-none-eabi- toolchain
	env['CC'] = "arm-none-eabi-gcc"
	env['CXX'] = "arm-none-eabi-g++"
	env['AS'] = "arm-none-eabi-as"
	env['OBJCOPY'] = "arm-none-eabi-objcopy"
	env['OBJDUMP'] = "arm-none-eabi-objdump"
	env['AR'] = "arm-none-eabi-ar"
	env['NM'] = "arm-none-eabi-nm"
	env['RANLIB'] = "arm-none-eabi-ranlib"
	env['SIZE'] = "arm-none-eabi-size"

	env.AppendUnique(CCFLAGS = [
		"-Os",
		"-gdwarf-2",
		"-mcpu=" + mcpu,
		"-mlittle-endian",
		"-mthumb",
		"-mno-thumb-interwork",
		"-nostartfiles",
		"-ffunction-sections",
		"-fdata-sections",
		"-fno-builtin",
		"-fdiagnostics-color=auto",
	])

	env['LINKFLAGS'] = [
		"-mcpu=" + mcpu,
		"-mthumb",
		"-Wl,--relax",
		"-Wl,--gc-sections",
		"-nostartfiles",
#		"-L$LINKPATH",
#		"-T$LINKFILE",
#		"-Wl,-Map=${TARGET.base}.map,--cref",
	]

def set_arch_method(env, arch):
	available_arch = {
		'amd64'     : ['amd64', set_arch_amd64],
		'cortex-m4f': ['cortex-m', set_arch_cortexm],
		'cortex-m0' : ['cortex-m', set_arch_cortexm]
	}

	arch = arch.lower()
	if arch not in available_arch:
		env.Error("Invalid architecture `{}`. Possible values are {}.".format(arch, available_arch.keys()))
		exit(1)

	# add include path with common pattern
	inc = os.path.abspath(os.path.join(env['OFT_ROOT'], 'architecture', available_arch[arch][0]))
	if not os.path.isdir(inc):
		env.Error("Include directory `{}` for arch `{}` does not exist!".format(inc, arch))
		exit(1)
	env.Append(CPPPATH = [inc])

	# load common settings
	set_arch_common(env)

	# load target specific settings
	return available_arch[arch][1](env, arch)

def generate(env):
	env.AddMethod(set_arch_method, 'Architecture')

def exists(env):
	return 1
