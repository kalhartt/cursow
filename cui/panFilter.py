#!/usr/bin/env python2

class panFilter(object):
	opts = {
			'instagib' : 'show',
			'gametype' : 'all',
			'full' : 'show',
			'empty' : 'show',
			}

	def __init__(self, win):
		self.h, self.w = win.getmaxyx()
		self.win = win
		self.win.clrtobot()
		self.win.box()
		self.pos = 0
