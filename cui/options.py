#!/usr/bin/env python2
import os.path, ConfigParser

class Settings(object):
	""" Settings class

	All of this just to avoid having a
	[DEFAULTS] section in the config
	file :S
	"""

	cfg = os.path.expanduser('~/.cursow')
	gendefaults = {
			'wsw_0.6' : 'true',
			'wsw0.6_path' : '/opt/warsow',
			'wsw0.7_path' : '/opt/warsow2',
			'wsw0.6_args' : '',
			'wsw0.7_args' : '',
			'pingservers' : 'true',
			}

	wsw6defaults = {
		'master1' : 'dpmaster.deathmask.net',
		'master2' : 'ghdigital.com',
		'master3' : 'excalibur.nvg.ntnu.no',
		'master4' : 'eu.master.warsow.net',
		'port' : '27950',
		'protocol' : '12',
		'options' : 'full empty'
		}

	wsw7defaults = {
		'master1' : 'dpmaster.deathmask.net',
		'master2' : 'ghdigital.com',
		'master3' : 'excalibur.nvg.ntnu.no',
		'master4' : 'eu.master.warsow.net',
		'port' : '27950',
		'protocol' : '6094',
		'options' : 'full empty'
		}

	def __init__(self):
		self.cp = ConfigParser.SafeConfigParser()

		if not os.path.exists( self.cfg ):
			self.initCfg()
		else:
			self.cp.read( self.cfg )
	
	def getPath(self):
		if self.cp.getboolean( 'General', 'wsw_0.6' ):
			return os.path.expanduser( self.cp.get( 'General' , 'wsw0.6_path' ) ) , self.cp.get( 'General' , 'wsw0.6_args' ) 
		else:
			return os.path.expanduser( self.cp.get( 'General' , 'wsw0.7_path' ) ) , self.cp.get( 'General' , 'wsw0.7_args' ) 

	def getPing(self):
		return self.cp.getboolean( 'General', 'pingservers' )
	
	def getMasters(self):
		if self.cp.getboolean( 'General', 'wsw_0.6' ):
			section = 'Warsow 0.6'
		else:
			section = 'Warsow 0.7'
		port = self.cp.getint( section, 'port' )
		protocol = self.cp.getint( section, 'protocol' )
		options = self.cp.get( section, 'options' )
		for k,v in self.cp.items( section ):
			if 'master' in k:
				yield v, port, protocol, options 

	def setOpt(self, section, option, value):
		self.cp.set( section, option, value )
	
	def switchVer(self):
		ver = not self.cp.getboolean( 'General', 'wsw_0.6' )
		self.cp.set( 'General', 'wsw_0.6', str(ver) )
	
	def initCfg(self):
		self.cp.add_section( 'General' )
		for k, v in self.gendefaults.items():
			self.cp.set( 'General', k, v )

		self.cp.add_section( 'Warsow 0.6' )
		for k, v in self.wsw6defaults.items():
			self.cp.set( 'Warsow 0.6', k, v )

		self.cp.add_section( 'Warsow 0.7' )
		for k, v in self.wsw7defaults.items():
			self.cp.set( 'Warsow 0.7', k, v )
		self.writeCfg()

	def writeCfg(self):
		cfgfile = open( self.cfg , 'w' )
		self.cp.write( cfgfile )
		cfgfile.close()

if __name__ == '__main__':
	sets = Settings()
	print sets.getMasters()
