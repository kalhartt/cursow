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

	Inherited methods:
	hide(self)
	show(self)
	getPanel(self)
	getWindow(self)
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

	def resize(self, height, width, y0=self.y0, x0=self.x0):#{{{
		"""
		Resize and/or move the window

		arguments:
		height -- resized height
		width -- resized width
		y0 -- y coord of new top-left corner (default = self.y0)
		x0 -- x coord of new top-left corner (default = self.x0)
		"""
		self.scaleColumns()
		super( columnList, self ).resize( height, width, y0, x0 )#}}}

	def display(self):
		pass

	def clear(self):#{{{
		"""
		Clear the display and mark all rows
		of the list for refresh
		"""
		self.displayed_items = {}
		super( columnList , self ).clear()#}}}

	def focus( self ):
		pass

	def handleInput( self ):
		pass

	def addItem(self, item):
		pass

	def getItem(self, index):
		pass

	def getItems(self):
		pass

	def getFilteredItems(self):
		pass

	def getSelectedItem(self):
		pass

	def scaleColumns(self):
		pass
