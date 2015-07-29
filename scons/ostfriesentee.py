# ostfriesentee.py
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
# Ostfriesentee Tool
This is a meta tool, that imports all tools that are needed in order to
build ostfriesentee projects.

## Build Directory Layout
One project will be built in one build directory. The layout will look
something like this:

build
    ├── app
    │   └── helloworld
    │       └── helloworld.di
    ├── lib
    │   └── base
    │       ├── base.di
    │       ├── base.dih
    │       ├── base.jar
    │       ├── class
    │       ├── java_lang_String.o
    │       ├── jlib_base.c
    │       ├── jlib_base.h
    │       ├── jlib_base.o
    │       └── libbase.a
    ├── main
    │   ├── main
    │   └── main.o
    └── vm
        └── vm.o
        └── libvm.a
"""

import os
from SCons.Script import ARGUMENTS, Dir

def run_program(env, program, parameters=""):
	""" helper method to run an executable as pseudo target """
	return env.Command('run_program', program, '{} {}'.format(program[0].abspath, parameters))

def format_size(size):
	""" takes size as integer and returns a human readable string """
	return "{} bytes".format(size)

def show_size_action(env, source, target):
	if not isinstance(source, list):
		source = [source]
	data = [(str(ff), format_size(ff.get_size())) for ff in source]
	max_size_chars = max([(len(dd[0]) + len(dd[1])) for dd in data])
	for dd in data:
		padding = max_size_chars - (len(dd[0]) + len(dd[1]))
		print(dd[0] + ": " + (" " * padding) + dd[1])

def show_size(env, source):
	""" helper method to show the size of a number of files """
	aa = env.Action(show_size_action, cmdstr="$OFT_SHOW_SIZE_COMSTR")
	return env.AlwaysBuild(env.Alias('__show_size__', source, aa))

def generate(env):
	# initialize environment globals that other tools rely on
	env['OFT_SCONS_TOOLS'] = os.path.dirname(os.path.abspath(__file__))
	env['OFT_ROOT'] = os.path.abspath(os.path.join(env['OFT_SCONS_TOOLS'], '..'))
	env['OFT_VM_INCLUDE'] = os.path.abspath(os.path.join(env['OFT_ROOT'], 'vm', 'src'))

	# import terminal type to enable gcc/clang to print colored output
	# http://stackoverflow.com/questions/9922521/why-doesnt-clang-show-color-output-under-scons
	env['ENV']['TERM'] = os.environ['TERM']

	# copy path from os environment
	env['ENV']['PATH'] = os.environ['PATH']

	# initialize logger
	env.Tool('logger')
	log_level = ARGUMENTS.get('log-level', None)
	if log_level == None:
		log_level = ARGUMENTS.get('ll', None)
	if log_level == None:
		log_level = 'warn'
	env.SetLogLevel(log_level)

	# load other tools
	env.Tool('find_files')
	env.Tool('oft_java')
	env.Tool('infuser')
	env.Tool('c_array')
	env.Tool('target')

	# helper functions
	env.AddMethod(run_program, 'Run')
	env['OFT_SHOW_SIZE_COMSTR'] = "Size:"
	env.AddMethod(show_size, 'ShowSize')

	# determine build directory
	# this is inspired by the code in `scons/site_tools/xpcc.py`
	# from the `xpcc` microcontroller library project
	if not 'OFT_BUILDPATH' in env:
		env['OFT_BUILDPATH'] = os.path.join(Dir('.').abspath, 'build')
	print(env['OFT_BUILDPATH'])

	# start list of ostfiresentee libraries
	env['OFT_LIBS'] = []

def exists(env):
	return 1
