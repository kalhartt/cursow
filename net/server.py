#!/usr/bin/env python2
import net, connection, re, subprocess

class REs(object): ##{{{
	"""
	A container for regular expressions used to parse the
	result of certain well-known server commands. In best
	Perl tradition, they are totally unreadable. 8-O
	"""
	# parse a player line from "getstatus" command
	# 11 50 "|ALPHA|MarvinTheSpud"
	GETSTATUS = re.compile(r'^(-?)(\d+) (\d+) "(.*)"')
	# parse a player line from "rcon status" command
	# 2 0 70 |ALPHA| Mad Professor^7 0 127.0.0.1:35107 229 25000
	RCON_STATUS = re.compile(r'\s*(\d+)\s+(-?)(\d+)\s+(\d+)\s+(.*)\^7\s+(\d+)\s+(\S*)\s+(\d+)\s+(\d+)')
	STRIPCOLOR = re.compile(r'(\^[0-9])')
	PING = re.compile( r'\d+\.\d+/(\d+\.\d+)/\d+\.\d+/\d+\.\d+')
	##}}}

class Player(object): ##{{{
	"""Record collecting information about a player."""

	def __init__(self): ##{{{
		"""Create empty record with lots of None fields."""
		# information from getstatus request
		self.frags = None
		self.ping = None
		self.name = None
		# information from rcon status request
		self.address = None
		self.slot = None
		self.lastmsg = None
		self.qport = None
		self.rate = None
		# information from dumpuser request
		self.guid = None
		self.variables = None ##}}}

	def __str__(self): ##{{{
		"""Short summary of name, address, and guid."""
		return ("Player<name: %s; address: %s; guid: %s; frags: %s; ping: %s>" %
				(self.name, self.address, self.guid, self.frags, self.ping)) ##}}}

	## }}}

class Server(object): ##{{{
	"""Record collecting information about a server."""

	def __init__(self, host, port, filter_colors=False): ##{{{
		"""Create empty record with lots of None fields."""
		# meta information before connect
		self.connection = connection.Connection(host, port, retries=3)
		self.filter = filter_colors
		self.host = host
		self.port = port
		# shortcuts to well-known variables
		self.name = None
		self.game = None
		self.map = None
		self.protocol = None
		self.version = None
		# dict of *all* server variables
		self.variables = {}
		# list of players
		self.players = [] ##}}}

	def address(self): ##{{{
		"""Helper to get "ip:port" for a server."""
		return "%s:%s" % (self.host, self.port) ##}}}

	def get_address(self): ##{{{
		"""Compatibiltiy alias for address()."""
		return self.address() ##}}}

	def command(self, command): ##{{{
		"""Wrapper calling Connection.command() for a server."""
		return self.connection.command(command) ##}}}

	def filter_name(self, name): ##{{{
		"""Helper to remove Quake 3 color codes from player names."""
		result = ""
		i = 0
		while i < len(name):
			if name[i] == "^":
				i += 2
			else:
				result += name[i]
				i += 1
		return result ##}}}

	def parse_getstatus_variables(self, data): ##{{{
		"""
		Parse variables portion of getstatus response.
		The format is "\\key\\value\\key\\value..." and
		we turn that into a dictionary; selected values
		are also made fields.
		"""
		data = data.split("\\")[1:]
		assert len(data) % 2 == 0
		keys = data[0::2]
		values = data[1::2]
		self.variables = dict(zip(keys, values))

		self.clients= int(self.variables.get('clients', 1))
		if 'sv_hostname' in self.variables:
			self.name = self.variables['sv_hostname']
			self.name2 = re.sub( REs.STRIPCOLOR, '', self.name )
			self.gametype = self.variables.get("gametype", '')
		elif 'tv_name' in self.variables:
			self.name = self.variables['tv_name']
			self.name2 = re.sub( REs.STRIPCOLOR, '', self.name )
			self.gametype = 'tv'
		else:
			self.name = ''
			self.name2 = ''
			self.gametype = ''
		self.game = self.variables.get('gamename', '')
		self.instagib = int(self.variables.get( 'g_instagib', 0 ))
		self.map = self.variables.get("mapname", '')
		self.maxclients= int(self.variables.get("sv_maxclients",0))
		self.mod = self.variables.get("fs_game", '')
		self.password = int(self.variables.get( 'g_needpass', 0 ))
		self.ping = 0
		self.protocol = self.variables["protocol"]
		self.version = self.variables["version"] ##}}}
	
	def parse_getstatus_players(self, data): ##{{{
		"""
		Parse players portion of getstatus response.
		TODO
		"""
		assert len(data) > 0
		self.players = []

		for record in data:

			match = REs.GETSTATUS.match(record)
			if match:
				negative, frags, ping, name = match.groups()
				if negative == "-":
					frags = "-" + frags
				if self.filter:
					name = self.filter_name(name)

				player = Player()
				player.frags = int(frags)
				player.ping = int(ping)
				player.name = name
				self.players.append(player) ##}}}

	def parse_getstatus(self, data): ##{{{
		"""
		Parse server response to getstatus command. The
		first line of the response has lots of variables
		while the following lines have players.
		"""
		data = data.strip().split("\n")

		variables = data[0].strip()
		players = data[1:]

		self.parse_getstatus_variables(variables)

		if len(players) > 0:
			self.parse_getstatus_players(players)
		else:
			self.players = []##}}}

	def getstatus(self): ##{{{
		"""
		Basic server query for public information only.
		"""
		status, data = self.connection.command("getstatus")
		if status == "statusResponse":
			self.parse_getstatus(data) ##}}}

	def getPing(self): ##{{{
		"""
		Super hacky!
		"""
		proc = subprocess.Popen( ['ping', '-c', '3', '-w', '2', self.host], stdout=subprocess.PIPE )
		for line in proc.stdout:
			found = re.search( REs.PING, line )
			if found:
				self.ping = float(found.group(1))
				return
		##}}}

	def __str__(self): ##{{{
		"""Short summary of name, address, and map."""
		return ("Server<name: %s; address: %s; map: %s>" %
			(self.name, self.address(), self.map)) ##}}}

	##}}}

def MasterServer(host, port=27950, protocol=12, options="full empty", timeout=1): ##{{{
	"""
	Method to query master server and return a
	list of ip addresses
	"""
	servers = set()
	master = connection.Connection( host, port, timeout=timeout, size=65536)
	## Warsow has
	## requeststring = va( "%s %c%s %i %s %s", cmdname, toupper( modname[0] ), modname+1, SERVERBROWSER_PROTOCOL_VERSION,
	##	 filter_allow_full ? "full" : "",
	##	 filter_allow_empty ? "empty" : "" );
	data = master.command_raw( "getservers Warsow %d %d %s" % ( protocol, protocol-1, options ) )
	for pos in range(22, len(data)-7, 7):
		sdata = data[pos:pos+7]
		if sdata.startswith("\\"):
			server = ""
			for part in sdata[1:5]:
				server += str(ord(part)) + "."
			server = server [:-1] + ":"
			server += str((ord(sdata[5])<<8) + ord(sdata[6]))
			servers.add(server)
	return servers ##}}}

if __name__=='__main__':
	print MasterServer('dpmaster.deathmask.net')
