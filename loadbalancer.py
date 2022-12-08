import os

class metadata:
    DEFAULT_PORT = 8080
    public_ip={"server-0": "128.95.190.67", "server-1": "128.95.190.68","server-2": "128.95.190.69", "router": "128.95.190.66", "client": "128.95.190.64"}

class Server:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port
        self.active = False
        self.connections = 0

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
    systems = [Server("server-0", metadata.public_ip["server-0"], metadata.DEFAULT_PORT), Server("server-1", metadata.public_ip["server-1"], metadata.DEFAULT_PORT), Server("server-2", metadata.public_ip["server-2"], metadata.DEFAULT_PORT), Server("router", metadata.public_ip["router"], metadata.DEFAULT_PORT), Server("client", metadata.public_ip["client"], metadata.DEFAULT_PORT)]

    def get_servers():
        return LoadBalancer.systems[:LoadBalancer.CURRENT_SERVERS]

class HelperFunctions:
    def ping(ip, port):
        hostname = ip+":"+str(port)
        response = os.system("curl " + hostname)
        return response

    def test_all_servers():
        for server in LoadBalancer.servers:
            if HelperFunctions.ping(server.ip, metadata.DEFAULT_PORT) == 0:
                server.active = True
            else:
                server.active = False
        
print(HelperFunctions.ping(metadata.public_ip["client"], metadata.DEFAULT_PORT))
print(LoadBalancer.get_servers())