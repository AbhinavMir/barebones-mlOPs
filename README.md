If you're storing your private key in ~/.ssh, it makes sense to `chmod 400 ~/.ssh/id_geni_ssh_rsa` to prevent others from reading it. This also prevents ssh from complaining about the key being world-readable.

To connect to server-0 machine:

```
ssh -i ~/.ssh/id_geni_ssh_rsa fjensen@pcvm1-18.instageni.washington.edu -p 22
```

To connect to client machine:

```
ssh -i ~/.ssh/id_geni_ssh_rsa fjensen@pcvm1-16.instageni.washington.edu
```

To connect to router machine:

```
ssh -i ~/.ssh/id_geni_ssh_rsa fjensen@pcvm1-17.instageni.washington.edu -p 22
``` 


Client ifconfig

```
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 128.95.190.64  netmask 255.255.255.0  broadcast 128.95.190.255
        inet6 fe80::1e:a8ff:fe3c:3530  prefixlen 64  scopeid 0x20<link>
        ether 02:1e:a8:3c:35:30  txqueuelen 1000  (Ethernet)
        RX packets 28429  bytes 46008543 (46.0 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 16565  bytes 1330443 (1.3 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.10.1.1  netmask 255.255.255.0  broadcast 10.10.1.255
        inet6 fe80::1b:8fff:fe52:f956  prefixlen 64  scopeid 0x20<link>
        ether 02:1b:8f:52:f9:56  txqueuelen 1000  (Ethernet)
        RX packets 74  bytes 6489 (6.4 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 32  bytes 4712 (4.7 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

To launch Imagenet Server
Connect to server 0 on which Anaconda and the needed python packages along with app.py are located

launch Anaconda
```
source ~/anaconda3/bin/activate
```

Then launch Flask Server
```
python -m flask run --host=0.0.0.0
```
