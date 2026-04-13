from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

def create_topology():
    net = Mininet(controller=RemoteController, link=TCLink)
    c0 = net.addController('c0', ip='127.0.0.1', port=6633)
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s3, s2)
    net.start()
    print("Network started!")
    print("Primary path: h1 -> s1 -> s2 -> h2")
    print("Backup path:  h1 -> s1 -> s3 -> s2 -> h2")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
