import os

import Ice, sys

import Murmur

class ServerCallbackI(Murmur.ServerCallback):
    def __init__(self, server, adapter):
        self.adapter = adapter
        self.server = server

    def userStateChanged(self, p, current=None):
        print("State of " + p.name + " changed")
        linked = p.identity != ""
        if p.session in cache:
            if cache[p.session] != linked:
                # TODO: Update in database
        else:
            cache[p.session] = linked
            # TODO: Update in database

    def userTextMessage(self, p, msg, current=None): pass
    def channelCreated(self, c, current=None): pass
    def channelRemoved(self, c, current=None): pass
    def channelStateChanged(self, c, current=None): pass
    def userConnected(self, p, current=None): pass
    def userDisconnected(self, p, current=None): pass


if __name__ == "__main__":
    global cache

    print("Initialization of Ice...")
    prop = Ice.createProperties(sys.argv)
    prop.setProperty("Ice.ImplicitContext", "Shared")

    idd = Ice.InitializationData()
    idd.properties = prop

    ice = Ice.initialize(idd)

    ice.getImplicitContext().put("secret", os.getenv("ICE_KEY"))

    print("Creation of TCP connections via Ice...")
    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy(os.getenv("ICE_PROXY"))) #
    adapter = ice.createObjectAdapterWithEndpoints("Callback.Client", os.getenv("ICE_CALLBACK"))
    adapter.activate()

    print("Finding started Mumble servers and adding callbacks to them...")
    for server in meta.getBootedServers():
        print("- Server discovered:")
        print(server)
        serverR = Murmur.ServerCallbackPrx.uncheckedCast(adapter.addWithUUID(ServerCallbackI(server, adapter)))
        server.addCallback(serverR)

    print("MumbleManager started successfully.")
    try:
        ice.waitForShutdown()
    except KeyboardInterrupt:
        print("Aborting...")

    ice.shutdown()
    print("Ice connection successfully terminated.")
