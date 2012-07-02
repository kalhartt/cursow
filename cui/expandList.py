#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget
from .common import *

class expandList(widget):
	"""
	Displays a list of data with columns
	List can be sorted and filtered arbitrarily
	Items can be expanded to show a list of strings

	Inherited methods:
	hide(self)
	show(self)
	focus(self)
	getPanel(self)
	getWindow(self)
	"""

	class column(object):#{{{
		"""
		Column object for expandList

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
		self.reversed = False

		## Item holders
		self.columns = []
		self.items = []
		self.filteredItems = []

		## Position variables
		self.row = 0
		self.firstrow = 0
		self.maxrow = 0
		self.paused = False

		## Display variables
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
		if self.paused:
			return

		if not self.columns:
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

		for index in range( len(self.filteredItems) ):
			y = 1 - self.firstrow + index
			if y >= self.height: break

			listItem = self.filteredItems[ index ]

			if self.displayItems.get( y, False ) == listItem:
				continue
			else:
				self.displayItems[ y ] = listItem

			mode = curses.A_REVERSE * ( index == self.row )
			if y > 0:
				self.printColor( y, 1, '', mode=mode)
			x = 1
			if isinstance( listItem, self.listItem ):
				if y > 0:
					for column in self.columns:
						w = column.width if column.width >= 1 else int( column.width * ( self.width - self.spacers ) )
						self.printColor( y, x,  column.data(listItem.item), w, mode )
						x += w+1
			elif y > 0:
				w = self.width - 4
				self.printColor( y, 3, listItem, w, mode )

		y = self.maxrow - self.firstrow + 1
		while y < self.height:
			## self.window.clrtobot() wasn't working for me
			## TODO investigate this
			self.printColor( y, 1, '')
			y += 1

		self.window.nooutrefresh()#}}}

	def printColor(self, y, x, message, width=None, mode=None):#{{{
		"""
		Parse quakestyle color codes and print as told

		arguments:
		y -- location to print
		x -- location to print
		message -- string to parse and print
		width -- allotted space to print (default = till screen end-1)
		mode -- mode to print (default = curses.A_NORMAL)
		"""
		#TODO - handle non-color terminals
		if width == None:
			width = self.width - x - 2
		if mode == None:
			mode = 0
		
		n = 0
		color = curses.color_pair(1)
		while width > 0:
			c = message[n] if n < len( message ) else ' '
			if c == '^' and n+1 < len( message ):
				c2 = message[n+1]
				try:
					color = curses.color_pair( int(c2) + 2 )
					n += 2
				except ValueError:
					self.window.addstr( y, x, c, mode|color )
					n += 1
					width -= 1
					x += 1
			else:
				self.window.addstr( y, x, c, mode|color )
				n += 1
				width -= 1
				x += 1
			#}}}

	def clear(self):#{{{
		"""
		Clear the display and mark all rows
		of the list for refresh
		"""
		self.displayItems = {}
		super( expandList , self ).clear()#}}}

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
			self.expandItem()#}}}

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
		if self.maxrow == 0 or self.row < 0:
			if self.firstrow != 0:
				self.displayItems = {}
				self.firstrow = 0
			else:
				self.displayItems[ 1 ] = False
			self.row = 0

		## End of list?
		if self.row >= self.maxrow:
			self.row = self.maxrow-1
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
		
	def addItem(self, item, expdata=[]):#{{{
		"""
		Add an item, and resort/display it
		if it matches current filter

		argument:
		item -- item to add
		expdata -- string of lists to show when item is expanded (default = [])
		"""
		listItem = self.listItem( item, expdata )
		self.items.append( listItem )
		if self.filter( listItem ):
			self.filteredItems.append( listItem )
			self.maxrow += 1
			self.sort()#}}}

	def getItem(self, index):#{{{
		"""
		Return the item at a given index
		from self.items

		arguments:
		index -- index of wanted item
		"""
		return self.items[ index ].item#}}}

	def expandItem( self ):#{{{
		"""
		toggle expansion of currently selected item
		"""
		index = self.getSelectedIndex()
		listItem = self.filteredItems[ index ]
		if listItem.expanded:
			listItem.expanded = False
			self.filteredItems = self.filteredItems[:index+1] + self.filteredItems[index+1+len(listItem.expdata):]
			self.maxrow -= len( listItem.expdata )
			self.row = index
			self.displayItems[ 1 + self.row - self.firstrow ] = False
		else:
			listItem.expanded = True
			self.filteredItems = self.filteredItems[:index+1] + listItem.expdata + self.filteredItems[index+1:]
			self.maxrow += len( listItem.expdata )
		self.display() #}}}

	def getItems(self):#{{{
		"""
		Return item list
		"""
		return [ x.item for x in self.items ]#}}}

	def getFilteredItems(self):#{{{
		"""
		Return filtered item list
		"""
		result = []
		for listItem in self.filteredItems:
			if isinstance( listItem, self.listItem ):
				result.append( listItem.item )
		return result#}}}

	def getSelectedIndex( self ):#{{{
		"""
		Get index of currently selected item
		"""
		index = self.row
		while not isinstance( self.filteredItems[index] , self.listItem ) and index > -1:
			index -= 1
		return index#}}}

	def getSelectedItem(self):#{{{
		"""
		Return currently highlighted item
		"""
		return self.filteredItems[ self.getSelectedIndex() ].item#}}}

	def setFilter( self, filt ):#{{{
		"""
		set the lists filtering function
		use lambda x: True to show all items

		arguments:
		filt -- new filter function for list
		"""
		self.filter = lambda x: filt( x.item )
		self.sort()#}}}
	
	def setSortKey( self, sortkey ):#{{{
		"""
		set the lists sorting function
		use lambda x: True keep in order added

		arguments
		sortkey -- new sort function for list
		"""
		self.sortkey = lambda x: sortkey( x.item )
		self.sort()#}}}

	def sort( self ):#{{{
		"""
		Sort items by given sortkey and filter
		"""
		self.filteredItems = sorted( filter( self.filter, self.items ), key=self.sortkey, reverse=self.reversed )
		n = 0
		while n < len( self.filteredItems ):
			if isinstance(self.filteredItems[ n ], self.listItem) and self.filteredItems[n].expanded:
				expdata = self.filteredItems[n].expdata
				self.filteredItems = self.filteredItems[:n+1] + expdata + self.filteredItems[n+1:]
				n += len( expdata )
			n += 1
		self.maxrow = len( self.filteredItems )
		self.clear()
		self.display()#}}}

	def reverse( self ):#{{{
		"""
		Reverse the sorting order
		"""
		self.reversed = not self.reversed
		self.sort()#}}}

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
	
	def delColumn( self, title ):#{{{
		"""
		Delete Column with Given title
	
		arguments:
		title -- title of column to delete
		"""
		for column in self.columns:
			if column.title == title:
				self.columns.remove( column )
				return#}}}
	
	def highlightColumnTitle( self, title ): #{{{
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

	def highlightColumnIndex( self, index ): #{{{
		"""
		Highlight the column with given title
		All other columns are de-highlighted

		arguments:
		index -- index of column to highlight
		"""
		for n in range( len( self.columns ) ):
			column = self.columns[n]
			if n == index:
				column.setHighlight( True )
			else:
				column.setHighlight( False )##}}}

	def pause( self ):#{{{
		"""
		Halt all printing to screen
		"""
		self.paused = True#}}}
	
	def unPause( self ):#{{{
		"""
		Resume printing to screen
		and immediately repaint
		"""
		self.clear()
		self.paused = False
		self.display()#}}}

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
