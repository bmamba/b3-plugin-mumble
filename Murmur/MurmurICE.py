import Ice
import Murmur

class MurmurICE:
	
	def __init__(self, endpoint = 'tcp -h 127.0.0.1 -p 6502', secret = None):
		Ice.loadSlice('Murmur/Murmur.ice')
		prop = Ice.createProperties([])
		prop.setProperty('Ice.ImplicitContext', 'Shared')
		idd = Ice.InitializationData()
		idd.properties = prop
		ice = Ice.initialize(idd)
		if secret is not None and secret != '':
			ice.getImplicitContext().put('secret', secret.encode('utf-8'))
		endpoint = 'Meta:'+endpoint
		prx = ice.stringToProxy(endpoint.encode('utf-8'))
		self.murmur = Murmur.MetaPrx.checkedCast(prx)

	def connectToServer(self, serverid):
		self.server = self.murmur.getServer(serverid)
		if self.server:
			return True
		else:
			return False

	def getUsers(self):
		return self.server.getUsers()

	def findUsersByName(self, name):
		users = self.getUsers()
		found = []
		for userInt in users:
			user = users[userInt]
			if user.name.lower().find(name.lower()) > -1:
				found.append(user)
		return found

	def findUserBySession(self, session):
		users = self.getUsers()
		for userInt in users:
			user = users[userInt]
			if user.session == int(session):
				return user
	
	def getState(self, session):
		return self.server.getState(session)

	def setState(self, state):
		self.server.setState(state)

	def muteUser(self, session):
		state = self.getState(session)
		state.mute = True
		self.setState(state)

	def unmuteUser(self, session):
		state = self.getState(session)
		state.mute = False
		self.setState(state)

	def kickUser(self, session, reason):
		self.server.kickUser(session, reason.encode('utf-8'))

	def sendMsg(self, session, msg):
		self.server.sendMessage(session, msg.encode('utf-8'))


