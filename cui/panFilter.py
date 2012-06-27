#!/usr/bin/env python2
import curses
import cui

class panFilter(object):
	optNames = [ 'Ping Servers' , 'Show Favorites', 'Instagib', 'Gametype', 'Mod' ]
	optVals = [ ['true', 'false'], ['true', 'false'], ['show all', 'show only', 'hide'], ['all'], ['all'] ]

	def __init__(self, win, opts):
		self.options = opts
		self.h, self.w = win.getmaxyx()
		self.pos = 0
		self.win = win
		self.win.keypad(1)
		self.win.clrtobot()
		self.win.box()
		self.disp()

	def focus(self):
		while True:
			self.disp()
			curses.doupdate()
			key = self.win.getch()
			if key in cui.KEY_UP:
				self.pos = (self.pos-1)%len( self.optNames )
			if key in cui.KEY_DOWN:
				self.pos = (self.pos+1)%len( self.optNames )
			if key in cui.KEY_LAUNCH:
				self.toggleSetting(1)
			if key in cui.KEY_LEFT:
				self.toggleSetting(-1)
			if key in cui.KEY_RIGHT:
				self.toggleSetting(-1)
			if key in cui.KEY_QUIT or key in cui.KEY_FILTER:
				return
			else:
				self.win.addstr( 1, 2, 'Key: %03d' % key)
	
	def getFilter(self):
		if self.options.getOpt( 'Display' , self.optNames[2]) == 'hide':
			f_insta = lambda x: x.instagib==0
		elif self.options.getOpt( 'Display' , self.optNames[2]) == 'show only':
			f_insta = lambda x: x.instagib==1
		else:
			f_insta = lambda x: True

		if self.options.getOpt( 'Display' , self.optNames[3]) == 'all':
			f_gt = lambda x: True
		else:
			gt = self.options.getOpt( 'Display', 'Gametype' )
			f_gt = lambda x: x.gametype.lower() == gt.lower()

		if self.options.getOpt( 'Display' , self.optNames[4]) == 'all':
			f_mod = lambda x: True
		else:
			mod = self.options.getOpt( 'Display', 'Mod' )
			f_mod = lambda x: x.mod.lower() == mod.lower()
	
		return lambda x: f_insta(x) and f_gt(x) and f_mod(x)

	def disp(self):
		for y in range(len(self.optNames)):
			mode =curses.A_REVERSE if self.pos==y else curses.A_NORMAL 
			name = self.optNames[y]
			self.win.addstr( y+2, 2, '%s: %s'.ljust(25) % ( name, self.options.getOpt( 'Display', name ) ), mode ) 

	def addMod(self, mod):
		indx = self.optNames.index('Mod')
		if mod not in self.optVals[indx]:
			self.optVals[indx] = sorted( self.optVals[indx].append(mod) )

	def addGametype(self, gt):
		indx = self.optNames.index('Gametype')
		if gt not in self.optVals[indx]:
			self.optVals[indx] = sorted( self.optVals[indx].append(gt) )
	
	def toggleSetting(self,n):
		curval = self.options.getOpt( 'Display', self.optNames[self.pos] )
		newval = self.optVals[self.pos][ (self.optVals[self.pos].index( curval )+n)%len(self.optVals[self.pos]) ]
		self.options.setOpt( 'Display', self.optNames[self.pos], newval )
