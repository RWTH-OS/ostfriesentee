# find_files.py
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
import os

class FileFinder(object):
	def __init__(self, suffix):
		if not isinstance(suffix, list):
			suffix = [suffix]
		self.suffix = self._parse_suffix(suffix)
		# list that contains the absolute paths of all files and directories
		# that where found (this might include unwanted files)
		self.paths_found = []
		# tracks the common path of files found
		self.common_path = None
		# list that contans the SCons.Node.FS.File objects for every file found
		# that had the correct suffix
		self.files_found = []

	def find(self, files):
		# if files is a list, call the find function on every element
		if isinstance(files, list):
			for ff in files:
				self.find(ff)
		# if it's not a list, we can calculate an absolute path
		ff = files
		path = os.path.abspath(str(files))
		# and check if we already found that path
		if path in self.paths_found:
			return
		self.paths_found.append(path)
		# if file is a directory string or a SCons.Node.FS.Dir, call find on its contents
		if isinstance(ff, SCons.Node.FS.Dir) or os.path.isdir(path):
			for ff in os.listdir(path):
				self.find(os.path.join(path, ff))
		# if file is a single file string or SCons.Node.FS.File
		if isinstance(ff, SCons.Node.FS.File) or os.path.isfile(path):
			if not os.path.splitext(path)[1] in self.suffix:
				return
			self.files_found.append(ff)
			# update common path
			if not self.common_path:
				self.common_path = os.path.dirname(path)
			else:
				self.common_path = os.path.commonprefix(
					[self.common_path, os.path.dirname(path)])

	def _parse_suffix(self, suffix_raw):
		""" makes sure that the suffixes are the correct format """
		suffix = []
		for su in suffix_raw:
			su = str(su)
			if not su.startswith('.'):
				su = '.' + su
			suffix.append(su)
		return suffix

def find_files_method(env, files, suffix):
	""" takes either a string/File/Dir or a list of strings/Files/Dirs and
	    searches for source files with the suffix specified.
	"""
	ff = FileFinder(suffix)
	ff.find(files)
	return (ff.files_found, ff.common_path)


def generate(env):
	env.AddMethod(find_files_method, 'FindFiles')

def exists(env):
	return 1
