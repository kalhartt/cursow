#!/usr/bin/env python2
import curses, re, subprocess, os
from curses import panel

escchar = re.compile(r'(\^.)')
stripcol = re.compile(r'(\^[0-9])')

class statusBar(object): ## {{{
	def __init__(self):
		self.win = curses.newwin(1, curses.COLS, curses.LINES-1, 0) 
		self.pan = panel.new_panel(self.win)
		#self.win.bkgdset(ord(' '), curses.color_pair(12))
		self.win.clear()
	
	def disp(self, msg, attr=False):
		self.win.clear()
		if attr:
			self.win.addstr(0,0, msg[:curses.COLS], attr)
		else:
			self.win.addstr(0,0, msg[:curses.COLS])
		panel.update_panels()
		curses.doupdate()
## }}}

class column(object): ##{{{
	def __init__(self, x, w, func, sortkey, title):
		self.x = x # horizontal position
		self.w = w # column width
		self.disp = func # function to return display string
		self.sort = sortkey # function to be key for sorted()
		self.title = title # column title
	## }}}

class serverList(object): ## {{{

	def __init__(self):
		w = self.w = curses.COLS-2
		h = self.h = curses.LINES-3
		self.win = curses.newwin(self.h, self.w, 1,1)
		self.pan = panel.new_panel(self.win)
		self.items = []
		self.pos = 1
		self.firstrow = 0

		## Column locations and widths
		colpng = column(0, 3, lambda x: '%03d' % x.ping, lambda x: x.ping, 'png')
		colplyr = column(4, 5, lambda x: '%02d/%02d' % ( x.clients, x.maxclients), lambda x: x.clients, 'plyrs')
		colmap = column(10, int((w-10)*0.2), lambda x: x.map, lambda x: x.map, 'map')
		colmod = column(11+int((w-10)*0.2), int((w-10)*0.2), lambda x: x.mod, lambda x: x.mod, 'mod')
		colgt = column(12+2*int((w-10)*0.2), int((w-10)*0.2), lambda x: x.gametype, lambda x: x.gametype, 'gametype')
		colname = column(13+3*int((w-10)*0.2), int((w-10)*0.4)-1, lambda x: x.name, lambda x: x.name2, 'name')
		self.columns = [ colpng, colplyr, colmap, colmod, colgt, colname ]
		self.sortcol = 1
		self.reverse = False
	
	def add(self, server):
		self.items.append(server)
		self.sort()
		self.disp()

	def sort(self):
		sortkey = self.columns[ self.sortcol ].sort
		self.items = sorted(self.items, key=sortkey, reverse=self.reverse)
	
	def nextSort(self):
		self.sortcol += 1
		if self.sortcol >= len(self.columns): self.sortcol = 0
		self.sort()
		self.disp()
	
	def reverseSort(self):
		self.reverse = not self.reverse
		self.disp()
	
	def disp(self):
		self.win.clear()

		## Print column headers
		for n in range(len(self.columns)):
			col = self.columns[n]
			if n == self.sortcol:
				mode = curses.A_REVERSE
			else:
				mode = curses.A_NORMAL
			self.win.addstr(0, col.x, col.title[:col.w], mode)

		## Print Columns
		ymax, xmax = self.win.getmaxyx()
		for y in range(1,self.h):
			if self.firstrow+y >= len(self.items):
				break

			server = self.items[self.firstrow + y]
			color = curses.color_pair(1)

			if y == self.pos:
				mode = curses.A_REVERSE
				self.win.insstr(y,0, curses.COLS*' ', color|mode)
			else:
				mode = curses.A_NORMAL

			for col in self.columns:
				msg = col.disp(server)
				lenmsg = len(msg)
				n = x = 0
				while n < col.w and n < lenmsg:
					if msg[n] == '^' and n < lenmsg-1:
						c = msg[n+1]
						if ord(c) < 58 and ord(c) > 47:
							color = curses.color_pair(int(c)+2)
							n += 2
							continue
						elif c == '^':
							self.win.addstr(y, col.x+x, msg[n], color|mode )
							n += 2
							x += 1
							continue
					self.win.addstr(y, col.x+x, msg[n], color|mode )
					n += 1
					x += 1
			y += 1
		panel.update_panels()
		curses.doupdate()
	
	def moveUp(self):
		if self.pos == 1:
			self.firstrow -= 1
			if self.firstrow < 0: self.firstrow = 0
			self.disp()
			return
		self.pos -= 1
		if self.pos < 1: self.pos = 1
		self.disp()

	def moveDown(self):
		if self.pos == self.h-1:
			self.firstrow += 1
			if self.firstrow + self.pos >= len(self.items)-3:
				self.pos -= 1
			self.disp()
			return
		self.pos += 1
		maxy = min( self.h-1, len(self.items) )
		if self.pos > maxy: self.pos = maxy
		self.disp()
	
	def launch(self):
		server = self.items[self.firstrow + self.pos-1]
		args = ['/opt/warsow/warsow', 'connect', '%s:%d' % (server.host, server.port)]
		p = subprocess.Popen(args, stdout=file(os.devnull, 'w'))

## }}}
