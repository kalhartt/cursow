#!/usr/bin/env python2
import curses

class statusBar(object):
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

class column(object):
	def __init__(self, width, data, sort, title):
		self.w = width
		self.data = data # function to return display data, ie: data = lambda x: x.name
		self.sort = sort # key function for sorted()
		self.title = title

class serverList(object):
	def __init__(self, parwin): ##{{{
		h, w = parwin.getmaxyx()
		self.w = w-2
		self.h = h-2
		self.win = parwin.subwin( self.h, self.w, 1, 1)
		self.win.clear()
		## Item containers
		## items holds each server
		## ditems holds currently displayed servers
		self.items = []
		self.ditems = {}
		self.pos = 0
		self.firstrow = 0
		self.reverse = False
		self.sortcol = 5

		## Make columns
		col0 = column(3, lambda x: '%03d' % x.ping, lambda x: x.ping, 'png')
		col1 = column(5, lambda x: '%s/%s' % (x.clients, x.maxclients), lambda x: x.clients, 'plyrs')
		col2 = column(int(0.2*(self.w-13)), lambda x: x.map, lambda x: x.map.lower(), 'map')
		col3 = column(int(0.2*(self.w-13)), lambda x: x.mod, lambda x: x.mod.lower(), 'mod')
		col4 = column(int(0.2*(self.w-13)), lambda x: x.gametype, lambda x: x.gametype.lower(), 'gametype')
		col5 = column(int(0.4*(self.w-13)), lambda x: x.name, lambda x: x.name.lower(), 'name')
		self.columns = [ col0, col1, col2, col3, col4, col5 ]
		## }}}
	
	def add(self, item): ## {{{
		self.items.append( item )
		self.sort()
		## }}}

	def clear(self): ##{{{
		self.win.move( 1, 0 )
		self.win.clrtobot()
		self.pos = 0
		self.firstrow = 0
		self.items = []
		self.ditems = {}
		self.disp()
		## }}}

	def disp(self): ##{{{
		y0 = self.firstrow
		for y in range(self.h-2):
			if y0+y >= len(self.items):
				break

			item = self.items[y0+y]
			if item == self.ditems.get(y, ''):
				continue
			else:
				self.ditems[y] = item

			x = 0
			mode = curses.A_REVERSE * ( y == self.pos )
			self.win.addstr(1+y,0, ' '*self.w, mode)

			for col in self.columns:
				self.prnt(1+y, x, col.w, col.data( item ), mode)
				x += col.w+1
		self.win.noutrefresh()
		## }}}
	
	def move(self, n): ##{{{
		self.pos += n

		if self.pos >= len(self.items):
			## End of list, does not reach bottom of window
			self.ditems[self.pos-n] = ''
			self.pos = len(self.items)-1
			self.ditems[self.pos] = ''
		elif self.pos > self.h-3:
			## Bottom of window, do we scroll?
			if self.firstrow + self.h-3 < len(self.items):
				## we can scroll
				self.firstrow += min( len(self.items) - self.firstrow-self.h+2 , self.pos-self.h+3 )
				self.pos = self.h - 3
				self.ditems = {}
			else:
				## cannot scroll
				self.ditems[self.pos-n] = ''
				self.pos = self.h-3
				self.ditems[self.pos] = ''
		elif self.pos < 0:
			## Top of window, do we scroll?
			if self.firstrow > 0:
				## we can scroll
				self.firstrow -= min( self.firstrow , -self.pos )
				self.pos = 0
				self.ditems = {}
			else:
				## cannot scroll
				self.ditems[self.pos-n] = ''
				self.pos = 0
				self.ditems[self.pos] = ''
		else:
			## Normal Move
			self.ditems[self.pos-n] = ''
			self.ditems[self.pos] = ''

		self.disp()
		##}}}

	def sort(self, n=0, rev=False): ##{{{
		if rev:
			self.reverse = not self.reverse
		if n:
			self.sortcol = (self.sortcol + n) % len( self.columns )
		sortkey = self.columns[ self.sortcol ].sort
		self.items = sorted( self.items, key=sortkey, reverse=self.reverse )
		self.prntCol()
		self.disp()
		## }}}
	
	def prnt(self, y, x, w, msg, mode=0): ##{{{
		color = curses.color_pair(1)

		## Print over it
		x2 = n = 0
		while n < len(msg):
			if x2 >= w:
				break
			c = msg[n]
			if c == '^':
				## Found a colorcode marker
				try:
					## Try changing the color
					c2 = msg[n+1]
					color = curses.color_pair( int(c2)+2 )
					n += 2
				except IndexError:
					## failed b/c its the last character, print it
					self.win.addstr(y, x+x2, c, color|mode)
					n += 1
					x2 += 1
				except ValueError:
					## failed b/c next character isn't a nubmer, print it
					self.win.addstr(y, x+x2, c, color|mode)
					n += 1
					x2 += 1
				continue
			## Normal character
			self.win.addstr(y, x+x2, c, color|mode)
			n += 1
			x2 += 1
		## }}}
	
	def prntCol(self): ##{{{
		color = curses.color_pair(1)
		x = 0
		for n in range( len(self.columns) ):
			col = self.columns[n]
			if n == self.sortcol:
				mode = curses.A_REVERSE
			else:
				mode = curses.A_NORMAL
			self.win.addstr( 0, x, col.title[:col.w].ljust(col.w), color|mode )
			x += col.w+1
		self.win.noutrefresh()
		## }}}

class filterPane(object):
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
	
## vim: set ts=4 sw=4 noexpandtab: ##
