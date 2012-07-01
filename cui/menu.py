#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget
from .common import *

class menu( widget ):
	"""
	Widget to show a menu with a list of options

	Inherited Methods:
	hide( self )
	show( self )
	getPanel( self )
	getWindow( self )
	resize( self, height, width, y0=None, x0=None )
	clear( self )
	focus( self )
	"""

	##########
	# Option type subclasses
	##########

	class label( object ):#{{{
		"""
		draw text without an option
		"""
		def __init__( self, window, message, just = None, mode = None ):#{{{
			"""
			Construct label

			arguments:
			window -- display window
			message -- string to show
			just -- how to justify message (default = left)
			mode -- curses mode option to display with (default = curses.A_NORMAL)
			"""
			self.window = window
			self.message = message
			if just == None:
				self.just = "left"
			else:
				self.just = just
			if mode == None:
				self.mode = curses.A_NORMAL
			else:
				self.mode = mode
			self.focused = False#}}}

		def display( self, y, x, width ):#{{{
			"""
			Draws the message on screen

			arguments:
			y -- row number to draw on
			x -- column to begin printing on
			width -- maximum allowable width
			"""
			if width < 1:
				return

			if self.just == "center":
				msg = self.message[:width].center( width )
			elif self.just == "right":
				msg = self.message[:width].rjust( width )
			else:
				msg = self.message[:width].ljust( width )

			self.window.addstr( y, x, msg, self.mode )#}}}
		
		def handleInput(self, key):#{{{
			"""
			Handle keypress event

			arguments:
			key -- ord(c) of key pressed
			"""
			return#}}}
		#}}}

	class toggle( object ):#{{{
		"""
		A simple boolean flipper
		"""

		def __init__( self, window, title, getValue, setValue ):#{{{
			"""
			Construct toggler

			arguments:
			window -- display window
			title -- string to show
			getValue -- function returning current value
			setValue -- function of one variable to set value
			"""
			self.window = window
			self.title = title
			self.getValue = getValue
			self.setValue = setValue
			self.focused = False#}}}

		def display( self, y, x, width ):#{{{
			"""
			Draws the option on screen

			arguments:
			y -- row number to draw on
			x -- column to begin printing on
			width -- maximum allowable width
			"""
			if width < 5:
				return

			if self.getValue():
				msg = '(X) ' + self.title
			else:
				msg = '( ) ' + self.title

			if self.focused:
				mode = curses.A_REVERSE
			else:
				mode = curses.A_NORMAL

			self.window.addstr( y, x, msg[:width].ljust( width ), mode )#}}}

		def handleInput(self, key):#{{{
			if key in KEY_LAUNCH or key in KEY_ACTION:
				self.setValue( not self.getValue() )#}}}
		#}}}

	##########
	# Main Widget
	##########

	def __init__(self, window):#{{{
		"""
		Create option holders

		arguments:
		window -- the curses window of the widget
		"""
		self.options = []

		## Position variables
		self.row = 0
		self.firstrow = 0
		self.maxrow = 0

		super( menu, self ).__init__( window )#}}}
	
	def display( self ):#{{{
		"""
		Draw all widgets
		"""
		w = self.width - 2
		index = self.firstrow
		y = 0
		while index < self.maxrow and y < self.height:
			option = self.options[ index ]
			option.focused = True if index == self.row else False
			option.display( y, 1, w )
			index += 1
			y += 1
		self.window.nooutrefresh()#}}}

	def handleInput( self, key ):#{{{
		"""
		Handle keyinput

		arguments:
		key -- ord(c) for character pressed
		"""
		if key in KEY_UP:
			self.move( -1 )
		if key in KEY_DOWN:
			self.move( 1 )
		if key in KEY_ACTION:
			self.options[ self.row ].handleInput( key )
			self.display()
		#}}}

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
		if self.maxrow == 0 or self.row < 0:
			self.row = 0
			if self.firstrow != 0:
				self.firstrow = 0

		## End of list?
		if self.row >= self.maxrow:
			self.row = self.maxrow-1

		## Scroll down?
		if self.row - self.firstrow > self.height - 2:
			self.firstrow = self.row - self.height + 2

		## Scroll up?
		if self.row < self.firstrow:
			self.firstrow = self.row

		self.display()#}}}

	def addLabel( self, message, just = None, mode = None ):#{{{
		"""
		Frontend to Construct and add a label

		arguments:
		message -- displayed string
		just -- justification of message (default = left)
		mode -- curses display mode (default = curses.A_NORMAL)
		"""
		label = self.label( self.window, message, just, mode)
		self.options.append( label )
		self.maxrow += 1#}}}

	def addToggleOption( self, title, getValue, setValue ):#{{{
		"""
		Frontend to Construct and add a toggle option

		arguments:
		title -- displayed string
		getValue -- function returning boolean
		setValue -- function of boolean which sets option
		"""
		toggle = self.toggle( self.window, title, getValue, setValue )
		self.options.append( toggle )
		self.maxrow += 1#}}}
