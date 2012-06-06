#!/usr/bin/env python
"Queries IOQuake3 master servers."

#    PyQuake3Master, queries IOQuake3 master servers.
#    Copyright (C) 2008  Joakim Soderlund
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import socket

__author__    = "Joakim Soderlund"
__license__   = "GPLv2"
__copyright__ = "Copyright (C) 2008  Joakim Soderlund"
__date__      = "2008-09-06"
__version__   = "1.0"

def fetchServerList(master, port=27950, protocol=68, options="full empty", timeout=5):
	"Returns a list of servers from an IOQuake3 master server."
	servers = []
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect((master, port))
	s.settimeout(timeout)
	connectionString = "\xFF\xFF\xFF\xFFgetservers %d %s" % (protocol, options)
	s.send(connectionString)
	data = s.recv(65536)
	s.close()
	for pos in range(22, len(data)-7, 7):
		sdata = data[pos:pos+7]
		if sdata.startswith("\\"):
			server = ""
			for part in sdata[1:5]:
				server += str(ord(part)) + "."
			server = server[:-1] + ":"
			server += str((ord(sdata[5]) << 8) + ord(sdata[6]))
			servers.append(server)
	return servers

if __name__ == "__main__":
	print fetchServerList("master.quake3arena.com")

