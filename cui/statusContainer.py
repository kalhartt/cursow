#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget
import sys

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
		self.message = ''
		self.mode = curses.A_NORMAL
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
		self.panel.show() #}}}
	
	def resize(self, height, width, y0=None, x0=None):#{{{
		"""
		Resize and/or move the window

		arguments:
		height -- resized height
		width -- resized width
		y0 -- y coord of new top-left corner (default = unchanged)
		x0 -- x coord of new top-left corner (default = unchanged)
		"""
		sys.stderr.write('Resize Event\n')
		sys.stderr.write('height: %d, width: %d\n' % (self.height, self.width) )
		super( statusContainer, self ).resize( height, width, y0, x0 )
		sys.stderr.write('height: %d, width: %d\n' % (self.height, self.width) )
		if self.widget:
			( h, w, y, x ) = self.getSubwinDimensions()
			self.widget.resize( h, w, y, x )#}}}

	def display( self ):#{{{
		"""
		Draw a status message at the given position with given properties
		defaults to writing rest of line with normal mode
		"""
		width = self.width - 1
		self.window.addstr( self.height-1, 0, self.message[:width].ljust(width), self.mode )
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

		returns:
		created subwidget
		"""
		if not self.subwindow:
			( h, w, y, x ) = self.getSubwinDimensions()
			self.subwindow = curses.newwin( h, w, y, x )
		self.widget = widget( self.subwindow )
		if self.visible:
			self.widget.show()
		return self.widget#}}}
	
	def getWidget(self):#{{{
		"""
		Get the subwidget of the container
		"""
		return self.widget#}}}

	def setMessage(self, message, mode=None):#{{{
		"""
		Set status container message

		arguments:
		message -- mesage to display
		mode -- curses mode to display with
		"""
		self.message = message
		if mode != None:
			self.mode = mode
		self.display()#}}}
	
	def getMessage(self):#{{{
		"""
		get current message
		"""
		return self.message#}}}
