#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget

class statusContainer(widget):
	"""
	Container widget with a statusbar at bottom
	Subwidget is displayed in remaining area
	statusContainer passes focus to subwidget

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
		super( statusContainer, self ).__init__( window )
		self.subwindow = None
		self.widget = None#}}}

	def hide( self ):#{{{
		"""
		Hide the widget's panel
		panel.update_panels() must be done manually after
		"""
		if not self.visible:
			return
		self.visible = False
		self.panel.bottom()
		self.panel.hide()
		if self.widget:
			self.widget.hide()#}}}
		
	def show(self):#{{{
		"""
		Show the widget's panel
		panel.update_panels() must be done manually after
		"""
		if self.visible:
			return
		if self.widget:
			self.widget.show()
		self.visible = True
		self.panel.top()
		self.panel.show()
		self.display()#}}}
	
	def resize(self, height, width, y0=self.y0, x0=self.x0):#{{{
		"""
		Resize and/or move the window

		arguments:
		height -- resized height
		width -- resized width

		keyword arguments:
		y0 -- y coord of new top-left corner
		x0 -- x coord of new top-left corner
		"""
		if self.widget:
			( h, w, y, x ) = self.getSubwinDimensions
			self.widget.resize( h, w, y, x )
		super( statusContainer, self ).resize( height, width, y0, x0 )#}}}

	def display( self, x=0, message, width=self.width, mode=curses.A_NORMAL ):#{{{
		"""
		Draw a status message at the given position with given properties
		defaults to writing rest of line with normal mode

		arguments:
		x -- horizontal position of message (relative to widget window) (default = 0)
		message -- string to be displayed
		width -- printing width allotted to message (default = self.width)
		mode -- display mode (default = curses.A_NORMAL)
		"""
		if x + width > self.width:
			width = self.width - x
		self.window.addstr( self.height-1, x, message[:width].ljust(width), mode )
		self.window.nooutrefresh()#}}}

	def clear( self ):#{{{
		"""
		Clear container and its subwidget
		"""
		if self.widget:
			self.widget.clear()
		super( statusContainer, self ).clear()#}}}

	def focus( self ):#{{{
		"""
		Passthrough focus to subwidget
		"""
		if self.widget:
			self.widget.focus()#}}}

	def handleInput( self, key ):#{{{
		"""
		Passthrough keys to subwidget
		"""
		if self.widget:
			self.widget.handleInput( key )#}}}

	def getSubwinDimensions(self):#{{{
		"""
		Helper function for container location/size
		"""
		return ( self.height-1, self.width, self.y0, self.x0 )#}}}

	def addWidget(self, widget):#{{{
		"""
		Add a widget to the container
		This will override a previous widget if it exists.
		to avoid screen-fighting, do not call display() on
		the previous widget after adding a new one.

		arguments:
		widget -- widget class (not an instance thereof) to be added
		"""
		if not self.subwindow:
			( h, w, y, x ) = self.getSubwinDimensions()
			self.subwindow = curses.newwin( h, w, y, x )
		self.widget = widget( self.subwindow )#}}}
	
	def getWidget(self):#{{{
		"""
		Get the subwidget of the container
		"""
		return self.widget#}}}
