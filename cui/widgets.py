#!/usr/bin/env python2
import curses, re
from curses import panel

escchar = re.compile(r'(\^.)')
stripcol = re.compile(r'(\^[0-9])')

def colorPrint( win, pos, msg, attr=curses.A_NORMAL ):
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
	

class statusBar(object): ## {{{
	def __init__(self):
		self.win = curses.newwin(1, curses.COLS, curses.LINES-1, 0) 
		self.pan = panel.new_panel(self.win)
		#self.win.bkgdset(ord(' '), curses.color_pair(12))
		self.win.clrtoeol()
	
	def disp(self, msg, attr=False):
		self.win.clrtobot()
		if attr:
			self.win.addstr(0,0, msg[:curses.COLS], attr)
		else:
			self.win.addstr(0,0, msg[:curses.COLS])
		panel.update_panels()
		curses.doupdate()
## }}}

class serverList(object): ## {{{

	def __init__(self):
		self.win = curses.newwin(curses.LINES-3, curses.COLS-2, 1,1)
		self.pan = panel.new_panel(self.win)
		self.items = []
		self.pos = 1

		## Column locations and widths
		self.colw = [3, 5, int(0.2*(curses.COLS-10)), int(0.2*(curses.COLS-10)), int(0.2*(curses.COLS-10)), int(0.4*(curses.COLS-10)) ]
		self.colp = [ sum(self.colw[:n])+n for n in range(len(self.colw)) ]
	
	def add(self, server):
		self.items.append(server)
		#self.sort()
		self.disp()

	def sort(self):
		sortkey = lambda x: re.sub('\^[0-9]', '', x.name)
		self.items = sorted(self.items, key=sortkey)
	
	def disp(self):
		self.win.clrtobot()
		## Print column headers
		self.win.addstr(0, self.colp[0], 'png')
		self.win.addstr(0, self.colp[1], 'plyrs')
		self.win.addstr(0, self.colp[2], 'map')
		self.win.addstr(0, self.colp[3], 'mod')
		self.win.addstr(0, self.colp[4], 'gametype')
		self.win.addstr(0, self.colp[5], 'name')

		ymax, xmax = self.win.getmaxyx()
		y = 1
		for server in self.items:
			if y > ymax:
				break
			self.win.addstr(y, self.colp[0], '000')
			self.win.addstr(y, self.colp[1], '%02d/%02d' % ( server.clients, server.maxclients ))
			self.win.addstr(y, self.colp[2], server.map)
			self.win.addstr(y, self.colp[3], server.mod)
			self.win.addstr(y, self.colp[4], server.gametype)
			colorPrint( self.win, [y, self.colp[5], self.colw[5] ], server.name )
			y += 1
		panel.update_panels()
		curses.doupdate()

## }}}
