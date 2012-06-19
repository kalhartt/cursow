#!/usr/bin/env python2
import curses, threading, time, os
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
		self.quit = False
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

		## Import servers
		self.mainThread = threading.Thread(target=self.queryMasters)
		self.mainThread.start()

		## Main Loop
		while True:
			key = self.stdscr.getch()

			if key == ord('q') or key == ord('Q'):
				self.quit = True
				self.settings.writeCfg()
				self.status.disp( 'Stopping active threads...' )
				curses.doupdate()
				while threading.activeCount() > 1:
					time.sleep(0.2)
				break

			elif key in cui.KEY_UP:
				self.srvlst.move( -1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_DOWN:
				self.srvlst.move( 1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_UP5:
				self.srvlst.move( -5 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_DOWN5:
				self.srvlst.move( 5 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_LEFT:
				self.srvlst.sort( n=-1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_RIGHT:
				self.srvlst.sort( n=1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_PGUP:
				self.srvlst.move( 3-self.srvlst.h )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_PGDOWN:
				self.srvlst.move( self.srvlst.h-3 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key in cui.KEY_ADDFAV:
				srv = self.srvlst.items[ self.srvlst.firstrow + self.srvlst.pos ]
				self.settings.addFav( '%s:%d' % ( srv.host , srv.port ) )

			elif key in cui.KEY_DELFAV:
				srv = self.srvlst.items[ self.srvlst.firstrow + self.srvlst.pos ]
				self.settings.delFav( '%s:%d' % ( srv.host , srv.port ) )

			elif key in cui.KEY_TOGGAME:
				self.serverips = set()
				self.quit = True
				self.status.disp( 'Stopping active threads...' )
				curses.doupdate()
				while threading.activeCount() > 1:
					time.sleep(0.2)
				self.quit = False
				self.srvlst.clear()
				self.settings.switchVer()
				self.mainThread = threading.Thread(target=self.queryMasters)
				self.mainThread.start()

			elif key in cui.KEY_LAUNCH:
				self.quit = True
				self.settings.writeCfg()
				self.status.disp( 'Stopping active threads...' )
				curses.doupdate()
				while threading.activeCount() > 1:
					time.sleep(0.2)
				self.launch()
				break

			elif key in cui.KEY_FILTER:
				if self.fltrpan.hidden():
					self.srvlst.pause()
					self.fltrpan.show()
					self.fltrpan.top()
				else:
					self.srvlst.unpause()
					self.fltrpan.hide()
				panel.update_panels()

			else:
				self.status.disp( 'No function on key: %s' % key )

			curses.doupdate()
	
	def launch(self):
		server = self.srvlst.items[self.srvlst.firstrow+self.srvlst.pos]
		path, args = self.settings.getPath()
		runlist = [ 'warsow', args, 'connect', '%s:%d' % (server.host, server.port) ]
		if os.fork():
			return
		else:
			os.setsid()
			os.execv( path, runlist )
	
	def queryMasters(self):
		if self.settings.getFav2():
			for host in self.settings.getFav():
				self.status.disp( 'Adding Favorite: %s' % (host) )
				if self.quit:
					return
				self.serverips.add( host )
				curses.doupdate()
		else:
			for host, port, protocol, opts  in self.settings.getMasters():
				if self.quit:
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
			self.mods.add( srv.mod )
			self.gametypes.add( srv.gametype )
			self.srvlst.add( srv )
			curses.doupdate()
		except Exception as err:
			self.status.disp( 'Querying Server: %s' % (err) )
			curses.doupdate()
		return

	def processServers(self):
		for ip in self.serverips:
			if self.quit:
				break
			if threading.activeCount() > 5:
				time.sleep(0.1)
			thread = threading.Thread(target=self.processServer, args=[ip])
			thread.start()

if __name__ == '__main__':
	curses.wrapper( cursow )
