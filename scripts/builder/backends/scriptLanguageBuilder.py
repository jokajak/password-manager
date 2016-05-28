#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import shutil
from backendBuilder import BackendBuilder

class ScriptLanguageBuilder(BackendBuilder):

	def compileCode (self):
		src = self.sourceFolder()
		dst = self.tempFolder()

		try:
			shutil.copytree(src, dst)
		except:
			pass


	def createPackage (self):
		src = self.tempFolder()
		dst = self.targetFolder()

		try:
			shutil.copytree(src, dst)
		except:
			pass
