#!/usr/bin/env python3
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
This class searches for SConstruct files in the directories specified.
If found, it executes scons and later reports the results.
"""

import os, sys, subprocess

class Checker(object):

	def __init__(self):
		if hasattr(sys.stdout, "isatty") and sys.stdout.isatty() or \
			('TERM' in os.environ and os.environ['TERM']=='ANSI'):
			self.ok   = "\033[0;32m" + "OK"   + "\033[0m"
			self.fail = "\033[0;31m" + "FAIL" + "\033[0m"
		else:
			self.ok   = "OK"
			self.fail = "FAIL"
		self.report = []
		self.everything_ok = True

	def run(self, dirs):
		if not isinstance(dirs, list):
			dirs = [dirs]
		for d in dirs:
			for path, directories, files in os.walk(d):
				if 'SConstruct' in files:
					self._check(path)

	def printreport(self):
		print("\nRESULTS:\n")
		print('\n'.join(self.report))
		if self.everything_ok:
			print("\n{0}!".format(self.ok))
			return 0
		else:
			print("\n{0}!".format(self.fail))
			return 1

	def _check(self, path):
		exitStatus = subprocess.call(['scons', '-Q', '-C', path])
		if exitStatus == 0:
			self.report.append("check: {0} -> {1}".format(path, self.ok))
		else:
			self.report.append("check: {0} -> {1}".format(path, self.fail))
			self.everything_ok = False
