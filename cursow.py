#!/usr/bin/env python2
import curses, threading, time, os, sys
from curses import panel

import cui
from net import *
from net import ConnectionError

class cursow(object):

	def __init__(self,screen):#{{{
		## curses options
		curses.curs_set(0)
		cui.color.setColor()
		self.stdscr = screen
		self.stdscr.keypad(1)

		self.settings = cui.settings()
		self.initSrvlst()
		self.initMenus()
		self.focusedWidget = self.srvlst

		panel.update_panels()
		curses.doupdate()

		self.startQuery()

		## Main Loop -- have to catch all quit events here
		while True:
			key = self.stdscr.getch()

			if key in cui.KEY_QUIT:
				self.quit()
				break

			if key in cui.KEY_LAUNCH and self.focusedWidget == self.srvlst:
				self.launch()
				self.quit()
				break

			else:
				self.handleInput( key )

			curses.doupdate()#}}}
	
	##########
	# Server Control
	##########

	def startQuery(self):#{{{
		"""
		Stop current server threads and restart query process
		"""
		self.stopServers()

		self.stop = False
		self.serverips = set()
		self.settings.clearGametype()
		self.settings.clearMod()
		self.srvlst.reset()
		self.mainThread = threading.Thread(target=self.queryMasters)
		self.mainThread.start()#}}}
	
	def queryMasters(self):#{{{
		if self.settings.getShowFavorites():
			for host in self.settings.getFav():
				self.status.setMessage( 'Adding Favorite: %s' % (host) )
				if self.stop:
					return
				self.serverips.add( host )
				curses.doupdate()
		else:
			for host, port, protocol, opts  in self.settings.getMasters():
				if self.stop:
					return
				try:
					self.status.setMessage( 'Querying Master Server: %s %d %d %s' % (host, port, protocol, opts) )
					curses.doupdate()
					self.serverips |= server.MasterServer( host, port=port, protocol=protocol, options=opts )
				except:
					continue
		self.processedServers = 0
		self.totalServers = len( self.serverips )
		self.mainThread = threading.Thread(target=self.processServers)
		self.mainThread.start()#}}}
	
	def processServer(self, ip):#{{{
		"""
		Try to get/parse a status response from a server

		arguments:
		ip -- ip:port string of server
		"""
		try:
			## Create Server Object
			host = ip.split(':')
			srv = server.Server( host[0], int(host[1]) )

			## Get Server information
			srv.getstatus()
			if self.settings.getPing(): srv.getPing()

			## Update others with new information
			expdata =  [ p.name for p in srv.players  ]
			self.srvlst.addItem( srv, expdata )
			self.settings.addGametype( srv.gametype )
			self.settings.addMod( srv.mod )

			## Update progress bar
			self.processedServers += 1
			self.printProcessStatus()

		except ConnectionError:
			## probably timed out, forget it
			self.processedServers += 1
			self.printProcessStatus()

		curses.doupdate()#}}}

	def processServers(self):#{{{
		"""
		Spawn a process thread for every found server
		"""
		for ip in self.serverips:
			if self.stop:
				break
			if threading.activeCount() > 5:
				time.sleep(0.1)
			thread = threading.Thread(target=self.processServer, args=[ip])
			thread.start()#}}}

	def stopServers(self): ## {{{
		"""
		Signals threads to stop and waits until all threads stopped
		"""
		self.stop = True
		while threading.activeCount() > 1:
			time.sleep(0.2)
		## }}}

	def printProcessStatus( self ):#{{{
		"""
		Helper method to update status with progress bar
		"""
		if self.totalServers == 0:
			return
		w = self.status.width - 1
		msg = '%d/%d' % ( self.processedServers, self.totalServers )
		w2 = int( float( w-len(msg)-3 ) * self.processedServers / self.totalServers )
		msg = msg + ' %' + ('='*w2).ljust( w-len(msg)-3 , '-') + '%'
		self.status.setMessage( msg )#}}}

	##########
	# Screen object helpers
	##########

	def initSrvlst( self ):#{{{
		"""
		Create status container and srvlst inside it
		"""
		win = curses.newwin( 0, 0 )
		self.status = cui.statusContainer( win )
		self.status.show()
		self.srvlst = self.status.addWidget( cui.expandList )
		self.initColumns()#}}}

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
		self.setFilters()

		## Make Column Toggler
		self.colMenu = self.tabcon.addWidget( 'Columns', cui.menu )
		self.colMenu.addLabel( 'Keyboard Shortcuts', just='center' )

		## Make Friends List
		self.friendMenu = self.tabcon.addWidget( 'Friends', cui.menu )
		self.friendMenu.addLabel( 'Keyboard Shortcuts', just='center' )

		## Make Help menu
		# TODO - make this read from cui/common
		self.helpMenu = self.tabcon.addWidget( 'Help', cui.menu )
		self.helpMenu.addLabel( 'Keyboard Shortcuts', just='center' )
		self.helpMenu.addLabel( 'General', mode=curses.A_REVERSE )
		self.helpMenu.addLabel( 'Quit: q,Q' )
		self.helpMenu.addLabel( 'Help: F1' )
		self.helpMenu.addLabel( 'Menu: F2' )
		self.helpMenu.addLabel( 'Stop: F3' )
		self.helpMenu.addLabel( 'Refresh: F4' )
		self.helpMenu.addLabel( 'Expand Server: <Space>' )
		self.helpMenu.addLabel( 'Launch Server: <Enter>' )
		self.helpMenu.addLabel( 'Add to Favorites: f' )
		self.helpMenu.addLabel( 'Remove from Favorites: F' )
		self.helpMenu.addLabel( 'Reverse Sort: r,R' )
		self.helpMenu.addLabel( 'Navigation', mode=curses.A_REVERSE )
		self.helpMenu.addLabel( 'Up: w,u,<UP>' )
		self.helpMenu.addLabel( 'Up 5: W,U'  )
		self.helpMenu.addLabel( 'Page Up: <PG-UP>'  )
		self.helpMenu.addLabel( 'Down: s,e,<DOWN>' )
		self.helpMenu.addLabel( 'Down 5: S,E'  )
		self.helpMenu.addLabel( 'Page Down: <PG-DN>'  )
		self.helpMenu.addLabel( 'Next Tab: <TAB>' )
		self.helpMenu.addLabel( 'Prev Tab: <S-TAB>' )

		#}}}

	def resize( self ):#{{{
		"""
		Resize main containers, the containers
		will resize their children
		"""
		height, width = self.stdscr.getmaxyx()
		self.status.resize( height, width )
		self.tabcon.resize( height-4, width-8, 2,4)
		if self.focusedWidget == self.srvlst:
			self.srvlst.display()
		else:
			self.tabcon.display()#}}}

	##########
	# Option Wrappers
	##########

	def setFilters( self ):#{{{
		"""
		Get filter options from settings and apply to srvlst
		"""
		if self.settings.getShowPassword() == 'only':
			password = lambda x: x.password == 1
		elif self.settings.getShowPassword() == 'hide':
			password = lambda x: x.password == 0
		else:
			password = lambda x: True

		if self.settings.getShowInstagib() == 'only':
			instagib = lambda x: x.instagib == 1
		elif self.settings.getShowInstagib() == 'hide':
			instagib = lambda x: x.instagib == 0
		else:
			instagib = lambda x: True

		if self.settings.getGametype() == 'all':
			gametype = lambda x: True
		else:
			gametype = lambda x: x.gametype == self.settings.getGametype()

		if self.settings.getMod() == 'all':
			mod = lambda x: True
		else:
			mod = lambda x: x.mod == self.settings.getMod()

		filt = lambda x: password(x) and instagib(x) and gametype(x) and mod(x)
		self.srvlst.setFilter( filt )#}}}

	##########
	# Input Handling
	##########

	def handleInput( self, key ):#{{{
		"""
		Handle a keypress

		arguments
		key -- ord(c) of key pressed
		"""
		if key in cui.KEY_RESIZE:
			self.resize()
			return

		## Serverlist Control
		if self.focusedWidget == self.srvlst:
			if key in cui.KEY_ADDFAV:
				self.addFav()

			elif key in cui.KEY_DELFAV:
				self.delFav()

			elif key in cui.KEY_LEFT or key in cui.KEY_TABPREV:
				self.navColumn( -1 )

			elif key in cui.KEY_RIGHT or key in cui.KEY_TABNEXT:
				self.navColumn( 1 )

			elif key in cui.KEY_REVERSE:
				self.srvlst.reverse()

			elif key in cui.KEY_MENU:
				self.showMenu()

			elif key in cui.KEY_HELP:
				self.tabcon.navigateTitle( 'Help' )
				self.showMenu()

			elif key in cui.KEY_STOP:
				self.stopServers()

			elif key in cui.KEY_REFRESH:
				self.startQuery()

			else:
				self.srvlst.handleInput( key )
		else:
			if key in cui.KEY_MENU or key in cui.KEY_HELP:
				self.hideMenu()

			else:
				self.tabcon.handleInput( key )#}}}
	
	def showMenu( self ):#{{{
		"""
		Remember current state and show menu
		"""
		self.oldGame = self.settings.getGame()
		self.oldFavs = self.settings.getShowFavorites()

		self.srvlst.pause()
		self.tabcon.show()
		self.menu.display()
		self.focusedWidget = self.tabcon
		panel.update_panels()
		curses.doupdate()#}}}
	
	def hideMenu( self ):#{{{
		"""
		Check if requery needed and hide menu
		"""
		if self.oldGame != self.settings.getGame() or self.oldFavs != self.settings.getShowFavorites():
			self.startQuery()

		self.tabcon.hide()
		self.setFilters()
		self.focusedWidget = self.srvlst
		panel.update_panels()
		curses.doupdate()
		self.srvlst.unPause()#}}}

	def addFav(self):#{{{
		"""
		Add selected server to favorites list
		"""
		srv = self.srvlst.getSelectedItem()
		self.settings.addFav( '%s:%d' % ( srv.host , srv.port ) )#}}}
	
	def delFav(self):#{{{
		"""
		Delete selected item from favorites list
		"""
		srv = self.srvlst.getSelectedItem()
		self.settings.delFav( '%s:%d' % ( srv.host , srv.port ) )#}}}

	def launch(self): ## {{{
		server = self.srvlst.getSelectedItem()
		path, args = self.settings.getPath(), self.settings.getArgs()

		if sys.platform == 'cygwin':
			prog = '/usr/bin/cygstart'
			runlist = [ 'warsow', '-d', os.path.dirname(path), path] + [ arg for arg in args.split() ] + ['connect', '%s:%d' % (server.host, server.port) ]
		else:
			prog = path
			runlist = [ 'warsow' ] + [ arg for arg in args.split() ] + [ 'connect', '%s:%d' % (server.host, server.port) ]

		if os.fork():
			return
		else:
			os.setsid()
			os.execv( prog, runlist )
		#}}}
	
	def navColumn(self, n): ## {{{
		self.column = (self.column+n)%len(self.columnSorts)
		self.srvlst.highlightColumnIndex( self.column )
		self.srvlst.setSortKey( self.columnSorts[ self.column ] )
		## }}}

	def quit(self): ## {{{
		self.settings.writeCfg()
		self.stopServers()
		## }}}

if __name__ == '__main__':
	curses.wrapper( cursow )
