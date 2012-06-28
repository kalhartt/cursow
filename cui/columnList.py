#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget

class column(object):
	"""
	Column object for columnList
	"""
	def __init__(self, width, data, title):
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
		self.highlight = False
	
	def setHighlight( self, highlight ):#{{{
		"""
		Highlight column title when displayed

		arguments:
		highlight -- True if title should be in reverse mode, false otherwise
		"""
		self.highlight = highlight#}}}

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

	def __init__(self, window):#{{{
		"""
		Create item holders and fake filters

		arguments:
		window -- the curses window of the widget
		"""

		## Sort/filter function
		self.sort = lambda x: x
		self.filter = lambda x: True

		## Item holders
		self.columns = []
		self.items = []
		self.filtered_items = []

		## Position variables
		self.row = 0
		self.firstrow = 0

		## Display variables
		self.displayed_items = {} # Dictionary is convenience to avoid some invalid-index checks
		self.spacers = 2

		super( statusContainer, self ).__init__( window )#}}}

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

	def display(self):#{{{
		"""
		Draw column headers and items
		Attempts to refresh only what has been updated
		"""
		if not self.columns or not self.filtered_items:
			self.window.move(0, 0)
			self.window.clrtobot()
			curses.nooutrefresh()
			return
	
		## Print column headers
		x = 1
		for column in self.columns:
			w = column.width if column.width >= 1 else int( column.width * ( self.width - self.spacers ) )
			mode = curses.A_REVERSE * column.highlight
			self.window.addstr( 0, x, column.title[:w].ljust( w ), mode )
			x += w+1

		for y in xrange( 1 , self.height ):
			## get item if it exists
			index = self.firstrow + y - 1

			if index >= len( self.filtered_items ):
				self.window.move( y , 0 )
				self.window.clrtobot()
				break
			item = self.filtered_items[ index ]

			if self.displayed_items.get( y, False ) == item:
				continue
			else:
				self.displayed_items[ y ] = item

			mode = curses.A_REVERSE * ( index == self.row )
			x = 1
			for column in self.columns:
				w = column.width if column.width >= 1 else int( column.width * ( self.width - self.spacers ) )
				self.window.addstr( y, x, item.data[:w].ljust( w ), mode )
				x += w+1

		curses.nooutrefresh()#}}}

	def clear(self):#{{{
		"""
		Clear the display and mark all rows
		of the list for refresh
		"""
		self.displayed_items = {}
		super( columnList , self ).clear()#}}}

	def focus( self ):
		"""
		TODO
		"""
		pass

	def handleInput( self ):
		"""
		TODO
		"""
		pass

	def move( self, n ):#{{{
		"""
		Move selection down by amount n
		Negative n moves up, will scroll
		display if necessary

		arguments:
		n -- amount to move by
		"""
		if n == 0:
			return

		self.row += n

		## Do we even have items? Or is it top of list?
		if not self.filtered_items or self.row < 0:
			if self.firstrow != 0:
				self.displayed_items = {}
				self.firstrow = 0
			else:
				self.displayed_items[ 1 + self.row-n - self.firstrow ] = False
				self.displayed_items[ 1 ] = False
			self.row = 0
			return

		## End of list?
		if self.row >= len( self.filtered_items ):
			self.displayed_items[ 1 + self.row - n - self.firstrow ] = False
			self.row = len( self.filtered_items ) - 1
			self.displayed_items[ self.row ] = False

		## Scroll down?
		if self.row - self.firstrow > self.height - 2:
			self.firstrow = self.row - self.height + 2
			self.displayed_items = {}

		## Scroll up?
		if self.row < self.firstrow:
			self.firstrow = self.row
			self.displayed_items = {}#}}}
		
	def addItem(self, item):#{{{
		"""
		Add an item, and resort/display it
		if it matches current filter

		argument:
		item -- item to add
		"""
		self.items.append( item )
		if self.filter( item ):
			self.filtered_items = self.sort( self.filtered_items.append( item ) )
		self.display()#}}}

	def getItem(self, index):#{{{
		"""
		Return the item at a given index
		from self.items

		arguments:
		index -- index of wanted item
		"""
		return self.items[ index ]#}}}

	def getItems(self):#{{{
		"""
		Return item list
		"""
		return self.items#}}}

	def getFilteredItems(self):#{{{
		"""
		Return filtered item list
		"""
		return self.filtered_items#}}}

	def getSelectedItem(self):#{{{
		"""
		Return currently highlighted item
		"""
		return self.items[ self.row ]#}}}

	def setFilter( self, filt ):#{{{
		"""
		set the lists filtering function

		arguments:
		filt -- new filter function for list
		"""
		self.filter = filt
		self.filtered_items = self.sort( filter( self.filter, self.items ) )#}}}
	
	def setSort( self, sort ):#{{{
		"""
		set the lists sorting function

		arguments
		sort -- new sort function for list
		"""
		self.sort = sort
		self.filtered_items = self.sort( self.filtered_items )#}}}

	def addColumn( self, column ):
		pass

	def scaleColumns(self):#{{{
		"""
		Calculate deadspace used
		as spacers between columns
		"""
		self.spacers = 1
		for column in self.columns:
			if column.width >= 1:
				self.spacers += column.width
			self.spacers += 1#}}}
