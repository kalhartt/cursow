#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget
from .common import *

class tabbedContainer(widget):
	"""
	Container widget with a tab-bar at the top
	and the displayed subwiget in the main window
	other widgets are hidden.
	tabbedContainer will intercept tab keys on focus
	and passthrough the rest to subwidget

	Inherited methods:
	getPanel( self )
	getWindow( self )
	"""

	def __init__(self, window):#{{{
		"""
		Create container window/panel
		and lists for widgets

		arguments:
		window -- the curses window of the widget
		"""
		super( tabbedContainer, self ).__init__( window )

		self.tab = 0
		self.tabNames = []
		self.tabWidgets = [] #}}}

	def hide(self):#{{{
		"""
		Hide the widget's panel
		panel.update_panels() must be done manually after
		"""
		if not self.visible:
			return
		self.visible = False
		self.panel.bottom()
		self.panel.hide()
		self.tabWidgets[ self.tab ].hide() #}}}

	def show(self):#{{{
		"""
		Show the widget's panel
		panel.update_panels() must be done manually after
		"""
		if len(self.tabNames) == 0 or self.visible:
			return
		self.visible = True
		self.panel.top()
		self.panel.show()
		self.tabWidgets[ self.tab ].show()
		self.display()#}}}

	def display(self):#{{{
		"""
		Draws tab-bar at top and window border
		"""
		self.window.move(1,0)
		self.window.clrtoeol()
		self.window.box()
		width = (self.width - len(self.tabNames) - 3) / len( self.tabNames )
		for n in xrange(len(self.tabNames)):
			mode = curses.A_REVERSE if n == self.tab else curses.A_NORMAL
			self.window.addstr( 1, 2+n+n*width, self.tabNames[n][:width].center(width), mode)
		self.window.nooutrefresh()#}}}

	def clear(self):##{{{
		"""
		Clear the widget's display
		"""
		for widget in self.tabWidgets:
			widget.clear()
		super( tabbedContainer, self ).clear()#}}}

	def resize(self, height, width, y0=None, x0=None):#{{{
		"""
		Resize and/or move the window

		arguments:
		height -- resized height
		width -- resized width
		y0 -- y coord of new top-left corner (default = unchanged)
		x0 -- x coord of new top-left corner (default = unchanged)
		"""
		super( tabbedContainer, self ).resize( height, width, y0, x0 )
		h, w, y, x = self.getSubwinDimensions()
		for widget in self.tabWidgets:
			widget.resize( h, w, y, x ) #}}}

	def getSubwinDimensions(self):#{{{
		"""
		Helper function for container location/size
		"""
		return ( self.height-3, self.width-2, self.y0+2, self.x0+1 )#}}}

	def addWidget(self, title, widget):#{{{
		"""
		add a widget with a given title to the container

		arguments:
		title -- distinct name of the widget to be displayed
		widget -- widget (not an instance thereof) to be added
		returns:
		widget -- reference to created widget
		"""
		if title in self.tabNames:
			raise cuiException( 'addWidget %s failed: Name already exists' % title )

		h, w, y, x = self.getSubwinDimensions()
		win = curses.newwin( h, w, y, x )
		wid = widget( win )
		self.tabNames.append( title )
		self.tabWidgets.append( wid )
		return wid#}}}

	def getWidget(self, title):#{{{
		"""
		Return the widget instance associated
		with a given title

		arguments:
		title -- title of desired widget
		"""
		indx = self.tabNames.index( title )
		return self.tabWidget( indx )#}}}
	
	def delWidget(self, title):#{{{
		"""
		Remove a widget from the container

		arguments:
		title -- title of widget to remove
		"""
		indx = self.tabNames.index( title )
		self.tabNames.remove( indx )
		self.navigate(0)#}}}
	
	def navigate(self, n):#{{{
		"""
		Switches tabs a given amount

		argument:
		n -- number of tabs to move right
		"""
		if n == 0:
			return
		self.tabWidget[ self.tab ].hide()
		self.tab = (self.tab+n)%len(self.tabNames)#}}}

	def focus(self):#{{{
		"""
		Handle keyboard input
		"""
		while True:
			key = self.window.getch()

			if key in KEY_QUIT:
				return
			else:
				self.handleInput( key )
			curses.doupdate()#}}}

	def handleInput(self, key):#{{{
		"""
		Handle a single keypress
		or passthrough to focused subwidget

		arguments:
		key -- ord(key) of the pressed key
		"""
		if key == KEY_TABNEXT:
			self.navigate( 1 )
			return
		if key == KEY_TABPREV:
			self.navigate( -1 )
			return
		if self.tabWidgets:
			self.tabWidgets[ self.tab ].handleInput( key )#}}}
