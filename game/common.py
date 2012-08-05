#!/usr/bin/env python2
"""
Base classes and functions that
every game plugin must implement
"""

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
	"""
	pass

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
