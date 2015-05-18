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

import os, re
from SCons.Script import SConscript, File, Depends
import SCons.Util

def ostfriesentee_library_method(env, name, source):
	""" This is a pseudo builder that tells scons how to generate a
	    `OstfriesenteeLibrary`:
	    * may consist of Java and C sources
	    * may depend on other libraries (specify with env['OFT_LIBS'])
	    * needs to be linked into the executable containing the Ostfriesentee jvm
	    * other libraries as well as apps may depend on it
	    * _input_: *.java, *.c
	    * _output_: *.a, *.di, *.dih
	"""
	# check if name is valid and determine buildpath
	if not re.match('[a-zA-Z][a-zA-Z0-9_]*', name):
		env.Error("Invalid name `{}`. Please use C identifier conventions.".format(name))
		exit(1)
	build_path = os.path.join(env['OFT_BUILDPATH'], 'lib', name)

	# build java sources
	java_src = env.FindFiles(source, ".java")[0]
	jar_name = os.path.join(build_path, name + '.jar')
	env_java = env.Clone()
	for lib in env['OFT_LIBS']:
		jar_dep = os.path.join(env['OFT_BUILDPATH'], 'lib', lib, lib + '.jar')
		env_java.AppendUnique(JAVACLASSPATH=jar_dep)
		Depends(jar_name, jar_dep)
	# do not depend on system jars
	env_java['JAVABOOTCLASSPATH'] = []
	jar = env.JavaToJar(os.path.join(build_path, name + '.jar'), java_src)

	# make infusion
	infusion_src = [jar]
	for lib in env['OFT_LIBS']:
		infusion_src.append(os.path.join(env['OFT_BUILDPATH'], 'lib', lib, lib + '.dih'))
	infusion = env.Infusion(build_path, infusion_src)
	def find_suffix(files, suffix):
		return [os.path.abspath(str(ff)) for ff in files if str(ff).endswith(suffix)]
	infusion_dih = find_suffix('.dih')
	infusion_di  = find_suffix('.di')
	infusion_c   = find_suffix('.c')

	# compile native code
	(c_src, c_src_dir) = env.FindFiles(source, ".c")
	c_env = env.Clone()
	# place object files in buildpath
	c_env.VariantDir(variant_dir=build_path, src_dir=c_src_dir)
	c_var_src = []
	for cc in c_src:
		abs_path = os.path.abspath(str(c_src))
		rel = os.path.relpath(c_src_dir, abs_path)
		c_var_src.append(os.path.join(build_path, rel))
	# for infusion_h file
	c_env.AppendUnique(CPPPATH = [buildpath])
	# tell scons how to build static lib
	lib = c_env.StaticLibrary(os.path.join(build_path, name), infusion_c + c_var_src)

	return lib + infusion_di + infusion_dih


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
		if not os.path.splitext(file_name)[1] in ['.class', '.dih', '.jar']:
			env.Error("Infusion source `{}` is neither *.class nor *.dih nor *.jar".format(file_name))
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

	# 4.) add ostfriesentee pseudo builders
	env.AddMethod(ostfriesentee_library_method, 'OstfriesenteeLibrary')

def exists(env):
	return 1
