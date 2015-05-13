# SConscript
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

Import('env')

# local dependencies
env = env.Clone()
env.AppendUnique(JAVACLASSPATH="/usr/share/java/bcel.jar")
# check default Fedora path
if os.path.isfile("/usr/share/java/beust-jcommander.jar"):
	env.AppendUnique(JAVACLASSPATH="/usr/share/java/beust-jcommander.jar")
# check default Ubuntu path
elif os.path.isfile("/usr/share/java/jcommander.jar"):
	env.AppendUnique(JAVACLASSPATH="/usr/share/java/jcommander.jar")
else:
	env.Error("Could not find jcommander.jar")
	exit(1)

# TODO: add manifest builder that turns class path dependencies and other
#       meta data into manifest file!

infuser = env.JavaToJar('build/infuser.jar', ['src', 'MANIFEST.MF'])

Return('infuser')
