#!/usr/bin/python2
import curses, threading, re
from pywsw import *
from curses import panel

class WARSOW(object): ## {{{
	MASTERSERVERS = ['dpmaster.deathmask.net']
	PORT = 27950
	PROTOCOL = 12
	OPTIONS = 'full empty'
## }}}

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

class Application(object): ## {{{
	colors = False
	serverips = set()

	def __init__(self, screen):
		self.screen = screen
		self.width = curses.COLS
		self.height = curses.LINES
		curses.curs_set(0)		# make cursor invisible
		screen.nodelay(1)		# getch() nonblocking
		screen.keypad(1)		# getch() returns extra keys
		self.initColors()		# set colors
		
		self.status = statusBar()
		self.serverList = serverList()

		panel.update_panels()
		curses.doupdate()

		for host in WARSOW.MASTERSERVERS:
			self.status.disp('Querying Master Server: %s' % host)
			self.serverips = self.serverips | MasterServer( host, port=WARSOW.PORT, protocol=WARSOW.PROTOCOL, options=WARSOW.OPTIONS, timeout=1)
			panel.update_panels()
			curses.doupdate()

		self.killThread = False
		self.serverThread = threading.Thread(target=self.processServers)
		self.serverThread.start()
		
		while True:
			key = screen.getch()
			if key == ord('q'):
				self.killThread = True
				self.serverThread.join()
				break
			if key == curses.KEY_RESIZE:
				#TODO
				pass

	def processServers(self): ##{{{
		for ip in self.serverips:
			if self.killThread:
				break
			self.status.disp('Querying Server: %s' % ip)
			host = ip.split(':')
			try:
				server = Guest(host[0], int(host[1]))
				server.update()
				self.serverList.add(server)
				self.update = True
			except:
				# TODO handle exception
				continue
		self.status.disp('done')
		## }}}

	def initColors(self): ## {{{
		if not curses.can_change_color() or curses.COLORS < 10:
			return
		curses.use_default_colors()
		for n in range(5):
			r = 1000 if 1&n else 0
			g = 1000 if 2&n else 0
			b = 1000 if 4&n else 0
			curses.init_color(n, r, g, b)
		curses.init_color(5,   0,1000,1000)
		curses.init_color(6,1000,   0,1000)
		curses.init_color(7,1000,1000,1000)
		curses.init_color(8,1000, 500,   0)
		curses.init_color(9, 500, 500, 500)
		curses.init_color(10,490, 490, 490)
	
		for n in range(23):
			bg = -1 if n<12 else 10
			# find a nice %11
			fg = n-2 if n<12 else n-13
			curses.init_pair(n, fg, bg)

		self.colors = {}
		self.hlcolors={}
		for n in range(-1,10):
			self.colors[n]   = curses.color_pair(n+2)
			self.hlcolors[n] = curses.color_pair(n+13)
		## }}}
## }}}


if __name__=='__main__':
	curses.wrapper( Application )
## vim: set ts=4 sw=4 noexpandtab: ##
