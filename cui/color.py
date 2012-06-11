#!/usr/bin/env python2

hascolor = False
colors = {}

## Assume curses.wrapper has set start_color()
if curses.has_color():
	hascolor = True
	colors = { 
			0 : curses.color_pair(

