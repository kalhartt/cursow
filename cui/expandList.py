#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget
from .common import *

class expandList(widget):
	"""
	Displays a list of data with columns
	List can be sorted and filtered arbitrarily
	Items in list can be expanded to show subdata

	Display function supports quake color formatting

	Inherited methods:
	hide(self)
	show(self)
	getPanel(self)
	getWindow(self)
	"""

	class column(object):#{{{
		"""
		Column object for columnList

		The columnList class should provide the interface for
		this class. An external class should never have to 
		explicitly interface with this class
		"""
		def __init__(self, width, data, title):#{{{
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
			self.highlight = False#}}}
		
		def setHighlight( self, highlight ):#{{{
			"""
			Highlight column title when displayed

			arguments:
			highlight -- True if title should be in reverse mode, false otherwise
			"""
			self.highlight = highlight#}}}
		#}}}

	class listItem( object ):#{{{
		"""
		class to hold item and its expanded data
		"""
		def __init__( self, item, expdata=[] ):#{{{
			"""
			listItem constructor

			arguments:
			item -- item to be contained
			expdata -- list of strings as expanded data (default = [])
			"""
			self.item = item
			self.expdata = expdata
			self.expanded = False#}}}

		def toggleExpand( self ):#{{{
			"""
			Toggle whether the item is expanded
			"""
			self.expanded = not self.expanded#}}}
		
		#}}}

	def __init__(self, window):#{{{
		"""
		Create item holders and fake filters

		arguments:
		window -- the curses window of the widget
		"""
		## Sort/filter function
		self.sortkey = lambda x: True
		self.filter = lambda x: True

		## Item holders
		self.columns = []
		self.items = []
		self.filteredItems = []

		## Position variables
		self.row = 0
		self.firstrow = 0

		## Display variables
		self.listLength = 0
		self.displayItems = {} # Dictionary is convenience to avoid some invalid-index checks
		self.spacers = 2

		super( expandList, self ).__init__( window )#}}}

	def resize(self, height, width, y0=None, x0=None):#{{{
		"""
		Resize and/or move the window

		arguments:
		height -- resized height
		width -- resized width
		y0 -- y coord of new top-left corner (default = self.y0)
		x0 -- x coord of new top-left corner (default = self.x0)
		"""
		self.scaleColumns()
		super( expandList, self ).resize( height, width, y0, x0 )#}}}

	def display(self):#{{{
		"""
		Draw column headers and items
		Attempts to refresh only what has been updated
		"""
		if not self.columns or not self.filteredItems:
			self.window.move(0, 0)
			self.window.clrtobot()
			self.window.nooutrefresh()
			return
	
		## Print column headers
		x = 1
		for column in self.columns:
			w = column.width if column.width >= 1 else int( column.width * ( self.width - self.spacers ) )
			mode = curses.A_REVERSE * column.highlight
			self.window.addstr( 0, x, column.title[:w].ljust( w ), mode )
			x += w+1

		index = self.firstrow
		y = 1
		while y < self.height:
			if index >= len( self.filteredItems ):
				self.window.move( y , 0 )
				self.window.clrtobot()
				break

			listItem = self.filteredItems[ index ]

			if self.displayItems.get( y, False ) == listItem:
				continue
			else:
				self.displayItems[ y ] = listItem

			mode = curses.A_REVERSE * ( y == self.row+1 )
			self.window.addstr( y, 1, ''.ljust(self.width-2), mode )
			x = 1
			for column in self.columns:
				w = column.width if column.width >= 1 else int( column.width * ( self.width - self.spacers ) )
				self.window.addstr( y, x, column.data(listItem.item)[:w].ljust( w ), mode )
				x += w+1

			#if listItem.expanded:
			#	w = self.width - 4
			#	for expdata in listItem.expdata:
			#		y += 1
			#		if y >= self.height: break
			#		mode = curses.A_REVERSE * ( y == self.row+1 )
			#		self.window.addstr( y, 3, expdata[:w].ljust( w ), mode )

			y += 1
			index += 1

		self.window.nooutrefresh() #}}}

	def clear(self):#{{{
		"""
		Clear the display and mark all rows
		of the list for refresh
		"""
		self.displayItems = {}
		super( expandList , self ).clear()#}}}

	def focus( self ):
		"""
		TODO
		"""
		pass

	def handleInput( self, key ):#{{{
		"""
		Handles a given keypress

		arguments:
		key -- ord(ch) of character pressed
		"""
		if key in KEY_QUIT:
			return
		elif key in KEY_UP:
			self.move( -1 )
		elif key in KEY_UP5:
			self.move( -5 )
		elif key in KEY_PGUP:
			self.move( -self.height + 1 )
		elif key in KEY_DOWN:
			self.move( 1 )
		elif key in KEY_DOWN5:
			self.move( 5 )
		elif key in KEY_PGDOWN:
			self.move( self.height - 1 )
		elif key in KEY_ACTION:
			self.expandSelectedItem()
		self.window.nooutrefresh()#}}}

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

		self.displayItems[ 1 + self.row - self.firstrow ] = False
		self.row += n
		self.displayItems[ 1 + self.row - self.firstrow ] = False

		## Do we even have items? Or is it top of list?
		if not self.filteredItems or self.row < 0:
			if self.firstrow != 0:
				self.displayItems = {}
				self.firstrow = 0
			else:
				self.displayItems[ 1 ] = False
			self.row = 0

		## End of list?
		if self.row >= self.listLength:
			self.row = self.listLength - 1
			self.displayItems[ 1 + self.row ] = False

		## Scroll down?
		if self.row - self.firstrow > self.height - 2:
			self.firstrow = self.row - self.height + 2
			self.displayItems = {}

		## Scroll up?
		if self.row < self.firstrow:
			self.firstrow = self.row
			self.displayItems = {}

		self.display()#}}}
	
	def sort( self ):#{{{
		"""
		Resort/filter the data and update listlength
		"""
		self.filteredItems = sorted( filter( lambda x: self.filter( x.item ), self.items ), key=lambda x: self.sortkey( x.item ) )
		self.listLength = len( self.filteredItems )
		for item in self.filteredItems:
			if item.expanded:
				self.listLength += len( item.expdata )#}}}

	def addItem(self, item, expdata):#{{{
		"""
		Add an item, and resort/display it
		if it matches current filter

		argument:
		item -- item to add
		"""
		newitem = self.listItem( item , expdata ) 
		self.items.append( newitem )
		self.filteredItems.append( newitem )
		self.listLength += 1
		#if self.filter( item ):
		#	self.filteredItems.append( newitem )
		#	self.filteredItems = sorted( self.filteredItems, key=lambda x: self.sortkey( x.item ) )
		#	self.listLength += 1
		self.display()#}}}

	def getItem(self, index):#{{{
		"""
		Return the item at a given index
		from self.items

		arguments:
		index -- index of wanted item
		"""
		return self.items[ index ].item#}}}

	def getItems(self):#{{{
		"""
		Return item list
		"""
		return [ x.item for x in self.items ]#}}}

	def getFilteredItems(self):#{{{
		"""
		Return filtered item list
		"""
		return [ x.item for x in self.filteredItems ]#}}}

	def getSelectedItem(self):#{{{
		"""
		Return currently highlighted item
		"""
		return self.items[ self.row ].item#}}}

	def selectedIndex( self ):#{{{
		"""
		Return index of currently highlighted object
		"""
		indx = 0
		row = 0
		while row <= self.row:
			listItem = self.filteredItems[ indx ]
			if listItem.expanded: row += len( listItem.expdata )
			indx += 1
			row += 1
		return indx#}}}

	def expandSelectedItem( self ):#{{{
		"""
		Expand currently highlighted item
		"""
		item = self.filteredItems[ self.selectedIndex() ]
		if item.expanded:
			self.listLength += len( item.expdata )
		else:
			self.listLength -= len( item.expdata )
		item.toggleExpand()#}}}

	def setFilter( self, filt ):#{{{
		"""
		set the lists filtering function

		arguments:
		filt -- new filter function for list
		"""
		self.filter = filt
		self.sort() #}}}
	
	def setSortKey( self, sortkey ):#{{{
		"""
		set the lists sorting function

		arguments
		sort -- new sort function for list
		"""
		self.sortkey = sortkey
		self.sort() #}}}

	def addColumn( self, width, data, title ):#{{{
		"""
		Wrapper to construct and add a column

		arguments:
		width -- w > 1, then width in pixels, w<1 then percentage free space
		data -- function returning an items value, ie: data = lambda x: x.name
		title -- display title of the column
		"""
		for column in self.columns:
			if column.title == title:
				raise cuiException('addColumn failed: Column with title %s already exists!' % title)
		col = self.column( width, data, title )
		self.columns.append( col )
		self.scaleColumns()#}}}
	
	def highlightColumn( self, title ): #{{{
		"""
		Highlight the column with given title
		All other columns are de-highlighted

		arguments:
		title -- tile of column to highlight
		"""
		for column in self.columns:
			if column.title == title:
				column.setHighlight( True )
			else:
				column.setHighlight( False )##}}}

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
