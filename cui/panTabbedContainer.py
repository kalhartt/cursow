#!/usr/bin/env python2
import curses
from curses import panel

class panTabbedContainer(object):

	def __init__(self, window, options):
		self.mainwin = window
		self.mainpan = panel.new_panel( self.mainwin )
		self.mainpan.bottom()
		self.mainpan.hide()
		self.y0, self.x0 = window.getbegyx()
		self.h, self.w = window.getmaxyx()

		self.tab = 0
		self.tabNames = []
		self.tabPanels = []
		self.tabWidgets = []
		self.isShowing = False
		self.options = options

	def addWidget(self, title, widget):
		if title in self.tabNames:
			# TODO raise err here
			# Need to make a cui err class first
			return
		h, w, y, x = self.getSubwinDimensions()
		win = curses.newwin( h, w, y, x )
		pan = panel.new_panel( win )
		pan.bottom()
		pan.hide()
		wid = widget( win, self.options )

		self.tabNames.append( title )
		self.tabPanels.append( pan )
		self.tabWidgets.append( wid )

	def getWidget(self, title):
		indx = self.tabNames.index( title )
		return self.tabWidget( indx )
	
	def delWidget(self, title):
		indx = self.tabNames.index( title )
		self.tabNames.remove( indx )
		self.tabPanels.remove( indx )
		self.navigate(0)
	
	def navigate(self, n):
		self.tab = (self.tab+n)%len(self.tabNames)

	def getSubwinDimensions(self):
		return ( self.h-3, self.w-2, self.y0+2, self.x0+1 )
	
	def getWin(self):
		return self.subwin

	def show(self):
		if len(self.tabNames) == 0 or self.isShowing:
			return
		self.isShowing = True
		self.mainpan.top()
		self.mainpan.show()
		self.tabPanels[ self.tab ].top()
		self.tabPanels[ self.tab ].show()
		panel.update_panels()
		self.disp()

	def hide(self):
		if not self.isShowing:
			return
		self.isShowing = False
		self.mainpan.bottom()
		self.mainpan.hide()
		self.tabPanels[ self.tab ].bottom()
		self.tabPanels[ self.tab ].hide()
		panel.update_panels()

	def disp(self):
		self.mainwin.box()
		width = (self.w - len(self.tabNames) - 1) / 3
		for n in xrange(len(self.tabNames)):
			mode = curses.A_REVERSE if n == self.tab else curses.A_NORMAL
			self.mainwin.addstr( 1, 1+n+n*width, self.tabNames[n][:width].center(width), mode)

		self.mainwin.nooutrefresh()
