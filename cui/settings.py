#!/usr/bin/env python2
import os.path, ConfigParser

class settings(object):
	""" Settings class

	All of this just to avoid having a
	[DEFAULTS] section in the config
	file :S
	"""

	##########
	# Defaults
	##########

	cfg = os.path.expanduser('~/.cursow')

	gendefaults = {#{{{
			'Game' : 'Warsow 0.6',
			'Ping Servers' : 'true',
			'Show Favorites' : 'false',
			'Instagib' : 'show',
			'Password' : 'show',
			'Gametype' : 'all',
			'Mod' : 'all',
			}#}}}

	wsw6defaults = {#{{{
		'path' : '/opt/warsow/warsow',
		'args' : '',
		'master1' : 'dpmaster.deathmask.net',
		#'master2' : 'ghdigital.com',
		#'master3' : 'excalibur.nvg.ntnu.no',
		#'master4' : 'eu.master.warsow.net',
		'port' : '27950',
		'protocol' : '12',
		'options' : 'full empty'
		}#}}}

	wsw7defaults = {#{{{
		'path' : '/opt/warsow/warsow',
		'args' : '',
		'master1' : 'dpmaster.deathmask.net',
		#'master2' : 'ghdigital.com',
		#'master3' : 'excalibur.nvg.ntnu.no',
		#'master4' : 'eu.master.warsow.net',
		'port' : '27950',
		'protocol' : '6094',
		'options' : 'full empty'
		}#}}}

	games = [ 'Warsow 0.6', 'Warsow 0.7' ]
	gametypes = ['all']
	mods = ['all']

	##########
	# Initialization
	##########

	def __init__(self):#{{{
		"""
		Open the settings file
		Create if it does not exist
		"""
		self.cp = ConfigParser.SafeConfigParser()

		if not os.path.exists( self.cfg ):
			self.initCfg()
		else:
			self.cp.read( self.cfg )#}}}

	def initCfg(self):#{{{
		"""
		Create basic settings file with default options
		"""
		self.cp.add_section( 'General' )
		for k, v in self.gendefaults.items():
			self.cp.set( 'General', k, v )

		self.cp.add_section( 'Warsow 0.6' )
		for k, v in self.wsw6defaults.items():
			self.cp.set( 'Warsow 0.6', k, v )

		self.cp.add_section( 'Warsow 0.7' )
		for k, v in self.wsw7defaults.items():
			self.cp.set( 'Warsow 0.7', k, v )

		self.cp.add_section( 'Favorites Warsow 0.6' )
		self.cp.add_section( 'Favorites Warsow 0.7' )
		self.cp.add_section( 'Friends' )

		self.writeCfg()#}}}
	
	def writeCfg(self):#{{{
		"""
		Write settings to file
		"""
		cfgfile = open( self.cfg , 'w' )
		self.cp.write( cfgfile )
		cfgfile.close()#}}}

	def getOpt(self, section, option ):#{{{
		"""
		Get an option from section

		arguments:
		section -- section name
		option -- option name
		"""
		return self.cp.get( section, option )#}}}
	
	def setOpt(self, section, option, value):#{{{
		"""
		Set an option from section

		arguments:
		section -- section name
		option -- option name
		value -- value to set
		"""
		self.cp.set( section, option, value )#}}}

	##########
	# General Setting Interfaces
	##########
	
	def addFav(self, host):#{{{
		"""
		Add a given host to the favorites list

		arguments:
		host -- ip:port of server to add
		"""
		section = 'Favorites ' + self.cp.get( 'General', 'Game' )
		numfav = len( self.cp.options( section ) )
		while self.cp.has_option( section , 'server%03d' % nextfav ):
			nextfav += 1
		self.cp.set( section , 'server%03d' % nextfav , host )#}}}

	def delFav(self, host):#{{{
		"""
		Remove a given host to the favorites list

		arguments:
		host -- ip:port of server to delete
		"""
		section = 'Favorites ' + self.cp.get( 'General', 'Game' )
		for k,v in self.cp.items( section ):
			if v == host: self.cp.remove_option( section, k )#}}}

	def getFav(self):#{{{
		"""
		Generator returning the favorites list for current game
		"""
		section = 'Favorites ' + self.cp.get( 'General', 'Game' )
		for key, val in self.cp.items( section ):
			yield val#}}}

	##########
	# Display Options
	##########

	def getGame(self):#{{{
		"""
		Get current game
		"""
		return self.cp.get( 'General', 'Game' )#}}}

	def incGame(self, n):#{{{
		"""
		Increment current game by n
		Rotates through recognized games

		arguments:
		n -- scroll amount
		"""
		game = self.cp.get( 'General', 'Game' )
		try:
			index = (self.games.index( game )+n)%len( self.games )
		except ValueError:
			index = 0
		self.cp.set( 'General', 'Game', self.games[ index ] )#}}}

	def getPing(self):#{{{
		"""
		Get whether or not to ping servers
		"""
		return self.cp.getboolean( 'General', 'Ping Servers' )#}}}

	def setPing(self, value):#{{{
		"""
		Set whether or not to ping servers

		arguments:
		value -- bool to ping servers
		"""
		value = str( value )
		self.cp.set( 'General', 'Ping Servers', value )#}}}

	def getShowFavorites(self):#{{{
		"""
		Get whether to show favorites
		"""
		return self.cp.getboolean( 'General', 'Show Favorites' )#}}}

	def setShowFavorites(self, value):#{{{
		"""
		Set whether to query favorites or query masterserver

		arguments:
		value -- boolean to show favorites
		"""
		value = str( value )
		self.cp.set( 'General', 'Show Favorites', value )#}}}

	def getShowInstagib(self):#{{{
		"""
		Get whether or not to show Instagib servers
		returns one of 'hide' 'show' 'only'
		"""
		return self.cp.get( 'General', 'Instagib' )#}}}

	def incShowInstagib(self, n):#{{{
		"""
		Increments whether to show Instagib servers

		arguments:
		n -- amount to increment by
		"""
		value = self.cp.get( 'General', 'Instagib' )
		options = [ 'show', 'hide', 'only' ]
		try:
			index = (options.index( value.lower() )+n)%3
		except ValueError:
			index = 0
		self.cp.set( 'General', 'Instagib', options[index] )#}}}
	
	def getShowPassword(self):#{{{
		"""
		Get whether or not to show password servers
		returns one of 'hide' 'show' 'only'
		"""
		return self.cp.get( 'General', 'Password' )#}}}

	def incShowPassword(self, n):#{{{
		"""
		Increments whether to show Password servers

		arguments:
		n -- amount to increment by
		"""
		value = self.cp.get( 'General', 'Password' )
		options = [ 'show', 'hide', 'only' ]
		try:
			index = (options.index( value.lower() )+n)%3
		except ValueError:
			index = 0
		self.cp.set( 'General', 'Password', options[index] )#}}}

	def addGametype(self, gametype):#{{{
		"""
		Add a recognized gametype to available options
		"""
		gametypename = gametype.lower()
		if gametypename not in self.gametypes:
			self.gametypes.append( gametypename )#}}}

	def getGametype(self):#{{{
		"""
		get current gametype filter
		"""
		return self.cp.get( 'General', 'Gametype' )#}}}

	def incGametype(self, n):#{{{
		"""
		Increments current filtered gametype

		arguments:
		n -- amount to increment by
		"""
		value = self.cp.get( 'General', 'Gametype' )
		try:
			index = (self.gametypes.index( value.lower() )+n)%len( self.gametypes )
		except ValueError:
			index = 0
		self.cp.set( 'General', 'Gametype', self.gametypes[index] )#}}}

	def addMod(self, mod):#{{{
		"""
		Add a recognized mod to available options
		"""
		modname = mod.lower()
		if modname not in self.mods:
			self.mods.append( modname )#}}}

	def getMod(self):#{{{
		"""
		get current mod filter
		"""
		return self.cp.get( 'General', 'Mod' )#}}}

	def incMod(self, n):#{{{
		"""
		Increments current filtered mod

		arguments:
		n -- amount to increment by
		"""
		value = self.cp.get( 'General', 'Mod' )
		try:
			index = (self.mods.index( value.lower() )+n)%len( self.mods )
		except ValueError:
			index = 0
		self.cp.set( 'General', 'Mod', self.mods[index] )#}}}

	def getPath(self):#{{{
		"""
		Get path to current game binary
		"""
		section = self.cp.get( 'General', 'Game' )
		return os.path.expanduser( self.cp.get( section , 'path' ) )#}}}

	def setPath(self, value):#{{{
		"""
		Set path to current game binary

		arguments:
		value -- path to current game binary
		"""
		section = self.cp.get( 'General', 'Game' )
		self.cp.set( section , 'path', value  )#}}}

	def getArgs(self):#{{{
		"""
		Get current game launch arguments
		"""
		section = self.cp.get( 'General', 'Game' )
		return self.cp.get( section , 'args' )#}}}

	def setArgs(self, value):#{{{
		"""
		Set current game launch arguments

		arguments:
		value -- path to current game binary
		"""
		section = self.cp.get( 'General', 'Game' )
		self.cp.set( section , 'args', value  )#}}}

	def getMasters(self):#{{{
		"""
		Generator returning list of master servers for current game
		"""
		section = self.cp.get( 'General', 'Game' )
		port = self.cp.getint( section, 'port' )
		protocol = self.cp.getint( section, 'protocol' )
		options = self.cp.get( section, 'options' )
		for k,v in self.cp.items( section ):
			if 'master' in k.lower():
				yield v, port, protocol, options #}}}

	
