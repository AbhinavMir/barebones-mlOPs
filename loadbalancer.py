import os
import time
from flask import Flask, request, jsonify, render_template
import json
from PIL import Image
import requests
import random
import threading
import csv
import datetime

app = Flask(__name__)

results_dict = {}
results2_dict = {}

def add_to_CSV(id,ip, result, time1, imageSize):
    with open('results.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([id, ip, result, time1, imageSize])

def add_to_CSV_result(id,ip, result, time1, imageSize):
    with open('results2.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([id, ip, result, time1, imageSize])

def get_from_CSV(ip):
    with open('results.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    for i in range(len(data)):
        if data[i][1] == ip:
            return data[i]
    return None

def get_from_CSV_all():
    with open('results.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def change_from_processing_to_result(ip, result):
    with open('results.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    for i in range(len(data)):
        if data[i][1] == ip:
            data[i][2] = result
            data[i][3] = str(datetime.datetime.now())
    with open('results.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def get_time():
    return str(datetime.datetime.now())

def extract_data(input_string):
  pattern = r"\((.*?)\)"
  matches = re.findall(pattern, input_string)
  return matches

class metadata:
    queueCoutner = 0
    queueActive = 0
    queue = {}
    # Queue of images to be processed, maps IP to image and has a counter which acts as ID
    DEFAULT_PORT = 5000
    public_ip = {"server-0": "128.95.190.67", "server-1": "128.95.190.68",
                 "server-2": "128.95.190.69", "router": "128.95.190.66", "client": "128.95.190.64"}

# show all images in the static folder


@app.route('/images')
def images():
    # return names of all images in the static folder without using render_template
    return jsonify(os.listdir('static'))


def send_image(image, server):
    Image = open(image, 'rb')
    files = {'myImage': Image}
    response = requests.post("http://" + server.ip +
                             ":" + str(server.port) + '/imagenet', files=files)
    return response.text


def test_this_server(server):
    response = requests.get("http://" + server.ip +
                            ":" + str(server.port) + "/test")
    return response.text

@app.route("/")
def main():
    return "200: Connection Init"

def imageSize_to_dimensions(imageSize):
    return imageSize[0] * imageSize[1]

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        metadata.queue[metadata.queueCoutner] = str(request.remote_addr)
        image = request.files["myImage"]
        im = Image.open(image)
        ext = os.path.splitext(image.filename)
        # create a random number
        im.save("static/" + ext[0] + "-(" + str(request.remote_addr) +  ")" + ext[1])
        metadata.queueCoutner += 1
        add_to_CSV(metadata.queueCoutner, str(request.remote_addr), "Processing", get_time(), imageSize=imageSize_to_dimensions(im.size))
        return "200: Image Uploaded"
    else:
        return "Please use POST, not GET"

@app.route("/queue")
def get_queue():
    return str(metadata.queue)

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
    systems = [Server("server-0", metadata.public_ip["server-0"], metadata.DEFAULT_PORT), Server("server-1", metadata.public_ip["server-1"], metadata.DEFAULT_PORT), Server("server-2",
                                                                                                                                                                            metadata.public_ip["server-2"], metadata.DEFAULT_PORT), Server("router", metadata.public_ip["router"], metadata.DEFAULT_PORT), Server("client", metadata.public_ip["client"], metadata.DEFAULT_PORT)]

    server_dict = {"server-0": systems[0], "server-1": systems[1],
                   "server-2": systems[2], "router": systems[3], "client": systems[4]}

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
            try:
                response = requests.get(
                    "http://" + LoadBalancer.systems[i].ip + ":" + str(LoadBalancer.systems[i].port) + "/isBusy")
            except:
                inactive.append(LoadBalancer.systems[i])
                continue
            if (response.json()["busy"]):
                busy.append(LoadBalancer.systems[i])
            else:
                not_busy.append(LoadBalancer.systems[i])
        return str({"busy": busy, "not_busy": not_busy, "inactive": inactive})

    def get_server_by_function():
        busy = []
        not_busy = []
        inactive = []
        for i in range(LoadBalancer.CURRENT_SERVERS):
            # ping server/busy
            try:
                response = requests.get(
                    "http://" + LoadBalancer.systems[i].ip + ":" + str(LoadBalancer.systems[i].port) + "/isBusy")
            except:
                inactive.append(LoadBalancer.systems[i])
                continue
            if (response.json()["busy"]):
                busy.append(LoadBalancer.systems[i])
            else:
                not_busy.append(LoadBalancer.systems[i])
        return {"busy": busy, "not_busy": not_busy, "inactive": inactive}

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

    @app.route('/results')
    def get_results():
        userIP = request.remote_addr
        return get_from_CSV(userIP)
    
    @app.route('/resultsAll')
    def get_results_all():
        return get_from_CSV_all()

    def run():
        print("STARTED BACKGROUND")
        files = os.listdir("static")
        for file in files:
            os.remove("static/" + file)

        while True:
            files = os.listdir("static")
            for file in files:
                print("DETECTED FILE")
                for i in range(LoadBalancer.CURRENT_SERVERS):
                    if (test_this_server(LoadBalancer.systems[i])==200):
                        print("sending to " + LoadBalancer.systems[i].name)
                        res = send_image(file, LoadBalancer.systems[i])
                        print("OUTPUT")
                        dataName= extract_data(file)
                        print(res)
                        print("CHANGING CSV")
                        change_from_processing_to_result(dataName, res)
                        print("REMOVING FILE")
                        os.remove("static/" + file)
                        break

if __name__ == '__main__':

    for i in range(LoadBalancer.CURRENT_SERVERS):
        print(test_this_server(LoadBalancer.systems[i]))
    my_thread = threading.Thread(target=HelperFunctions.run)
    my_thread.start()
    app.run(host="0.0.0.0", port=metadata.DEFAULT_PORT+34, debug=True)