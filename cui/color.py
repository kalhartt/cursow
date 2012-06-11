#!/usr/bin/env python2
import curses

def setColor():
	hascolor = False
	colors = {}

	if not curses.has_colors():
		return hascolor, colors

	curses.start_color()
	curses.use_default_colors()
	hascolor = True

	if False:
	#if curses.can_change_color():
		curses.init_color(0,   0,   0,   0)
		curses.init_color(1,1000,   0,   0)
		curses.init_color(2,   0,1000,   0)
		curses.init_color(3,1000,1000,   0)
		curses.init_color(4,   0,   0,1000)
		curses.init_color(5,   0,1000,1000)
		curses.init_color(6,1000,   0,1000)
		curses.init_color(7,1000,1000,1000)
		curses.init_color(8,1000, 500,   0)
		curses.init_color(9, 500, 500, 500)
		for n in range(-1,10):
			curses.init_pair(n+2, n, -1)
			colors[n] = curses.color_pair(n+2)
	else:
		curses.init_pair(1, -1, -1)
		curses.init_pair(2, curses.COLOR_BLACK  , -1)
		curses.init_pair(3, curses.COLOR_RED    , -1)
		curses.init_pair(4, curses.COLOR_GREEN  , -1)
		curses.init_pair(5, curses.COLOR_YELLOW , -1)
		curses.init_pair(6, curses.COLOR_BLUE   , -1)
		curses.init_pair(7, curses.COLOR_CYAN   , -1)
		curses.init_pair(8, curses.COLOR_MAGENTA, -1)
		curses.init_pair(9, curses.COLOR_WHITE  , -1)
		curses.init_pair(10,curses.COLOR_YELLOW , -1)
		curses.init_pair(11,curses.COLOR_WHITE  , -1)
		for n in range(-1, 10):
			colors[n] = curses.color_pair(n+2)
	
	return hascolor, colors
