#!/usr/bin/env python2

class panFilter(object):
	opts = {
			'instagib' : ['show all', 'show only', 'hide'],
			'gametype' : ['all'],
			}

	def __init__(self, win, opts):
		self.h, self.w = win.getmaxyx()
		self.options = opts
		self.pos = 0
		self.win = win
		self.win.clrtobot()
		self.win.box()
	
	def disp(self, mods, gametypes):
		pass
