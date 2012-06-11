#!/usr/bin/env python2
import curses, re

escchar = re.compile(r'(\^.)')

def colorPrint( win, pos, msg, attr=curses.A_NORMAL ):
	## pos = [ y , x , width ]
	msg = re.split( escchar, msg)
	color = curses.color_pair(1)

	w = 0
	for submsg in msg:
		if w > width:
			break
		if submsg[0] == '^':
			try:
				color = curses.color_pair(int(submsg[1]))
				continue
			except ValueError:
				pass
		self.win.addstr(pos[0], pos[1]+w, submsg[:width-w])
		w += len(submsg)
	

class statusBar(object): ## {{{
	def __init__(self):
		self.win = curses.newwin(1, curses.COLS, curses.LINES-1, 0) 
		self.pan = panel.new_panel(self.win)
		self.win.bkgdset(ord(' '), curses.color_pair(12))
		self.win.clrtoeol()
	
	def disp(self, msg):
		self.win.clrtobot()
		self.win.addstr(0,0, msg[:curses.COLS])
		panel.update_panels()
		curses.doupdate()
## }}}

class serverList(object): ## {{{

	def __init__(self):
		self.win = curses.newwin(curses.LINES-3, curses.COLS-2, 1,1)
		self.pan = panel.new_panel(self.win)
		self.win.bkgdset(ord(' '), curses.color_pair(12))
		self.win.clrtobot()
		self.items = []
		self.key = 'name'
	
	def add(self, server):
		self.items.append(server)
		#self.sort()
		self.disp()

	def sort(self):
		sortkey = lambda x: re.sub('\^[0-9]', '', x.name)
		self.items = sorted(self.items, key=sortkey)
	
	def disp(self):
		self.win.clrtobot()
		colwidth = [ 3, 5, int(0.1*(curses.COLS-8)), int(0.1*(width-8)), int(0.2(width-8)), int(0.6(width-8)) ]
		colstart = [ sum(colwidth[0:n])+n for n in xrange(len(colwidth)) ]
		color = self.colors(1)
		self.win.addstr(0, colwidth[0],'png')
		self.win.addstr(0, colwidth[1],'plyrs')
		self.win.addstr(0, colwidth[2],'gametype'[:colwidth[2]])
		self.win.addstr(0, colwidth[3],'map'[:colwidth[3]])
		self.win.addstr(0, colwidth[4],'mod'[:colwidth[4]])
		self.win.addstr(0, colwidth[5],'name'[:colwidth[5]])

		y = 1
		for server in self.items:
			if y >= curses.COLS-3:
				break
			color = self.colors(1)
			self.win.addstr(y, colwidth[0],'000')
			self.win.addstr(y, colwidth[1], '%02d/%02d' % ( server.clients , server.maxclients ) )
			self.win.addstr(y, colwidth[2], server.gametype[:colwidth[2]])
			self.win.addstr(y, colwidth[3], server.map[:colwidth[3]])
			self.win.addstr(y, colwidth[4], server.mod[:colwidth[4]])

			name = re.split(r'(\^.)', server.name)
			w = colwidth[5]
			wm = curses.COLS-3-w
			while wm > 0:
				for part in name:
					if part[0] == '^':
						try:
							color = self.colors(int(part[1]))
						except:
							self.win.addstr(y, w, part[:wm])
							w += len(part)
							wm -= len(part)
					else:
						self.win.addstr(y, w, part[:wm])
						w += len(part)
						wm -= len(part)
			y += 1

		for n in xrange(len(self.items)):
			if n > curses.COLS-3:
				break

			name = re.sub(r'\^[0-9]', '', server.name)
			self.win.addstr(n,0,name)
		panel.update_panels()
		curses.doupdate()
## }}}
