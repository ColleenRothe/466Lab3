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

    server = network.Host(3)
    object_L.append(server)

    client2 = network.Host(2)
    object_L.append(client2)

    # table_rule_a = {'source': 1, 'next': 'B', 'source2':2, 'next2':'C'}
    # table_rule_b = {'source': 1, 'next': 'D'}
    # table_rule_c = {'source': 2, 'next': 'D'}
    # table_rule_d = {'source': 1, 'next': '3', 'source2':2, 'next2':'3'}

    #next/next2 means go out interface...
    table_rule_a = {'source': 1, 'next': 0, 'source2': 2, 'next2': 1}
    table_rule_b = {'source': 1, 'next': 0}
    table_rule_c = {'source': 2, 'next': 0}
    table_rule_d = {'source': 1, 'next': 0, 'source2': 2, 'next2': 0} #next2 could be 1?

    ##interface count is the number of input and output interfaces (needs to be 2 for A)?
    router_a = network.Router(name='A', intf_count=2, max_queue_size=router_queue_size, table_rule=table_rule_a)
    object_L.append(router_a)

    router_b = network.Router(name='B', intf_count=1, max_queue_size=router_queue_size, table_rule=table_rule_b)
    object_L.append(router_b)

    router_c = network.Router(name='C', intf_count=1, max_queue_size=router_queue_size,table_rule=table_rule_c)
    object_L.append(router_c)

    router_d = network.Router(name='D', intf_count=2, max_queue_size=router_queue_size,table_rule=table_rule_d)
    object_L.append(router_d)




    # create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    # add all the links
    #client=1, server=2, other=3

    #top path
    link_layer.add_link(link.Link(client, 0, router_a, 0, 50))  # mtu=50
    link_layer.add_link(link.Link(router_a, 0, router_b, 0, 50))  # mtu=50
    link_layer.add_link(link.Link(router_b, 0, router_d, 0, 50))  # mtu=50


    #bottom path
    link_layer.add_link(link.Link(client2, 0, router_a, 1, 50))  # mtu=50
    link_layer.add_link(link.Link(router_a, 1, router_c, 0, 50))  # mtu=50
    link_layer.add_link(link.Link(router_c, 0, router_d, 1, 50))  # mtu=50
    link_layer.add_link(link.Link(router_d, 0, server, 0, 50))  # mtu=50


    # start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client.__str__(), target=client.run))
    thread_L.append(threading.Thread(name=client2.__str__(), target=client2.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))
    thread_L.append(threading.Thread(name=server.__str__(), target=server.run))





    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    # create some send events
    #client.udt_send(1,3,'We are at Grace Hopper having a super time. It is the best. Gonna stay in Houston for days.')
    client.udt_send(2,3,'Sitting in the cs lab is the most fun in the world')


    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")



# writes to host periodically
