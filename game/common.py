#!/usr/bin/env python2
"""
Base classes and functions that
every game plugin must implement
"""
from collections import OrderedDict

##########
# CONSTANTS
##########
NAME = 'Example Game'
COLUMNS = [#{{{
		{
			# 'name' columns header display
			'name' : 'column_example',

			# 'display' is a function returning an items
			# string value for the column
			'display' : lambda x: x.example_display(),

			# 'sort' is a function returning some comparable
			# used as a key for sorted()
			'sort' : lambda x: x.example_sort(),

			# width is column width in chars if positive
			# or a weight value to distribute available if negative
			'width': 1
		},
		{   'name' : 'column_example_2',
			'display' : lambda x: x.example_display_2(),
			'sort' : lambda x: x.example_sort_2(),
			'width': -1
		}
]#}}}

##########
# CLASSES
##########
class Settings(object):
	"""
	Class representing settings for the game
	Its values must be an OrderedDict in self.values

	The methods for setting values are fed into the
	menu via a makeMenu function
	"""

	defaults = OrderedDict([
		('setting1', 'on'),
		('setting2', '0')
		])

	def __init__(self):
		self.values = OrderedDict()
		for key in self.defaults:
			self.values[key] = self.defaults[key]

	def toggle_setting1(self):
		if self.values['setting1'] == 'on':
			self.values['setting1'] = 'off'
		else:
			self.values['setting1'] = 'on'

	def inc_setting2(self):
		self.values['setting2'] = str(int(self.values['setting2'])+1)

	def makeMenu(self, cuimenu):
		"""
		Make the menu 
		"""
		cuimenu.addToggle( 'setting1', lambda: self.values['setting1'] , self.toggle_setting1 )
		cuimenu.addListBox( 'setting2', lambda: self.values['setting2'] , self.inc_setting2 )

class Server(object):
	"""
	Base class for game server objects
	"""

	def __init__(self, identifier, settings):
		"""
		Servers will be initialized with
		the identifier from getServerList()
		and the programs Settings instance
		"""
		pass

##########
# FUNCTIONS
##########

def getServerList():
	"""
	Return a list of objects used to instantiate Server objects
	"""
	return []

if __name__=='__main__':
	sett = Settings( '/home/alex/.cursow_test' )
