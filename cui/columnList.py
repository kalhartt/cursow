#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget

class column(object):
	"""
	Column object for columnList
	"""
	def __init__(self):
		"""
		Column constructor

		arguments:
		width -- w > 1, then width in pixels, w<1 then percentage free space
		data -- function returning an items value, ie: data = lambda x: x.name
		title -- display title of the column
		"""
		self.width = width
		self.data = data
		self.title = title

class columnList(widget):
	"""
	Displays a list of data with columns
	List can be sorted and filtered arbitrarily
	"""

	def __init__(self, window):
		"""
		Create item holders and fake filters

		arguments:
		window -- the curses window of the widget
		"""
		self.items = []
		self.filtered_items = []
		self.displayed_items = {} # Dictionary is convenience to avoid some invalid-index checks
		super( statusContainer, self ).__init__( window )
