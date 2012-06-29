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
		self.settings = cui.options()

		self.stdscr = screen
		## Status Container
		win = curses.newwin( 0, 0 )
		self.status = cui.statusContainer( win )
		self.status.show()
		## Server list as statusContainer widget
		self.status.addWidget( cui.expandList )
		self.srvlst = self.status.getWidget()
		self.srvlst.addColumn( 3, lambda x: '%03d' % x.ping, 'png' )
		self.srvlst.addColumn( 5, lambda x: '%s/%s' % (x.clients, x.maxclients), 'plyrs')
		self.srvlst.addColumn(0.2, lambda x: x.map, 'map')
		self.srvlst.addColumn(0.2, lambda x: x.mod, 'mod')
		self.srvlst.addColumn(0.2, lambda x: x.gametype, 'gametype')
		self.srvlst.addColumn(0.4, lambda x: x.name, 'name')

		panel.update_panels()
		curses.doupdate()

		##self.tabwin = curses.newwin( curses.LINES-4, curses.COLS-8, 2,4)
		##self.tabcon = cui.panTabbedContainer( self.tabwin, self.settings )
		##self.tabcon.addWidget( 'Filter1', cui.panFilter )
		##self.tabcon.addWidget( 'Filter2', cui.panFilter )

		## Import servers
		self.mainThread = threading.Thread(target=self.queryMasters)
		self.mainThread.start()

		## Main Loop
		while True:
			key = self.stdscr.getch()

			if key in cui.KEY_QUIT:
				self.quit()
				break

			else:
				self.srvlst.move( 1 )
				self.status.display( 'row: %d firstrow: %d height: %d items: %d' % (self.srvlst.row, self.srvlst.firstrow, self.srvlst.height, len(self.srvlst.items)) )

			curses.doupdate()#}}}
	
	def queryMasters(self):#{{{
		if self.settings.showFavorites():
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
		## 	runlist = [ 'warsow', args, 'connect', '%s:%d' % (server.host, server.port) ]

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
		self.srvlst.sort( n=n )
		self.status.display( 'row: %d\tfirstrow: %d\theight: %d\titems: %d' % (self.srvlst.row, self.srvlst.firstrow, self.srvlst.height, len(self.srvlst.items)) )
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
