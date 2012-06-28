#!/usr/bin/env python2
import curses
from curses import panel

class statusContainer(object):

	def __init__(self, window):
		self.mainwin = window
		self.mainpan = panel.new_panel( self.mainwin )
		self.mainpan.bottom()
		self.mainpan.hide()
		self.y0, self.x0 = window.getbegyx()
		self.h, self.w = window.getmaxyx()
