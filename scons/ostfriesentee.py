# ostfriesentee.py
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
""" Ostfriesentee Tool
    This is a meta tool, that imports all tools that are needed in order to
    build ostfriesentee projects.
"""

import os
from SCons.Script import ARGUMENTS

def run_program(env, program, parameters=""):
	""" helper method to run an executable as pseudo target """
	return env.Command('run_program', program, '{} {}'.format(program[0].abspath, parameters))

def generate(env):
	# initialize environment globals that other tools rely on
	env.Append(OT_SCONS_TOOLS=os.path.dirname(os.path.abspath(__file__)))

	# initialize logger
	env.Tool('logger')
	log_level = ARGUMENTS.get('--log-level', None)
	if log_level == None:
		log_level = ARGUMENTS.get('-ll', None)
	if log_level == None:
		log_level = 'warn'
	env.SetLogLevel(log_level)

	# load other tools
	env.Tool('oft_java')
	env.Tool('infuser')
	env.Tool('c_array')

	# helper functions
	env.AddMethod(run_program, 'Run')

def exists(env):
	return 1
