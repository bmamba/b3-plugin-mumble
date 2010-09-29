# Mumble - A plugin to send commands to a mumble server
#
# Copyright (C) 2010 BlackMamba
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses/>.
#
# Requirements:
#   B3 v1.3+
#   python-zeroc-ice
#   Murmur 1.2.2

import Murmur.MurmurICE
import b3, b3.plugin
import re

class MumblePlugin(b3.plugin.Plugin):
	
	def startup(self):
		self._adminPlugin = self.console.getPlugin('admin')
		if not self._adminPlugin:
			self.error('Could not find admin plugin')
			return False

		try:
			serverid = self.config.getInt('settings', 'serverid')
		except:
			serverid = 1

		try:
			secret = self.config.get('settings', 'secret')
		except:
			secret = None

		try:
			endpoint = self.config.get('settings', 'endpoint')
		except:
			endpoint = 'tcp -h 127.0.0.1 -p 6502'

		self.murmur = Murmur.MurmurICE.MurmurICE(endpoint, secret)
		self.debug(serverid)
		if not self.murmur.connectToServer(serverid):
			self.error('Could not connect to murmur server')
			return False
	
		commands = ['m_kick', 'm_msg', 'm_mute', 'm_unmute', 'm_list']
		level = {}

		for cmd in commands:
			try:
				level[cmd] = self.config.getInt('commands',cmd)
			except:
				level[cmd] = 100
		
		self._adminPlugin.registerCommand(self, 'm_kick', level['m_kick'], self.cmd_kick)
		self._adminPlugin.registerCommand(self, 'm_msg', level['m_msg'], self.cmd_msg)
		self._adminPlugin.registerCommand(self, 'm_mute', level['m_mute'], self.cmd_mute)
		self._adminPlugin.registerCommand(self, 'm_unmute', level['m_unmute'], self.cmd_unmute)
		self._adminPlugin.registerCommand(self, 'm_list', level['m_list'], self.cmd_list)

	def findUser(self, client, name):
		if re.match('^[0-9]+$', name, re.I):
			user = self.murmur.findUserBySession(name)
			if user is None:
				client.message('Could not find user on mumble server with this session id')
				self.debug('Could not find user with session id %s' % name)
				return
			return user
		else:
			users = self.murmur.findUsersByName(name)
			if len(users) == 1:
				return users[0]
			elif len(users) == 0:
				client.message('Could not find user on mumble server')
				self.debug('Could not find user %s on mumble server' % name)
				return
			else:
				client.message('^7Found more than one user with this name:')
				for id in users:
					user = users[id]
					client.message('[%s] %s' % (user.name, user.session))
				return

	def dataSplit(self, client, data, paramNr, restrictive = False):
		dataSplit = data.split()
		if len(dataSplit) == paramNr or (len(dataSplit)>=paramNr and not restrictive):
			return data.split(None, paramNr - 1)
		else:
			client.message('^7Invalid parameters')
			self.debug('Need %s parameters, %s are given' % (str(paramNr), str(len(dataSplit))))
			return

	def cmd_kick(self, data, client, cmd=None):
		"""\
		<mumble_client> <reason> - kick client from mumble server
		"""
		dataSplit = self.dataSplit(client, data, 2)
		if dataSplit is None:
			return
		name = dataSplit[0]
		reason = dataSplit[1]
		user = self.findUser(client, name)
		if user is not None:
			self.murmur.kickUser(user.session, '%s: %s' % (user.name, reason))
			client.message('User %s was kicked' % user.name)
			self.debug('User %s was kicked' % user.name)

	def cmd_msg(self, data, client, cmd=None):
		"""\
		<mumble_client> <message> - send a message to a client
		"""
		dataSplit = self.dataSplit(client, data, 2)
		if dataSplit is None:
			return
		name = dataSplit[0]
		msg = dataSplit[1]
		user = self.findUser(client, name)
		if user is not None:
			self.murmur.sendMsg(user.session, '%s: %s' % (client.name, msg))
			client.message('Message was sent')

	def cmd_mute(self, data, client, cmd=None):
		"""\
		<mumble_client> - mutes a client
		"""
		dataSplit = self.dataSplit(client, data, 1, True)
		if dataSplit is None:
			return
		name = dataSplit[0]
		user = self.findUser(client, name)
		if user is not None:
			self.murmur.muteUser(user.session)
			client.message('User was muted')

	def cmd_unmute(self, data, client, cmd=None):
		"""\
		<mumble_client> - unmutes a client
		"""
		dataSplit = self.dataSplit(client, data, 1, True)
		if dataSplit is None:
			return
		name = dataSplit[0]
		user = self.findUser(client, name)
		if user is not None:
			self.murmur.unmuteUser(user.session)
			client.message('User was unmuted')

	def cmd_list(self, data, client, cmd=None):
		"""\
		lists all clients on mumble server
		"""
		users = self.murmur.getUsers()
		if len(users) == 0:
			client.message('^7No users on mumble server')
			return
		i = 0;
		text = ''
		for id in users:
			if text != '':
				text += ', '
				if i % 3 == 0:
					client.message(text)
					text = ''
			user = users[id]
			text += '[%s]: %s' % (user.session, user.name)
			i += 1
		if text != '':
			client.message(text)	
