#!/usr/bin/env python2
__all__ = ['color', 'options', 'panFilter', 'widStatus', 'widSrvlst']

from . import color
from .options import options
from .widStatus import widStatus
from .widSrvlst import widSrvlst
from .panFilter import panFilter

import curses

## Program Functions
KEY_QUIT = [ ord(x) for x in 'qQ' ]
KEY_HELP = [ curses.KEY_F1 ]
KEY_FILTER = [ curses.KEY_F2 ]
KEY_STOP = [ curses.KEY_F3 ]
KEY_REFRESH = [ curses.KEY_F4 ]
KEY_LAUNCH = [ ord(x) for x in '\n\r' ]
KEY_TOGGAME = [ ord(x) for x in '\t' ]
KEY_ADDFAV = [ ord(x) for x in 'f' ]
KEY_DELFAV = [ ord(x) for x in 'F' ]

## Navigation
KEY_UP = [ ord(x) for x in 'wu' ] + [ curses.KEY_UP ]
KEY_UP5 = [ ord(x) for x in 'WU' ]
KEY_PGUP = [ curses.KEY_PPAGE ]
KEY_DOWN = [ ord(x) for x in 'se' ] + [ curses.KEY_DOWN ]
KEY_DOWN5 = [ ord(x) for x in 'SE' ]
KEY_PGDOWN = [ curses.KEY_NPAGE]
KEY_LEFT = [ ord(x) for x in 'aAnN' ] + [ curses.KEY_LEFT ]
KEY_RIGHT = [ ord(x) for x in 'dDiI' ] + [ curses.KEY_RIGHT ]
