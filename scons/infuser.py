# infuser.py
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
# Infuser Scons Tool

There are two types of infusion:
The `OstfriesenteeLibrary`, and the `OstfriesenteeApp`.
Only libraries may contain native code. Apps can only rely
on libraries in order to access native code. This is because
it should be possible to load an app at run time, while
a library needs to be compiled into the executable.
"""

import os
from SCons.Script import SConscript, File, Depends
import SCons.Util

def ostfriesentee_library_action(name, source, env):
	""" This is a pseudo builder that tells scons how to generate a
	    `OstfriesenteeLibrary`:
	    * may consist of Java and C sources
	    * may depend on other libraries (specify with env['OFT_LIBS'])
	    * needs to be linked into the executable containing the Ostfriesentee jvm
	    * other libraries as well as apps may depend on it
	    * _input_: *.java, *.c
	    * _output_: *.a, *.di, *.dih
	"""




"""
# TODO: make this less hacky
# make sure to specify lib only once
if 'LIB_BASE_INFUSION' in env and 'LIB_BASE_CLASSES_PATH' in env:
	infusion     = env['LIB_BASE_INFUSION']
	classes_path = env['LIB_BASE_CLASSES_PATH']
	Return('infusion', 'classes_path')

# build java code and run infuser
env_java = env.Clone()
env_java.AppendUnique(JAVACFLAGS = ['-encoding', 'utf8', '-Xlint:deprecation', '-Xlint:unchecked'])
# do not depend on system jars
env_java['JAVABOOTCLASSPATH'] = []
classes_path = os.path.abspath('build/classes')
classes      = env_java.Java(classes_path, 'java')
infusion_res = env_java.Infusion('build/infusion/base', classes)

# split up infusion
infusion_dih = [os.path.abspath(str(f)) for f in infusion_res if str(f).endswith('.dih')]
infusion_di  = [os.path.abspath(str(f)) for f in infusion_res if str(f).endswith('.di')]
infusion_c   = [os.path.abspath(str(f)) for f in infusion_res if str(f).endswith('.c')]
infusion_h   = [os.path.abspath(str(f)) for f in infusion_res if str(f).endswith('.h')]

# build c code
c_env = env.Clone()
c_env.VariantDir(variant_dir='build/base', src_dir='c')
c_env.Append(CPPPATH = [os.path.abspath('./build/infusion/base')])
c_env.Append(CPPPATH = [os.path.abspath('../../../vm/c')])
# TODO: move config somewhere else
c_env.Append(CPPPATH = [os.path.abspath('../../../config/native/c')])
c_env.Append(CPPPATH = [os.path.abspath('../../../architecture/native/c/')])

infusion = c_env.StaticLibrary('build/base', infusion_c + env.Glob('build/base/*.c'))

# add infusion and infusion header as well a c header to target
infusion += infusion_dih + infusion_di + infusion_h

env['LIB_BASE_INFUSION']     = infusion
env['LIB_BASE_CLASSES_PATH'] = classes_path

"""




def infusion_action_generator(target, source, env, for_signature):
	flags = {'.dih': '-h', '.di': '-o', '.h': '-d', '.c': '-c'}
	name = os.path.basename(os.path.dirname(str(target[0])))

	action_str = "java -jar $INFUSER_JAR"

	for tar in target:
		try:
			flag = flags[os.path.splitext(str(tar))[1]]
		except KeyError:
			env.Error("Invalid infusion target `{}`".format(str(tar)))
			exit(1)
		action_str += " {} {}".format(flag, str(tar))

	action_str += " -n {}".format(name)

	return action_str + " $SOURCES"

def infusion_string(target, source, env):
	name = os.path.basename(os.path.dirname(str(target[0])))
	return "Infusing: '{}'".format(name)

def infusion_emitter(target, source, env):
	if len(target) != 1:
		env.Error("Infusion needs exactly one output directory!")
		exit(1)
	target[0].must_be_same(SCons.Node.FS.Dir)

	# derrive infusion path and name
	infusion_path = str(target[0])
	infusion_name = os.path.basename(infusion_path)

	# check source files
	for s in source:
		file_name = str(s)
		if not (file_name.endswith('.class') or file_name.endswith('.dih')):
			env.Error("Infusion source `{}` is neither *.class nor *.dih".format(file_name))
			exit(1)

	# create file targets
	output_templates = ['{}.dih', '{}.di', 'jlib_{}.c', 'jlib_{}.h']
	target = []
	for templ in output_templates:
		path = os.path.join(infusion_path, templ.format(infusion_name))
		file_target = File(path)
		Depends(file_target, env['INFUSER_JAR'])
		target.append(file_target)

	return target, source

def generate(env):
	# 1.) find the infusor directory
	sconscript = os.path.join(env['OT_SCONS_TOOLS'], '..', 'SConscript')
	if not os.path.isfile(sconscript):
		env.Error("Could not find the infuser. `{}` does not exist.".format(sconscript))
		exit(1)

	# 2.) build infusor string
	jar= SConscript([sconscript], exports = 'env')
	env['INFUSER_JAR'] = jar

	# 3.) create the infusion builder
	infusion_builder = SCons.Builder.Builder(
		generator = infusion_action_generator,
		emitter = infusion_emitter,
		target_factory = SCons.Node.FS.Dir,
		source_factory = SCons.Node.FS.Entry)

	env.Append(BUILDERS = { 'Infusion': infusion_builder })

def exists(env):
	return 1
