#!/usr/bin/env python2
import curses
from curses import panel

class widget( object ):
	"""
	Base widget class for cui widgets
	All widgets require their own window
	and must implement the methods in
	this base class
	"""

	def __init__(self, window):#{{{
		"""
		Assign window and panel to the widget

		arguments:
		window -- the curses window of the widget
		"""
		self.window = window
		self.window.keypad(1)
		self.panel = panel.new_panel( self.window )
		self.panel.bottom()
		self.panel.hide()

		self.y0, self.x0 = window.getbegyx()
		self.height, self.width = window.getmaxyx()
		self.visible = False#}}}
	
	def hide(self):#{{{
		"""
		Hide the widget's panel
		panel.update_panels() must be done manually after
		"""
		if not self.visible:
			return
		self.panel.bottom()
		self.panel.hide()#}}}

	def show(self):#{{{
		"""
		Show the widget's panel
		panel.update_panels() must be done manually after
		"""
		if self.visible:
			return
		self.panel.top()
		self.panel.show()#}}}

	def getPanel(self):#{{{
		"""
		Get widget's associated panel
		"""
		return self.panel#}}}

	def getWindow(self):#{{{
		"""
		Get widget's associated window
		"""
		return self.window#}}}

	def resize(self, height, width, y0=None, x0=None):#{{{
		"""
		Resize and/or move the window

		arguments:
		height -- resized height
		width -- resized width
		y0 -- y coord of new top-left corner (default = unchanged)
		x0 -- x coord of new top-left corner (default = unchanged)
		"""
		self.clear()
		self.height = height
		self.width = width
		self.window.resize( height, width )
		if y0 != None and x0 != None:
			self.y0 = y0
			self.x0 = x0
			self.window.mvwin( y0, x0 ) #}}}

	def display(self):#{{{
		"""
		This function handles the drawing
		All widgets must override this function

		A widget's display method can have unique arguments
		Only call a widget's display method when you know
		what type of widget you are displaying
		"""
		pass#}}}

	def clear(self):#{{{
		"""
		Clear the widget's display
		"""
		self.window.move( 0, 0 )
		self.window.clrtobot()
		self.window.nooutrefresh()#}}}

	def focus(self):#{{{
		"""
		Handles user input to give a widget 'focus'
		This should implement a main loop with getch()
		and return when done.
		"""
		pass#}}}

	def handleInput(self, key):#{{{
		"""
		Handle a single key press, from
		an external source

		While focus implements a main loop,
		and catches all keys
		handleInput is essential so container
		widgets can catch certain keys and pass
		through others

		arguments:
		key -- ord(key) of the key pressed
		"""
		pass#}}}
