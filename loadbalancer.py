import os
import time
from flask import Flask
import json

app = Flask(__name__)

class metadata:
    DEFAULT_PORT = 8080
    public_ip = {"server-0": "128.95.190.67", "server-1": "128.95.190.68",
                 "server-2": "128.95.190.69", "router": "128.95.190.66", "client": "128.95.190.64"}


class Server:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port
        self.active = False
        self.connections = 0

    def isActive(self):
        return self.active

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __repr__(self):
        return f"{self.name} ({self.ip})"

    def ping(self):
        print(f"Pinging {self.name} ({self.ip})...")
        if self.active == False:
            print(f"{self.name} is down.")
        else:
            print(f"{self.name} is up.")

    def connect(self):
        if self.active == False:
            print(f"Cannot connect to {self.name} ({self.ip}).")
        else:
            print(f"Connecting to {self.name} ({self.ip})...")
            self.connections += 1

    def disconnect(self):
        if self.active == False:
            print(f"Cannot disconnect from {self.name} ({self.ip}).")
        else:
            print(f"Disconnecting from {self.name} ({self.ip})...")
            self.connections -= 1


class LoadBalancer:
    MAX_SERVERS = 3
    CURRENT_SERVERS = 2
    CURRENT_SYSTEMS = 5
    systems = [Server("server-0", metadata.public_ip["server-0"], metadata.DEFAULT_PORT), Server("server-1", metadata.public_ip["server-1"], metadata.DEFAULT_PORT), Server("server-2", metadata.public_ip["server-2"], metadata.DEFAULT_PORT), Server("router", metadata.public_ip["router"], metadata.DEFAULT_PORT), Server("client", metadata.public_ip["client"], metadata.DEFAULT_PORT)]

    server_dict = {"server-0": systems[0], "server-1": systems[1], "server-2": systems[2], "router": systems[3], "client": systems[4]}

    @app.route('/status')
    def get_systems():
        return HelperFunctions.turn_to_jsonack(str(LoadBalancer.systems))

    @app.route('/ping')
    def get_system_status():
        print("Testing...")
        HelperFunctions.test_all_servers()
        to_return = []
        for system in LoadBalancer.systems:
            to_return.append(system.ping())
        return HelperFunctions.turn_to_jsonack(to_return)

    @app.route('/activity')
    def get_system_activity():
        to_return = {}
        for system in LoadBalancer.systems:
            to_return[system.name] = system.connections
        return HelperFunctions.turn_to_jsonack(str(to_return))


class HelperFunctions:

    def turn_to_jsonack(data):
        # Add  json.dumps({'success':True}), 200, {'ContentType':'application/json'} and data to another field called data
        json_response = {"success": True, "data": data}
        return json_response

    def ping(ip, port):
        hostname = ip+":"+str(port)
        response = os.system("ping " + hostname)
        return response

    # test all servers and update loadbalancers
    def test_all_servers():
        for server in LoadBalancer.systems:
            test_server(server)

    def test_server(server):
        if HelperFunctions.ping(server.ip, metadata.DEFAULT_PORT) == 0:
            server.active = True
        else:
            server.active = False

    @app.route('/')
    def hello_world():
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
