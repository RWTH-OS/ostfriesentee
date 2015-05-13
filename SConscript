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

classes = env.Java('build/classes', 'src')

# WARNING: building jars with scons is somewhat broken, beacause scons
#          is unable to find all *.class files produced by javac and
#          thus, not all *.class files will be added to the .jar
# http://scons.tigris.org/issues/show_bug.cgi?id=1594
# http://scons.tigris.org/issues/show_bug.cgi?id=2547
infuser = env.Jar('build/infuser.jar', classes + ['MANIFEST.MF'])

# return classpath and main class in order to be able to execute the infuser
# without having to use the broken jar
classpath  = list(env['JAVACLASSPATH'])
classpath.append(os.path.abspath('build/classes'))
main_class = "org.csiro.darjeeling.infuser.InfuserCommandLine"

Return('infuser', 'classpath', 'main_class')
