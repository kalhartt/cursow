#!/usr/bin/env python2

class widStatus(object):
	def __init__(self, parwin):
		y, x = parwin.getmaxyx()
		self.w = x
		self.win = parwin.subwin(y-1, 0)
		self.win.clear()
	
	def disp(self, msg, attr=0):
		self.win.move(0,0)
		self.win.clrtoeol()
		self.win.addstr(0,0, msg[:self.w-1], attr)
		self.win.noutrefresh()
