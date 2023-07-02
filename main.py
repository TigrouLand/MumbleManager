import json

import Ice
import Murmur
import sys
from flask import Flask, jsonify

murmurServer = None
app = Flask(__name__)


@app.route("/links")
def links():
    with Ice.initialize(sys.argv) as communicator:
        base = communicator.stringToProxy("Meta:tcp -h 127.0.0.1 -p 6502")

        meta = Murmur.MetaPrx.checkedCast(base)
        if not meta:
            raise RuntimeError("Invalid proxy")

        servers = meta.getAllServers()

        if len(servers) == 0:
            return jsonify(
                status='error',
                message='no mumble server found'
            )

        mumbleusers = servers[0].getUsers()
        userlist = []
        for i in mumbleusers:
            user = mumbleusers[i]
            if user.identity != "" and user.identity is not None:
                try:
                    jsonidentity = json.loads(user.identity)
                    minecraftname = jsonidentity['name']
                    userlist.append({
                        "mumbleName": user.name,
                        "minecraftName": minecraftname,
                        "linked": True
                    })
                except Exception as e:
                    userlist.append({
                        "mumbleName": user.name,
                        "error": repr(e),
                    })
            else:
                userlist.append({
                    "mumbleName": user.name,
                    "linked": False
                })

        try:
            return jsonify(userlist)
        except Exception as e:
            return jsonify(
                status='error',
                message=repr(e)
            )


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=8090)
