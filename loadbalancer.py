import os
import time
from flask import Flask, request, jsonify, render_template
import json
from PIL import Image
import requests

app = Flask(__name__)

class metadata:
    queueCoutner = 0
    queue = {}
    DEFAULT_PORT = 8080
    public_ip = {"server-0": "128.95.190.67", "server-1": "128.95.190.68",
                 "server-2": "128.95.190.69", "router": "128.95.190.66", "client": "128.95.190.64"}

def send_image(image, server):
    files = {'myImage': image}
    response = requests.post("http://" + server.ip + ":" + str(server.port), files=files)
    return response


@app.route("/upload", methods=["GET", "POST"])
@app.route("/", methods=['POST'])
def upload():
    if request.method == "POST":
        image = request.files["myImage"]
        im = Image.open(image)
        ext = os.path.splitext(image.filename)[1]
        im.save("static/" + str(metadata.queueCoutner) + ext)
        metadata.queueCoutner += 1
    else :
        return "Use POST, not GET"

class Server:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port
        self.active = False

    def isActive(self):
        return self.active

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __repr__(self):
        return f"{self.name} ({self.ip})"

class LoadBalancer:
    MAX_SERVERS = 3
    CURRENT_SERVERS = 3
    CURRENT_SYSTEMS = 5
    systems = [Server("server-0", metadata.public_ip["server-0"], metadata.DEFAULT_PORT), Server("server-1", metadata.public_ip["server-1"], metadata.DEFAULT_PORT), Server("server-2", metadata.public_ip["server-2"], metadata.DEFAULT_PORT), Server("router", metadata.public_ip["router"], metadata.DEFAULT_PORT), Server("client", metadata.public_ip["client"], metadata.DEFAULT_PORT)]

    server_dict = {"server-0": systems[0], "server-1": systems[1], "server-2": systems[2], "router": systems[3], "client": systems[4]}

    @app.route('/status')
    def get_systems():
        return HelperFunctions.turn_to_jsonack(str(LoadBalancer.systems))

class HelperFunctions:

    servers = LoadBalancer.systems


    @app.route("/track")
    def get_IP():
        return request.remote_addr

    @app.route('/busyChecker')
    def get_busy_status():
        busy = []
        not_busy = []
        inactive = []
        for i in range(LoadBalancer.CURRENT_SERVERS):
            # ping server/busy
            try:
                response = requests.get("http://" + LoadBalancer.systems[i].ip + ":" + str(LoadBalancer.systems[i].port) + "/isBusy")
            except:
                inactive.append(LoadBalancer.systems[i])
                continue
            if(response.json()["busy"]):
                busy.append(LoadBalancer.systems[i])
            else:
                not_busy.append(LoadBalancer.systems[i])
        return "Busy: " + str(busy) + "\nNot busy:  " + str(not_busy) + "\nInactive: " + str(inactive)

    def get_queue():
        queue = {}
        for server in LoadBalancer.systems:
            queue[server.name] = server.connections

    def turn_to_jsonack(data):
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
