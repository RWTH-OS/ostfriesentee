# infuser.py
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
from SCons.Script import SConscript, File, Depends
import SCons.Util

def infusion_action_generator(target, source, env, for_signature):
	flags = {'.dhi': '-h', '.di': '-o', '.h': '-d', '.c': '-c'}
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
	output_templates = ['{}.dhi', '{}.di', 'jlib_{}.c', 'jlib_{}.h']
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

	# 2.) get jar file as scons node
	env['INFUSER_JAR'] = SConscript([sconscript], exports = 'env')[0]

	# 3.) create the infusion builder
	infusion_builder = SCons.Builder.Builder(
#		action = env.Action(infusion_action, infusion_string),
		generator = infusion_action_generator,
		emitter = infusion_emitter,
		target_factory = SCons.Node.FS.Dir,
		source_factory = SCons.Node.FS.Entry)

	env.Append(BUILDERS = { 'Infusion': infusion_builder })

def exists(env):
	return 1
