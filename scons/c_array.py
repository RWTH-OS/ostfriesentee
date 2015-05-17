# c_array.py
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

import SCons
import struct, os

c_array_header = """
// WARNING: auto generated from {source}!
//          Do not edit!
#include <stddef.h>
size_t {name}_size = {size};
const unsigned char {name}_data[] = {{
\t
"""

def c_array_action(target, source, env):
	source = source[0].abspath
	target = target[0].abspath

	# read raw source and put bytes into c array
	array = ""
	bytes_in_line = 0
	number_of_bytes = 0
	with open(source, 'rb') as f:
		byte = f.read(1)
		while byte != "":
			next_byte = f.read(1)
			array += "0x{0:02x}".format(struct.unpack('B', byte[0])[0])
			if next_byte != "":
				array += ','
			bytes_in_line += 1
			number_of_bytes += 1
			if bytes_in_line > 6:
				array += "\n\t"
				bytes_in_line = 0
			else:
				array += " "
			byte = next_byte

	sub = {
		'name': os.path.splitext(os.path.basename(target))[0],
		'source': source,
		'size': number_of_bytes
	}

	output = c_array_header.format(**sub) + array + "\n};\n"

	open(target, 'w').write(output)

	return 0

def c_array_string(target, source, env):
	return "CArray: $SOURCE -> TARGET"

def generate(env):
	c_array_builder = SCons.Builder.Builder(
		action = env.Action(c_array_action, c_array_string))
	env.Append(BUILDERS = { 'CArray': c_array_builder })

def exists(env):
	return 1
