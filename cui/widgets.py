#!/usr/bin/env python2
import curses, re
from curses import panel

escchar = re.compile(r'(\^.)')
stripcol = re.compile(r'(\^[0-9])')

def colorPrint( win, pos, msg, attr=curses.A_NORMAL ): ## {{{
	## pos = [ y , x , width ]
	msg = re.split( escchar, msg)
	color = curses.color_pair(1)

	w = 0
	for submsg in msg:
		if w > pos[2]:
			break
		if submsg[0] == '^':
			try:
				color = curses.color_pair(int(submsg[1]))
				continue
			except ValueError:
				pass
		win.addstr(pos[0], pos[1]+w, submsg[:pos[2]-w], color)
		w += len(submsg)
	## }}}
	
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
	def __init__(self, x, w, func, title):
		self.x = x # horizontal position
		self.w = w # column width
		self.disp = func # function to return display string
		self.title = title # column title
	## }}}

class serverList(object): ## {{{

	def __init__(self):
		w = curses.COLS-2
		h = curses.LINES-3
		self.win = curses.newwin(h, w, 1,1)
		self.pan = panel.new_panel(self.win)
		self.items = []
		self.pos = 1

		## Column locations and widths
		colpng = column(0, 3, lambda x: '000', 'png')
		colplyr = column(4, 5, lambda x: '%02d/%02d' % ( x.clients, x.maxclients), 'plyrs')
		colmap = column(10, int((w-10)*0.2), lambda x: x.map, 'map')
		colmod = column(11+int((w-10)*0.2), int((w-10)*0.2), lambda x: x.map, 'mod')
		colgt = column(12+2*int((w-10)*0.2), int((w-10)*0.2), lambda x: x.gametype, 'gametype')
		colname = column(13+3*int((w-10)*0.2), int((w-10)*0.4)-1, lambda x: x.name, 'name')
		self.columns = [ colpng, colplyr, colmap, colmod, colgt, colname ]
	
	def add(self, server):
		self.items.append(server)
		#self.sort()
		self.disp()

	def sort(self):
		sortkey = lambda x: re.sub('\^[0-9]', '', x.name)
		self.items = sorted(self.items, key=sortkey)
	
	def disp(self):
		self.win.clear()
		## Print column headers
		for col in self.columns:
			self.win.addstr(0, col.x, col.title[:col.w])

		ymax, xmax = self.win.getmaxyx()
		y = 1
		for server in self.items:
			if y > ymax-5:
				break
			for col in self.columns:
				self.win.addstr(y, col.x, col.disp(server)[:col.w] )
			y += 1
		panel.update_panels()
		curses.doupdate()

## }}}
