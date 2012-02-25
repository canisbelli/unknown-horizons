# ###################################################
# Copyright (C) 2012 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
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

from horizons.command.unit import CreateUnit
from horizons.constants import UNITS, BUILDINGS
from horizons.world.component.selectablecomponent import SelectableComponent
from tests.gui import TestFinished, gui_test
from tests.gui.helper import get_player_ship


@gui_test(use_dev_map=True, timeout=120)
def test_ticket_1352(gui):
	"""
	Clicking on a frigate crashes the game.
	"""
	yield # test needs to be a generator for now

	player = gui.session.world.player
	ship = CreateUnit(player.worldid, UNITS.FRIGATE_CLASS, 68, 10)(player)
	x, y = ship.position.x, ship.position.y

	gui.session.view.center(x, y)

	"""
	# low-level selection
	# disabled because it is difficult to select the ship
	gui.cursor_move(x, y)
	gui.cursor_click(x, y, 'left')
	"""

	gui.select([ship])

	yield TestFinished


@gui_test(use_dev_map=True, ai_players=3, timeout=120)
def test_ticket_1368(gui):
	"""
	Selecting a warehouse from an ai player crashes.

	Test runs faster with 3 AI players, because a new settlement is
	founded earlier. It is still pretty slow, but let's care about
	speed later.
	"""
	yield # test needs to be a generator for now

	# Wait until ai has settled down
	world = gui.session.world
	while not world.settlements:
		yield

	ai_warehouse = world.settlements[0].warehouse
	gui.select([ai_warehouse])

	yield TestFinished


@gui_test(use_fixture='ai_settlement', timeout=60)
def test_ticket_1369(gui):
	"""
	Ship tab closed when moving away from another player's warehouse after trading.
	"""
	yield

	ship = get_player_ship(gui.session)
	gui.select([ship])

	# ally players so they can trade
	world = gui.session.world
	for player in world.players:
		if player is not ship.owner:
			world.diplomacy.add_ally_pair( ship.owner, player )

	# move ship near foreign warehouse and wait for it to arrive
	gui.cursor_click(68, 23, 'right')
	while (ship.position.x, ship.position.y) != (68, 23):
		yield

	# click trade button
	gui.trigger('overview_trade_ship', 'trade/action/default')

	# trade widget visible
	assert gui.find(name='buy_sell_goods')

	# move ship away from warehouse
	gui.cursor_click(77, 17, 'right')
	while (ship.position.x, ship.position.y) != (77, 17):
		yield

	# trade widget should not be visible anymore
	assert gui.find(name='buy_sell_goods') is None

	# but the ship overview should be
	assert gui.find(name='overview_trade_ship')

	yield TestFinished


@gui_test(use_dev_map=True, timeout=120)
def test_ticket_1362(gui):
	"""
	Saving a game, loading it again and attempting to save it again will crash.
	"""
	yield

	gui.press_key(gui.Key.F5)	# quicksave
	for i in gui.run(seconds=2):
		yield

	gui.press_key(gui.Key.F9)	# quickload
	while gui.find(name='loadingscreen'):
		yield

	def func():
		yield
		# test for error popup
		assert gui.find(name='popup_window') is None

	# quicksave
	with gui.handler(func):
		gui.press_key(gui.Key.F5)

	yield TestFinished


@gui_test(use_dev_map=True, timeout=120)
def test_ticket_1371(gui):
	"""
	Build related tab becomes invisible.

	 * use uninterrupted building (press shift)
	 * click on lumberjack
	 * click on the 'build related' tab
	 * click on the tree
	 * build a tree

     => tab itself is invisible, but buttons for choosing it aren't
	"""
	yield

	ship = get_player_ship(gui.session)
	gui.select([ship])

	gui.cursor_click(59, 1, 'right')
	while (ship.position.x, ship.position.y) != (59, 1):
		yield

	# Found settlement
	gui.trigger('overview_trade_ship', 'found_settlement/action/default')

	gui.cursor_click(56, 3, 'left')

	gui.trigger('mainhud', 'build/action/default')

	# Build lumberjack
	gui.trigger('tab', 'button_5/action/default')
	gui.cursor_click(52, 7, 'left')

	# Select lumberjack
	# TODO selecting should work when clicking on the map
	settlement = gui.session.world.player.settlements[0]
	lumberjack = settlement.buildings_by_id[BUILDINGS.LUMBERJACK_CLASS][0]
	gui.select([lumberjack])

	# Open build related tab
	gui.trigger('tab_base', '1/action/default')

	# Select tree
	gui.trigger('farm_overview_buildrelated', 'build17/action/default')

	# Plant a tree (without uninterrupted building)
	gui.cursor_click(49, 6, 'left')
	assert gui.find(name='farm_overview_buildrelated')

	# Select tree again and plant it with uninterrupted building
	gui.trigger('farm_overview_buildrelated', 'build17/action/default')
	gui.cursor_click(49, 7, 'left', shift=True)

	# Tab should still be there
	assert gui.find(name='farm_overview_buildrelated')

	yield TestFinished

@gui_test(use_fixture='fife_exception_not_found', timeout=60)
def test_ticket_1447(gui):
	"""
	Clicking on a sequence of buildings may make fife throw an exception.
	"""
	yield

	lumberjack = gui.session.world.islands[0].ground_map[(23, 63)].object
	assert(lumberjack.id == BUILDINGS.LUMBERJACK_CLASS)

	fisher = gui.session.world.islands[0].ground_map[(20, 67)].object
	assert(fisher.id == BUILDINGS.FISHERMAN_CLASS)

	warehouse = gui.session.world.islands[0].ground_map[(18, 63)].object
	assert(warehouse.id == BUILDINGS.WAREHOUSE_CLASS)

	gui.select([fisher])
	fisher.get_component(SelectableComponent).select()
	yield

	fisher.get_component(SelectableComponent).deselect()
	gui.select([lumberjack])
	lumberjack.get_component(SelectableComponent).select()
	yield

	lumberjack.get_component(SelectableComponent).deselect()
	gui.select([warehouse])
	warehouse.get_component(SelectableComponent).select()
	yield # this could crash the game

	yield TestFinished
