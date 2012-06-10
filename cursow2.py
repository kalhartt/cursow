#!/usr/bin/python2
import curses, threading
from pywsw import *
from curses import panel

class WARSOW(object):
	MASTERSERVERS = ['dpmaster.deathmask.net']
	PORT = 27950
	PROTOCOL = 12
	OPTIONS = 'full empty'

class statusBar(object):
	def __init__(self):
		self.win = curses.newwin(1, curses.COLS, curses.LINES-1, 0) 
		self.pan = panel.new_panel(self.win)
		self.win.bkgdset(ord(' '), curses.color_pair(12))
		self.win.clrtoeol()
	
	def disp(self, msg):
		self.win.clrtoeol()
		self.win.addstr(0,0, msg[:curses.COLS])
		panel.update_panels()
		curses.doupdate()


class serverList(object):
	cols = ['png', 'plyrs', 'map', 'mod', 'name']
	showcol = ['png', 'plyrs', 'map', 'mod', 'name']

	def __init__(self):
		self.win = curses.newwin(curses.LINES-3, curses.COLS-2, 1,1)
		self.pan = panel.new_panel(self.win)
		self.win.bkgdset(ord(' '), curses.color_pair(12))
		self.win.clrtobot()
		self.items = []
	
	def add(self, server):
		self.items.append(server)
		self.disp()
	
	def disp(self):
		for n in xrange(len(self.items)):
			if n > curses.COLS-3:
				break
			server = self.items[n]
			self.win.addstr(n,0,server.name)
		panel.update_panels()
		curses.doupdate()

class Application(object):
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

		self.serverThread = threading.Thread(target=self.processServers)
		self.serverThread.start()
		
		while True:
			key = screen.getch()
			if key == ord('q'):
				break
			if key == curses.KEY_RESIZE:
				#TODO
				pass

	def processServers(self):
		for ip in self.serverips:
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

	def initColors(self): ## {{{
		if not curses.can_change_color() or curses.COLORS < 10:
			return
		curses.use_default_colors()
		for n in range(5):
			curses.init_color(n, 1000*(1&n), 1000*(2&n), 1000*(4&n))
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

if __name__=='__main__':
	curses.wrapper( Application )
## vim: set ts=4 sw=4 noexpandtab: ##
