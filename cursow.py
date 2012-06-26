#!/usr/bin/env python2
import curses, threading, time, os, sys
from curses import panel

import cui
from net import *

class cursow(object):
	def __init__(self,screen):
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

		## screen objects
		self.stdscr = screen
		self.mainwin = curses.newwin(0,0)
		self.fltrwin = curses.newwin( curses.LINES-4, curses.COLS-8, 2,4)
		self.mainpan = panel.new_panel( self.mainwin )
		self.fltrpan = panel.new_panel( self.fltrwin )
		self.status = cui.widStatus( self.mainwin )
		self.srvlst = cui.widSrvlst( self.mainwin )
		self.filter = cui.panFilter( self.fltrwin, self.settings )
		self.srvlst.setFilter( self.filter.getFilter() )

		## Import servers
		self.mainThread = threading.Thread(target=self.queryMasters)
		self.mainThread.start()

		## Main Loop
		while True:
			key = self.stdscr.getch()

			if key in cui.KEY_QUIT:
				self.quit()
				break

			elif key in cui.KEY_UP:
				self.navigate( -1 )

			elif key in cui.KEY_DOWN:
				self.navigate( 1 )

			elif key in cui.KEY_UP5:
				self.navigate( -5 )

			elif key in cui.KEY_DOWN5:
				self.navigate( 5 )

			elif key in cui.KEY_LEFT:
				self.navColumn( -1 )

			elif key in cui.KEY_RIGHT:
				self.navColumn( 1 )

			elif key in cui.KEY_PGUP:
				self.navigate( 3 - self.srvlst.h )

			elif key in cui.KEY_PGDOWN:
				self.navigate( self.srvlst.h - 3 )

			elif key in cui.KEY_ADDFAV:
				srv = self.srvlst.items[ self.srvlst.firstrow + self.srvlst.pos ]
				self.settings.addFav( '%s:%d' % ( srv.host , srv.port ) )

			elif key in cui.KEY_DELFAV:
				srv = self.srvlst.items[ self.srvlst.firstrow + self.srvlst.pos ]
				self.settings.delFav( '%s:%d' % ( srv.host , srv.port ) )

			elif key in cui.KEY_TOGGAME:
				self.serverips = set()
				self.stop = True
				self.status.disp( 'Stopping active threads...' )
				curses.doupdate()
				while threading.activeCount() > 1:
					time.sleep(0.2)
				self.stop = False
				self.srvlst.clear()
				self.settings.switchVer()
				self.mainThread = threading.Thread(target=self.queryMasters)
				self.mainThread.start()

			elif key in cui.KEY_LAUNCH:
				self.stop = True
				self.settings.writeCfg()
				self.status.disp( 'Stopping active threads...' )
				curses.doupdate()
				while threading.activeCount() > 1:
					time.sleep(0.2)
				self.launch()
				break

			elif key in cui.KEY_FILTER:
				## Show filter menu
				self.srvlst.pause()
				self.fltrpan.show()
				self.fltrpan.top()
				panel.update_panels()

				## Get new filter
				self.filter.focus()
				self.srvlst.setFilter( self.filter.getFilter() )

				## Hide again
				self.srvlst.unpause()
				self.fltrpan.hide()
				panel.update_panels()

			elif key in cui.KEY_STOP:
				self.stopServers()

			elif key in cui.KEY_REFRESH:
				self.refresh()

			else:
				self.status.disp( 'No function on key: %s' % key )

			curses.doupdate()
	
	def queryMasters(self):
		if self.settings.showFavorites():
			for host in self.settings.getFav():
				self.status.disp( 'Adding Favorite: %s' % (host) )
				if self.stop:
					return
				self.serverips.add( host )
				curses.doupdate()
		else:
			for host, port, protocol, opts  in self.settings.getMasters():
				if self.stop:
					return
				try:
					self.status.disp( 'Querying Master Server: %s %d %d %s' % (host, port, protocol, opts) )
					curses.doupdate()
					self.serverips |= server.MasterServer( host, port=port, protocol=protocol, options=opts )
				except:
					continue
		self.mainThread = threading.Thread(target=self.processServers)
		self.mainThread.start()
	
	def processServer(self, ip):
		try:
			self.status.disp( 'Querying Server: %s' % (ip) )
			host = ip.split(':')
			srv = server.Server( host[0], int(host[1]) )
			srv.getstatus()
			if self.settings.getPing(): srv.getPing()
			self.filter.addMod( srv.mod )
			self.filter.addGametype( srv.gametype )
			self.srvlst.add( srv )
			curses.doupdate()
		except Exception as err:
			self.status.disp( 'Querying Server: %s' % (err) )
			curses.doupdate()
		return

	def processServers(self):
		for ip in self.serverips:
			if self.stop:
				break
			if threading.activeCount() > 5:
				time.sleep(0.1)
			thread = threading.Thread(target=self.processServer, args=[ip])
			thread.start()

	## Functions bound to keys

	def launch(self): ## {{{
		server = self.srvlst.items[self.srvlst.firstrow+self.srvlst.pos]
		path, args = self.settings.getPath()

		if sys.platform == 'cygwin':
			if os.fork():
				return
			else:
				runlist = [ 'warsow', '-d', os.path.dirname(path), path, args, 'connect', '%s:%d' % (server.host, server.port) ]
				os.setsid()
				os.execv( '/usr/bin/cygstart', runlist )

		else:
			if os.fork():
				return
			else:
				runlist = [ 'warsow', args, 'connect', '%s:%d' % (server.host, server.port) ]
				os.setsid()
				os.execv( path, runlist )
		## }}}
	
	def navigate(self, n): ## {{{
		self.srvlst.move( n )
		self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )
		## }}}
	
	def navColumn(self, n): ## {{{
		self.srvlst.sort( n=n )
		self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )
		## }}}

	def refresh(self): ##{{{
		self.stopServers()
		## Wait for stopServers
		while threading.activeCount() > 1:
			time.sleep(0.2)
		## Clear variables and display
		self.stop = False
		self.serverips = set()
		self.mods = set()
		self.gametypes = set()
		self.srvlst.clear()
		## Restart Server Thread
		self.mainThread = threading.Thread(target=self.queryMasters)
		self.mainThread.start()
		## }}}

	def stopServers(self): ## {{{
		self.stop = True
		self.status.disp( 'Stopping active threads...' )
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
