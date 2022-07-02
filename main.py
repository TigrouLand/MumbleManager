import os
import socket

import Ice, sys
import Murmur
from pymongo import MongoClient

cache = {}

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

if __name__ == "__main__":
    print("Creating Mongo connection...")
    mongo = MongoClient(host=os.getenv("MONGO_URI"))

    print("Initialization of Ice...")
    prop = Ice.createProperties(sys.argv)
    prop.setProperty("Ice.ImplicitContext", "Shared")

    idd = Ice.InitializationData()
    idd.properties = prop

    ice = Ice.initialize(idd)

    if os.getenv("ICE_SECRET") is not None:
        ice.getImplicitContext().put("secret", os.getenv("ICE_SECRET"))

    print("Creation of TCP connections via Ice...")

    iceHost = os.getenv("ICE_HOST")
    if os.getenv("ICE_DOCKER") is not None:
        iceHost = socket.gethostbyname(iceHost)

    icePort = os.getenv("ICE_PORT")
    iceCallbackHost = os.getenv("ICE_CALLBACK_HOST")

    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy("Meta:tcp -h %s -p %s" % (iceHost, icePort)))
    adapter = ice.createObjectAdapterWithEndpoints("Callback.Client", "tcp -h %s" % iceCallbackHost)
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
