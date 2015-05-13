# SConstruct
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


env = Environment()
env.Append(JAVACFLAGS = ['-encoding', 'utf8', '-Xlint:deprecation', '-Xlint:unchecked'])

(infuser_jar, infuser_classpath, infuser_main)= SConscript(['SConscript'], exports = 'env')

print("WARNING: The infuser.jar will be broken, because of scons' shortcomings.")
print("         http://scons.tigris.org/issues/show_bug.cgi?id=1594")
print("         http://scons.tigris.org/issues/show_bug.cgi?id=2547")

env.Default(infuser_jar)
