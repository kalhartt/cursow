#!/usr/bin/env python2
import color, curses, threading, widgets
import net.wsw as wsw
from curses import panel

## Curses Display Options
## A_NORMAL for most everything
## A_REVERSE for highlighted objects

class App(object):
	serverips = set()

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
		for host in wsw.wswms:
			self.status.disp('Querying Master Server: %s' % host)
			self.serverips = self.serverips | wsw.MasterServer( host, port=wsw.wswport, protocol=wsw.wswprot, options=wsw.wswopt, timeout=1)
			panel.update_panels()
			curses.doupdate()

		## Start Processing Servers
		self.runThread = True
		self.serverThread = threading.Thread(target=self.processServers)
		self.serverThread.start()

		## Main Loop
		n = -1
		while True:
			key = screen.getch()
			if key == ord('q') or key == ord('Q'):
				self.quit()
				break
			else:
				self.status.disp( 'Hi There', self.colors[n]|curses.A_REVERSE )
				n += 1
				if n == 10:
					n=-1
				panel.update_panels()
				curses.doupdate()

	def processServers(self): ##{{{
		for ip in self.serverips:
			if not self.runThread:
				break
			self.status.disp('Querying Server: %s' % ip)
			host = ip.split(':')
			try:
				server = wsw.Guest(host[0], int(host[1]))
				server.update()
				self.serverList.add(server)
			except:
				# TODO handle exception
				continue
		self.status.disp('done')
		## }}}
	
	def quit(self):
		## kill thread if running
		if self.runThread:
			self.runThread = False
			self.serverThread.join()


# vim: set ts=4 sw=4 noexpandtab: ##
