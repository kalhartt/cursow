#!/usr/bin/env python2
import curses
from curses import panel
from .widget import widget
from .common import *
import sys

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

	class listBox( object ):#{{{
		"""
		Switch through multiple settings
		"""

		def __init__( self, window, title, getValue, incValue ):#{{{
			"""
			Construct toggler

			arguments:
			window -- display window
			title -- string to show
			getValue -- function returning current value
			incValue -- function incrementing value by amount n
			"""
			self.window = window
			self.title = title
			self.getValue = getValue
			self.incValue = incValue
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
			
			msg = self.title + ': ' + self.getValue()

			if self.focused:
				mode = curses.A_REVERSE
			else:
				mode = curses.A_NORMAL

			self.window.addstr( y, x, msg[:width].ljust( width ), mode )#}}}

		def handleInput(self, key):#{{{
			"""
			handle key input

			arguments:
			key -- ord(ch) of key pressed
			"""
			if key in KEY_LEFT:
				self.incValue(-1)
			elif key in KEY_RIGHT:
				self.incValue(1)
			elif key in KEY_LAUNCH or key in KEY_ACTION:
				self.incValue(1)#}}}
		#}}}

	class inputBox( object ):#{{{
		"""
		line input widget with optional label
		"""
		def __init__( self, window, getValue, setValue, label = None):#{{{
			"""
			Construct label

			arguments:
			window -- display window
			getValue -- function returning string to show in input box
			setValue -- function of string to set value to
			label -- label shown left of inputbox (default = blank)
			"""
			self.window = window
			self.label = '' if label == None else label+': '
			self.getValue = getValue
			self.setValue = setValue
			self.focused = False

			## Display Variables
			self.pos = 0
			self.firstpos = 0
			self.message = self.getValue()
			#}}}

		def display( self, y, x, width ):#{{{
			"""
			Draws the inputBox on screen

			arguments:
			y -- row number to draw on
			x -- column to begin printing on
			width -- maximum allowable width
			"""
			## Remember settings
			self.y = y
			self.x = x
			self.width = width

			mode = curses.A_REVERSE if self.focused else curses.A_NORMAL
			msg = self.label + self.message
			self.window.addstr( y, x, msg[:width].ljust( width ), mode )
			self.window.nooutrefresh()#}}}
		
		def focusDisplay( self ):#{{{
			"""
			Initial display when entering input mode
			"""
			msg1 = self.label + self.message[ self.firstpos:self.pos ]
			try:
				msg2 = self.message[ self.pos ]
				if msg2 == '': msg2 = ' '
			except IndexError:
				msg2 = ' '
			msg3 = self.message[ self.pos+1: ]

			width = self.width
			x = self.x
			
			self.window.addstr( self.y, x, msg1[:width], curses.A_NORMAL )
			width -= len( msg1 )
			x += len( msg1 )
			if width <= 0: return

			self.window.addstr( self.y, x, msg2[:width], curses.A_REVERSE )
			width -= len( msg2 )
			x += len( msg2 )
			if width <= 0: return

			self.window.addstr( self.y, x, msg3[:width].ljust(width), curses.A_NORMAL )
			self.window.nooutrefresh()#}}}

		def focus( self ):#{{{
			"""
			Focus widget and take all input
			#TODO - fix so screen-resizes caught are sent back up
			"""
			self.message = self.getValue()
			self.focusDisplay()

			while True:
				curses.doupdate()
				key = self.window.getch()
				
				if key == curses.KEY_LEFT:
					self.moveLeft()

				elif key == curses.KEY_RIGHT:
					self.moveRight()

				elif key == curses.KEY_HOME:
					sys.stderr.write( 'Move to Home\n' )
					self.pos = 0
					self.firstpos = 0
					self.focusDisplay()

				elif key == curses.KEY_END:
					sys.stderr.write( 'Move to End\n' )
					self.pos = len( self.message )
					self.firstpos = len( self.message ) - self.width + len( self.label ) + 1
					if self.firstpos <= 0: self.firstpos = 0
					self.focusDisplay()

				elif key == curses.KEY_BACKSPACE or key == 127:
					if self.pos == len( self.message ) and self.firstpos > 0:
						self.firstpos -= 1
					sys.stderr.write( 'Backspace Character\n' )
					self.message = self.message[:self.pos-1] + self.message[self.pos:]
					self.pos -= 1
					if self.pos < 0: self.pos = 0
					self.focusDisplay()

				elif key == curses.KEY_DC:
					sys.stderr.write( 'Deleting Character\n' )
					self.message = self.message[:self.pos] + self.message[self.pos+1:]
					if self.pos > len( self.message ): self.pos = len(self.message)
					self.focusDisplay()

				elif key == curses.KEY_ENTER or key == ord( '\n' ):
					sys.stderr.write( 'Setting input mode OFF\n' )
					break

				elif key in range(32, 255):
					sys.stderr.write( 'Adding Character %s\n' % chr(key) )
					self.message += chr(key) 
					self.moveRight()
				
				sys.stderr.write('\n')

			self.setValue( self.message )
			self.display( self.y, self.x, self.width )#}}}

		def moveLeft( self ):#{{{
			"""
			Helper function to move input left
			"""
			if self.pos <= 0:
				self.pos = 0
				return

			if self.pos < self.firstpos:
				self.firstpos = self.pos

			try:
				c1 = self.message[ self.pos ]
			except IndexError:
				c1 = ' '
			c2 = self.message[ self.pos-1 ]
			x1 = self.x + len( self.label ) + self.pos - self.firstpos
			self.pos -= 1
			self.window.addstr( self.y, x1, c1, curses.A_NORMAL)
			self.window.addstr( self.y, x1-1, c2, curses.A_REVERSE)
			#}}}

		def moveRight( self ):#{{{
			"""
			Helper function to move input right
			"""
			if self.pos >= len( self.message ):
				self.pos = len( self.message )
				return
			
			self.pos += 1
			overflow = self.pos - self.firstpos + 1 - self.width + len( self.label )
			sys.stderr.write( 'Overflow %d\n' % overflow )
			if overflow > 0:
				self.firstpos += overflow
				self.focusDisplay()
				return

			c1 = self.message[ self.pos-1 ]
			try:
				c2 = self.message[ self.pos ]
			except IndexError:
				c2 = ' '
			x1 = self.x + len( self.label ) + self.pos - self.firstpos
			self.window.addstr( self.y, x1-1, c1, curses.A_NORMAL)
			self.window.addstr( self.y, x1, c2, curses.A_REVERSE)
			#}}}

		def handleInput(self, key):#{{{
			"""
			Handle keypress event

			arguments:
			key -- ord(c) of key pressed
			"""
			if key in KEY_ACTION or key in KEY_LAUNCH: self.focus() #}}}

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
		if not self.options:
			return

		elif key in KEY_UP:
			self.move( -1 )

		elif key in KEY_DOWN:
			self.move( 1 )

		else:
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
		self.maxrow += 1
		return label#}}}

	def addToggle( self, title, getValue, setValue ):#{{{
		"""
		Frontend to Construct and add a toggle option

		arguments:
		title -- displayed string
		getValue -- function returning boolean
		setValue -- function of boolean which sets option
		"""
		toggle = self.toggle( self.window, title, getValue, setValue )
		self.options.append( toggle )
		self.maxrow += 1
		return toggle#}}}

	def addListBox( self, title, getValue, incValue ):#{{{
		"""
		Frontend to Construct and add a toggle option

		arguments:
		title -- displayed string
		getValue -- function returning string representing value
		incValue -- function incrementing value by n
		"""
		listBox = self.listBox( self.window, title, getValue, incValue )
		self.options.append( listBox )
		self.maxrow += 1
		return listBox#}}}
	
	def addInputBox( self, getValue, setValue, label=None ):#{{{
		"""
		Frontend to Construct and add a inputBox

		arguments:
		getValue -- function returning string to show in input box
		setValue -- function of string to set value to
		label -- displayed string before inputbox
		"""
		inputBox = self.inputBox( self.window, getValue, setValue, label )
		self.options.append( inputBox )
		self.maxrow += 1
		return inputBox#}}}
