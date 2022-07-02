import os
import Ice, sys
import Murmur
from pymongo import MongoClient


class ServerCallbackI(Murmur.ServerCallback):
    def __init__(self, server, adapter, database):
        self.adapter = adapter
        self.server = server
        self.database = database

    def setUserLinkedState(self, name, linked):
        self.database.players.find_one_and_update({"name": name}, {"$set": {"linked": linked}})

    def userStateChanged(self, p, current=None):
        print("State of " + p.name + " changed")
        linked = p.identity != ""
        if p.session in cache:
            if cache[p.session] == linked:
                return
        else:
            cache[p.session] = linked
        self.setUserLinkedState(p.name, linked)

    def userTextMessage(self, p, msg, current=None):
        pass

    def channelCreated(self, c, current=None):
        pass

    def channelRemoved(self, c, current=None):
        pass

    def channelStateChanged(self, c, current=None):
        pass

    def userConnected(self, p, current=None):
        pass

    def userDisconnected(self, p, current=None):
        pass


if __name__ == "__main__":
    global cache

    print("Creating Mongo connection...")
    mongo = MongoClient(host=os.getenv("MONGO_URI"))

    print("Initialization of Ice...")
    prop = Ice.createProperties(sys.argv)
    prop.setProperty("Ice.ImplicitContext", "Shared")

    idd = Ice.InitializationData()
    idd.properties = prop

    ice = Ice.initialize(idd)

    ice.getImplicitContext().put("secret", os.getenv("ICE_KEY"))

    print("Creation of TCP connections via Ice...")
    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy(os.getenv("ICE_PROXY")))
    adapter = ice.createObjectAdapterWithEndpoints("Callback.Client", os.getenv("ICE_CALLBACK"))
    adapter.activate()

    print("Finding started Mumble servers and adding callbacks to them...")
    for server in meta.getBootedServers():
        print("- Server discovered:")
        print(server)
        serverR = Murmur.ServerCallbackPrx.uncheckedCast(
            adapter.addWithUUID(ServerCallbackI(server, adapter, mongo.get_database("tigrouland"))))
        server.addCallback(serverR)

    print("MumbleManager started successfully.")
    try:
        ice.waitForShutdown()
    except KeyboardInterrupt:
        print("Aborting...")

    ice.shutdown()
    print("Ice connection successfully terminated.")
