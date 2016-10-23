'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network
import link
import threading
from time import sleep

##configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 3  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network nodes
    client = network.Host(1)
    object_L.append(client)

    server = network.Host(2)
    object_L.append(server)

    #started to create the new configuration.....
    router_a = network.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)

    router_b = network.Router(name='B', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_b)

    router_c = network.Router(name='C', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_c)

    router_d = network.Router(name='D', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_d)




    # create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    # add all the links
    link_layer.add_link(link.Link(client, 0, router_a, 0, 50))  # mtu=50
    link_layer.add_link(link.Link(router_a, 0, server, 0, 30)) #changed this MTU!

    # start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client.__str__(), target=client.run))
    thread_L.append(threading.Thread(name=server.__str__(), target=server.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    # create some send events
    client.udt_send(2,'We are at Grace Hopper having a super time. It is the best. Gonna stay in Houston for days.' )

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")



# writes to host periodically
