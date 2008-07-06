# ###################################################
# Copyright (C) 2008 The OpenAnno Team
# team@openanno.org
# This file is part of OpenAnno.
#
# OpenAnno is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import fife
import game.main
from tearingtool import TearingTool
from game.util import livingObject

class IngameKeyListener(livingObject, fife.IKeyListener):
	"""KeyListener Class to process key presses ingame"""

	def begin(self):
		super(IngameKeyListener, self).begin()
		game.main.fife.eventmanager.addKeyListener(self)
		self.keysPressed = []

	def end(self):
		game.main.fife.eventmanager.removeKeyListener(self)
		super(IngameKeyListener, self).end()

	def keyPressed(self, evt):
		keyval = evt.getKey().getValue()
		keystr = evt.getKey().getAsString().lower()
		was = keyval in self.keysPressed
		if not was:
			self.keysPressed.append(keyval)
		if keyval == fife.Key.LEFT:
			if not was: game.main.session.view.autoscroll(-25, 0)
		elif keyval == fife.Key.RIGHT:
			if not was: game.main.session.view.autoscroll(25, 0)
		elif keyval == fife.Key.UP:
			if not was: game.main.session.view.autoscroll(0, -25)
		elif keyval == fife.Key.DOWN:
			if not was: game.main.session.view.autoscroll(0, 25)
		elif keystr == 't':
			game.main.session.view.renderer['GridRenderer'].setEnabled(not game.main.session.view.renderer['GridRenderer'].isEnabled())
		elif keystr == 'x':
			game.main.session.cursor = TearingTool()
		elif keystr == 'd':
			game.main.session.cursor.debug = True
		else:
			return
		evt.consume()

	def keyReleased(self, evt):
		keyval = evt.getKey().getValue()
		try:
			self.keysPressed.remove(keyval)
		except:
			return
		if keyval == fife.Key.LEFT:
			game.main.session.view.autoscroll(25, 0)
		elif keyval == fife.Key.RIGHT:
			game.main.session.view.autoscroll(-25, 0)
		elif keyval == fife.Key.UP:
			game.main.session.view.autoscroll(0, 25)
		elif keyval == fife.Key.DOWN:
			game.main.session.view.autoscroll(0, -25)
