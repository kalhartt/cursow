#!/usr/bin/env python2
import curses, threading, time
from curses import panel
import color, widgets
from net import *

## Curses Display Options
## A_NORMAL for most everything
## A_REVERSE for highlighted objects

class App(object):
	serverips = set()
	quit = False

	def __init__(self, screen):
		## Curses Options
		curses.curs_set(0)
		#screen.nodelay(1)
		screen.keypad(1)

		## Set colors
		self.hascolor, self.colors = color.setColor()

		## Set screen objects
		self.stdscr = screen
		self.status = widgets.statusBar()
		self.serverList = widgets.serverList()

		## Query Master Servers
		for host in wsw.masterServers:
		 	self.status.disp('Querying Master Server: %s' % host)
		 	self.serverips = self.serverips | server.MasterServer( host, port=wsw.port, protocol=wsw.protocol, options=wsw.options, timeout=1)
		 	panel.update_panels()
		 	curses.doupdate()

		## Start Processing Servers
		self.serverThread = threading.Thread(target=self.processServers)
		self.serverThread.start()

		## Main Loop
		while True:
			key = screen.getch()
			if key == ord('q') or key == ord('Q'):
				self.quit = True
				break
			elif key == ord('w') or key == ord('u') or key == curses.KEY_UP:
				self.serverList.moveUp()
			elif key == ord('s') or key == ord('e') or key == curses.KEY_DOWN:
				self.serverList.moveDown()
			elif key == ord('z'):
				self.status.disp('Launching')
				self.serverList.launch()
				self.quit = True
				break

	def processServers(self): ##{{{
		for ip in self.serverips:
			while threading.activeCount() > 5:
				time.sleep(0.1)
			newThread = threading.Thread(target=self.processServer, args=[ip] )
			newThread.start()
		self.status.disp(str(len(self.serverips)))
		## }}}
	
	def processServer(self,ip):
		host = ip.split(':')
		try:
			srv = server.Guest(host[0], int(host[1]))
			srv.getstatus()
			self.serverList.add(srv)
		except Exception as err:
			self.status.disp('Excepted: %s' % err )
	
	def quit(self):
		pass


# vim: set ts=4 sw=4 noexpandtab: ##
