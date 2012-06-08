#!/usr/bin/python2
from pywsw import *
import curses, threading, Queue, time

class WARSOW(object):
    MASTERSERVERS = ["dpmaster.deathmask.net"]
    PORT = 27950
    PROTOCOL = 12
    OPTIONS = "empty"

class cursow(object):
    serverips = set()
    colors = False
    update = False
    servers = []

    def __init__(self, screen): ## {{{ Init
        self.screen = screen
        self.height, self.width = self.screen.getmaxyx()

        ## Set curses options {{{
        curses.curs_set(0)
        self.screen.nodelay(1)
        self.screen.keypad(1)
        self.colorCheck()
        ## }}}

        ## Get Server List from master servers {{{
        for host in WARSOW.MASTERSERVERS:
            self.printStatus("Querying Master Server: %s" % (host))
            self.serverips = self.serverips | MasterServer( host, port=WARSOW.PORT, protocol=WARSOW.PROTOCOL, options=WARSOW.OPTIONS, timeout = 1)
        ## }}}
        
        ## Start Server processing {{{
        self.workerThread = threading.Thread(target=self.processServers)
        self.workerThread.start()
        ## }}}

        ## {{{ Page options
        self.page = 0 # 0 - serverbrowser 1 options
        self.pos = 0 # current position
        ## }}}

        ## Main loop {{{
        while True:
            key = self.screen.getch()
            if key == ord('q'):
                break
            if key == curses.KEY_UP:
                self.pos -= 1
                self.pos = 0 if self.pos < 0 else self.pos
                self.printStatus(str(self.pos))
                self.refresh()
            if key == curses.KEY_DOWN:
                self.pos += 1
                self.pos = self.height-4 if self.pos > self.height-4 else self.pos
                self.printStatus(str(self.pos))
                self.refresh()
            if self.update:
                self.refresh()
            time.sleep(0.1)
        ## }}}

    ## }}}

    def colorCheck(self): ## {{{
        if curses.can_change_color() and curses.COLORS > 10:
            curses.use_default_colors()
            curses.init_color(0,1000,0000,0000)
            curses.init_color(1,0000,1000,0000)
            curses.init_color(2,1000,1000,0000)
            curses.init_color(3,0000,0000,1000)
            curses.init_color(4,0000,1000,1000)
            curses.init_color(5,1000,0000,1000)
            curses.init_color(6,1000,1000,1000)
            curses.init_color(8,1000,0500,0000)
            curses.init_color(9,0500,0500,0500)
            curses.init_color(10,490,490,490)

            curses.init_pair(  1, -1, -1)
            curses.init_pair(  2,  0, -1)
            curses.init_pair(  3,  1, -1)
            curses.init_pair(  4,  2, -1)
            curses.init_pair(  5,  3, -1)
            curses.init_pair(  6,  4, -1)
            curses.init_pair(  7,  5, -1)
            curses.init_pair(  8,  6, -1)
            curses.init_pair(  9,  7, -1)
            curses.init_pair( 10,  8, -1)
            curses.init_pair( 11,  9, -1)
            curses.init_pair( 12, -1, 10)
            curses.init_pair( 13,  0, 10)
            curses.init_pair( 14,  1, 10)
            curses.init_pair( 15,  2, 10)
            curses.init_pair( 16,  3, 10)
            curses.init_pair( 17,  4, 10)
            curses.init_pair( 18,  5, 10)
            curses.init_pair( 19,  6, 10)
            curses.init_pair( 20,  7, 10)
            curses.init_pair( 21,  8, 10)
            curses.init_pair( 22,  9, 10)
            self.colors = {
                    -1 : curses.color_pair( 1),
                     0 : curses.color_pair( 2),
                     1 : curses.color_pair( 3),
                     2 : curses.color_pair( 4),
                     3 : curses.color_pair( 5),
                     4 : curses.color_pair( 6),
                     5 : curses.color_pair( 7),
                     6 : curses.color_pair( 8),
                     7 : curses.color_pair( 9),
                     8 : curses.color_pair(10),
                     9 : curses.color_pair(11),
                     }
            self.hlcolors = {
                    -1 : curses.color_pair(12),
                     0 : curses.color_pair(13),
                     1 : curses.color_pair(14),
                     2 : curses.color_pair(15),
                     3 : curses.color_pair(16),
                     4 : curses.color_pair(17),
                     5 : curses.color_pair(18),
                     6 : curses.color_pair(19),
                     7 : curses.color_pair(20),
                     8 : curses.color_pair(21),
                     9 : curses.color_pair(22),
                     }
    ## }}}

    def processServers(self): ## Server Processing {{{
        ## Order the server list
        for ip in self.serverips:
            self.printStatus("Querying Server: %s" % ip)
            host = ip.split(":")
            assert len(host) == 2
            try:
                server=Guest(host[0], int(host[1]))
                server.update()
                self.servers.append(server)
                self.update = True
            except:
                continue
        self.printStatus("done")
        ## }}}
                
    def printStatus(self, msg): ## {{{
        height,width = self.screen.getmaxyx()
        message = msg[:width-1].ljust(width-1)
        self.screen.addstr( height-1 , 0 , message)
        self.screen.refresh()
        ## }}}

    def printLn(self, ystart, xstart, width, msg): ## {{{
        if self.colors:
            x = xstart
            y = ystart
            curcolor = self.hlcolors[-1] if y==self.pos else self.colors[-1]
            colormark = False
            for c in msg:
                if x > xstart+width:
                    break
                if colormark and ord(c) < 58 and ord(c) > 47:
                    curcolor = self.hlcolors[int(c)] if y==self.pos else self.colors[int(c)]
                    colormark = False
                    continue
                elif colormark:
                    self.screen.addstr(y, x, "^"+c, curcolor)
                    x += 1
                    colormark = False
                    continue
                elif c == "^":
                    colormark = True
                    continue
                self.screen.addstr(y, x, c, curcolor)
                x += 1
            while x < xstart+width:
                #self.screen.addstr(y, x, " ")
                x += 1
        else:
            self.screen.addstr(y, x, msg[:width].ljust(width))
        ## }}}

    def refresh(self): ##{{{
        height,width = self.screen.getmaxyx()
        
        ## Calculate column width
        colwidth = [ 3, 5, int(0.2*(width-8)) , int(0.2*(width-8)), int(0.2*(width-8)), int(0.4*(width-8)) ] 
        colstart = [ sum(colwidth[0:n])+n for n in xrange(len(colwidth)) ]
        self.printLn(0,colstart[0], colwidth[0], "png")
        self.printLn(0,colstart[1], colwidth[1], "plyrs")
        self.printLn(0,colstart[2], colwidth[2], "gametype")
        self.printLn(0,colstart[3], colwidth[3], "map")
        self.printLn(0,colstart[4], colwidth[4], "mod")
        self.printLn(0,colstart[5], colwidth[5], "name")

        for n in xrange(min(len(self.servers),height-3)):
            server = self.servers[n]
            self.printLn(n+1,colstart[0], colwidth[0], "000")
            self.printLn(n+1,colstart[1], colwidth[1], "%02d/%02d" % ( server.clients , server.maxclients ))
            self.printLn(n+1,colstart[2], colwidth[2], server.gametype)
            self.printLn(n+1,colstart[3], colwidth[3], server.map)
            self.printLn(n+1,colstart[4], colwidth[4], server.mod)
            self.printLn(n+1,colstart[5], colwidth[5], server.name)
        self.screen.refresh()
        self.update = False
        ##}}}

curses.wrapper(cursow)
## vim: set ts=4 sw=4 expandtab: ##
