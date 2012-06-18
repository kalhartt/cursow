#!/usr/bin/env python2
import curses, threading, time, os, subprocess
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

		## Variables and screen objects
		self.quit = False
		self.stdscr = screen
		self.settings = cui.options()
		self.serverips = set()

		self.mainwin = curses.newwin(0,0)
		self.fltrwin = curses.newwin( curses.LINES-4, curses.COLS-8, 2,4)
		self.mainpan = panel.new_panel( self.mainwin )
		self.fltrpan = panel.new_panel( self.fltrwin )
		self.fltrpan.top()
		self.status = cui.widStatus( self.mainwin )
		self.srvlst = cui.widSrvlst( self.mainwin )
		self.filter = cui.panFilter( self.fltrwin )

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

			elif key == ord('w') or key == ord('u') or key == curses.KEY_UP:
				self.srvlst.move( -1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == ord('s') or key == ord('e') or key == curses.KEY_DOWN:
				self.srvlst.move( 1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == ord('W') or key == ord('U'):
				self.srvlst.move( -5 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == ord('S') or key == ord('E'):
				self.srvlst.move( 5 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == ord('a') or key == ord('n') or key == curses.KEY_LEFT:
				self.srvlst.sort( n=-1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == ord('d') or key == ord('i') or key == curses.KEY_RIGHT:
				self.srvlst.sort( n=1 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == curses.KEY_PPAGE:
				self.srvlst.move( 3-self.srvlst.h )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == curses.KEY_NPAGE:
				self.srvlst.move( self.srvlst.h-3 )
				self.status.disp( 'pos: %d\trow: %d\theight: %d\titems: %d' % (self.srvlst.pos, self.srvlst.firstrow, self.srvlst.h, len(self.srvlst.items)) )

			elif key == ord('f'):
				srv = self.srvlst.items[ self.srvlst.firstrow + self.srvlst.pos ]
				self.settings.addFav( '%s:%d' % ( srv.host , srv.port ) )

			elif key == ord('F'):
				srv = self.srvlst.items[ self.srvlst.firstrow + self.srvlst.pos ]
				self.settings.delFav( '%s:%d' % ( srv.host , srv.port ) )


			elif key == ord('\t'):
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

			elif key == ord('\n') or key == ord('\r'):
				self.quit = True
				self.settings.writeCfg()
				self.status.disp( 'Stopping active threads...' )
				curses.doupdate()
				while threading.activeCount() > 1:
					time.sleep(0.2)
				self.launch()
				break

			elif key == ord('x'):
				if self.fltrpan.hidden():
					self.fltrpan.show()
				else:
					self.fltrpan.hide()
				panel.update_panels()

			curses.doupdate()
	
	def launch(self):
		server = self.srvlst.items[self.srvlst.firstrow+self.srvlst.pos]
		path, args = self.settings.getPath()
		runlist = [ path , args , 'connect', '%s:%d' % (server.host, server.port) ]
		#subprocess.Popen( runlist, stdout=file(os.devnull, 'w') )
		subprocess.Popen( runlist )
	
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
					self.serverips = self.serverips | server.MasterServer( host, port=port, protocol=protocol, options=opts )
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
