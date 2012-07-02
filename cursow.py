#!/usr/bin/env python2
import curses, threading, time, os, sys
from curses import panel

import cui
#from cui.common import *
#from cui import color, options, columnList, tabbedContainer
from net import *
from net import Error, ConnectionError

class cursow(object):

	def __init__(self,screen):#{{{
		## curses options
		curses.curs_set(0)
		screen.keypad(1)
		#screen.nodelay(1)

		## Set colors
		cui.color.setColor()
		
		## Needed variables
		self.stop = False
		self.serverips = set()
		self.mods = set()
		self.gametypes = set()
		self.settings = cui.settings()

		self.stdscr = screen
		## Status Container
		win = curses.newwin( 0, 0 )
		self.status = cui.statusContainer( win )
		self.status.show()
		## Server list as statusContainer widget
		self.status.addWidget( cui.expandList )
		self.srvlst = self.status.getWidget()
		self.initColumns()
		self.initMenus()

		panel.update_panels()
		curses.doupdate()


		## Import servers
		self.mainThread = threading.Thread(target=self.queryMasters)
		self.mainThread.start()

		## Main Loop
		while True:
			key = self.stdscr.getch()

			if key in cui.KEY_QUIT:
				self.quit()
				break

			elif key in cui.KEY_LEFT:
				self.navColumn( -1 )

			elif key in cui.KEY_RIGHT:
				self.navColumn( 1 )

			elif key in cui.KEY_FILTER:
				self.srvlst.pause()
				self.tabcon.show()
				panel.update_panels()
				curses.doupdate()
				self.menu.display()
				curses.doupdate()

				self.tabcon.focus()

				self.tabcon.hide()
				panel.update_panels()
				curses.doupdate()
				self.srvlst.unPause()

			elif key in cui.KEY_RESIZE:
				self.resize()

			else:
				self.srvlst.handleInput( key )
				self.status.display( 'row: %d firstrow: %d height: %d items: %d' % (self.srvlst.row, self.srvlst.firstrow, self.srvlst.height, len(self.srvlst.items)) )

			curses.doupdate()#}}}
	
	##########
	# Screen object helpers
	##########

	def initColumns( self ):#{{{
		self.column = 4
		self.columnNames = [ 'i', 'p', 'png', 'plyrs', 'map', 'mod', 'gametype', 'name' ]
		self.columnDisps = [
				lambda x: 'X' if x.instagib else ' ', 
				lambda x: 'X' if x.password else ' ',
				lambda x: '%d' % x.ping,
				lambda x: '%s/%s' % (x.clients, x.maxclients),
				lambda x: x.map,
				lambda x: x.mod,
				lambda x: x.gametype,
				lambda x: x.name ]
		self.columnSorts = [
				lambda x: 1 if x.instagib else 0, 
				lambda x: 1 if x.password else 0,
				lambda x: x.ping,
				lambda x: x.clients,
				lambda x: x.map.lower(),
				lambda x: x.mod.lower(),
				lambda x: x.gametype.lower(),
				lambda x: x.name2.lower() ]
		self.columnWidths = [ 1, 1, 3, 5, -1, -1, -1, -2 ]
		totalwidth = 5
		
		for n in range( len(self.columnNames) ):
			w = self.columnWidths[n]
			if w < 0: w = -w / float( totalwidth )
			self.srvlst.addColumn( w, self.columnDisps[n], self.columnNames[n] )
		self.srvlst.highlightColumnIndex( self.column )
		self.srvlst.setSortKey( self.columnSorts[ self.column ] )#}}}

	def initMenus( self ):#{{{
		"""
		Helper to make menus
		"""
		## Make tabbed container
		self.tabwin = curses.newwin( curses.LINES-4, curses.COLS-8, 2,4)
		self.tabcon = cui.tabbedContainer( self.tabwin )

		## Make filter menu
		self.menu = self.tabcon.addWidget( 'Filters', cui.menu )
		self.menu.addListBox( "Game", self.settings.getGame , self.settings.incGame )
		self.menu.addToggle( "Ping Servers", self.settings.getPing, self.settings.setPing  )
		self.menu.addToggle( "Show Favorites", self.settings.getShowFavorites , self.settings.setShowFavorites )
		self.menu.addListBox( "Show Password", self.settings.getShowPassword , self.settings.incShowPassword  )
		self.menu.addListBox( "Show Instagib", self.settings.getShowInstagib , self.settings.incShowInstagib  )
		self.menu.addListBox( "Gametype", self.settings.getGametype , self.settings.incGametype )
		self.menu.addListBox( "Mod", self.settings.getMod , self.settings.incMod )
		#self.menu.addListBox( "Show Empty", self.settings.getShowEmpty , self.settings.incShowEmpty  )
		#self.menu.addListBox( "Show Full", self.settings.getShowFull , self.settings.incShowFull  )
		self.menu.addLabel( "Hello There" )
		#}}}

	def resize( self ):
		"""
		Resize main containers, the containers
		will resize their children
		"""
		height, width = self.stdscr.getmaxyx()
		self.status.resize( height, width )
		self.tabcon.resize( height-4, width-8, 2,4)
		self.status.display( 'ROWS: %d COLS: %d height: %d width: %d' % (curses.LINES, curses.COLS, height, width) )

	def queryMasters(self):#{{{
		if self.settings.getShowFavorites():
			for host in self.settings.getFav():
				self.status.display( 'Adding Favorite: %s' % (host) )
				if self.stop:
					return
				self.serverips.add( host )
				curses.doupdate()
		else:
			for host, port, protocol, opts  in self.settings.getMasters():
				if self.stop:
					return
				try:
					self.status.display( 'Querying Master Server: %s %d %d %s' % (host, port, protocol, opts) )
					curses.doupdate()
					self.serverips |= server.MasterServer( host, port=port, protocol=protocol, options=opts )
				except:
					continue
		self.mainThread = threading.Thread(target=self.processServers)
		self.mainThread.start()#}}}
	
	def processServer(self, ip):#{{{
		try:
			self.status.display( 'Querying Server: %s' % (ip) )
			host = ip.split(':')
			srv = server.Server( host[0], int(host[1]) )
			srv.getstatus()
			self.settings.addGametype( srv.gametype )
			self.settings.addMod( srv.mod )
			if self.settings.getPing(): srv.getPing()
			expdata =  [ p.name for p in srv.players  ]
			self.srvlst.addItem( srv, expdata )
			curses.doupdate()
		except ConnectionError as err:
			self.status.display( 'Querying Server: %s' % (err) )
			curses.doupdate()
		return#}}}

	def processServers(self):#{{{
		for ip in self.serverips:
			if self.stop:
				break
			if threading.activeCount() > 5:
				time.sleep(0.1)
			thread = threading.Thread(target=self.processServer, args=[ip])
			thread.start()#}}}

	## Functions bound to keys
	def addFav(self):#{{{
		pass
		#srv = self.srvlst.getServer()
		#self.settings.addFav( '%s:%d' % ( srv.host , srv.port ) )#}}}
	
	def delFav(self):#{{{
		pass
		#srv = self.srvlst.getServer()
		#self.settings.delFav( '%s:%d' % ( srv.host , srv.port ) )#}}}

	def launch(self): ## {{{
		pass
		##server = self.srvlst.getServer()
		## path, args = self.settings.getPath()

		## if sys.platform == 'cygwin':
		## 	prog = '/usr/bin/cygstart'
		## 	runlist = [ 'warsow', '-d', os.path.dirname(path), path, args, 'connect', '%s:%d' % (server.host, server.port) ]
		## else:
		## 	prog = path
		## 	runlimt = [ 'warsow', args, 'connect', '%s:%d' % (server.host, server.port) ]

		## if os.fork():
		## 	self.stop = True
		## 	self.settings.writeCfg()
		## 	self.status.disp( 'Stopping active threads...' )
		## 	curses.doupdate()
		## 	while threading.activeCount() > 1:
		## 		time.sleep(0.2)
		## 	return
		## else:
		## 	os.setsid()
		## 	os.execv( prog, runlist )
		## }}}
	
	def navigate(self, n): ## {{{
		self.srvlst.move( n )
		self.status.display( 'row: %d firstrow: %d height: %d items: %d' % (self.srvlst.row, self.srvlst.firstrow, self.srvlst.height, len(self.srvlst.items)) )
		## }}}
	
	def navColumn(self, n): ## {{{
		self.column = (self.column+n)%len(self.columnSorts)
		self.srvlst.highlightColumnIndex( self.column )
		self.srvlst.setSortKey( self.columnSorts[ self.column ] )
		self.status.display( 'row: %d firstrow: %d height: %d items: %d' % (self.srvlst.row, self.srvlst.firstrow, self.srvlst.height, len(self.srvlst.items)) )
		## }}}

	def refresh(self): ##{{{
		pass
		## self.stopServers()
		## ## Wait for stopServers
		## while threading.activeCount() > 1:
		## 	time.sleep(0.2)
		## ## Clear variables and display
		## self.stop = False
		## self.serverips = set()
		## self.mods = set()
		## self.gametypes = set()
		## self.srvlst.clear()
		## ## Restart Server Thread
		## self.mainThread = threading.Thread(target=self.queryMasters)
		## self.mainThread.start()
		## }}}

	def stopServers(self): ## {{{
		self.stop = True
		#self.status.disp( 'Stopping active threads...' )
		curses.doupdate()
		## }}}

	def quit(self): ## {{{
		self.stopServers()
		self.settings.writeCfg()
		while threading.activeCount() > 1:
			time.sleep(0.2)
		## }}}

if __name__ == '__main__':
	curses.wrapper( cursow )
