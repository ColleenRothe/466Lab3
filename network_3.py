'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import queue
import threading

global fragment_list
fragment_list = []

global blank_count
blank_count = 0

## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);

    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None

    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)

## Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths
    dst_addr_S_length = 5
    source_length = 5
    flag_length = 2 ##can only be a 0 or 1
    offset_length = 2 ##???? not sure about this


    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, offset, flag, source_addr, data_S, ):
        self.dst_addr = dst_addr
        self.offset = offset
        self.flag = flag
        self.source_addr = source_addr
        self.data_S = data_S

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += str(self.offset).zfill(self.offset_length)
        byte_S += str(self.flag).zfill(self.flag_length)
        byte_S += str(self.source_addr).zfill(self.source_length)
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length]) ## 0-5
        offset = int(byte_S[NetworkPacket.dst_addr_S_length: NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length]) ##5-7
        flag = int(byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length : NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length + NetworkPacket.flag_length ])
        source_addr = int(byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length + NetworkPacket.flag_length: NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length + NetworkPacket.flag_length+NetworkPacket.source_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length + NetworkPacket.flag_length+NetworkPacket.source_length  : ] ##to the end...
        return self(dst_addr, offset, flag, source_addr, data_S)




## Implements a network host for receiving and transmitting data
class Host:

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination

    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)

    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self,src_addr, dst_addr, data_S):

        #p = NetworkPacket(dst_addr, 400,1,data_S)
        # print("TESTING FLAG HERE")
        # print(p.flag)
        # print("TESTING OFFSET HERE")
        # print(p.offset)
        # print("TESTING DATA HERE")
        # print(p.data_S)
        # print("TESTING Address HERE")
        # print(p.dst_addr)
        source_num = src_addr

        if len(data_S) > 20:  # probably better way to grab this, account for the 00002
            calced = (int)(len(data_S) / 20) + 1  # how many packets you will need (round up)
            start = 0  # index to start grabbing
            stop = 19  # index to stop grabbing
            data = ''  # save the data string


            for i in range(calced):  # for each new packet
                data = ''  # set string = 0
                for j in range(start, stop, 1):

                    if (j >= len(data_S)):  # if the index is out of bounds
                        break  # get out of the loop

                    data = data + data_S[j]  # append to string


                # send packet with data
                flag = 1 #all but last have flag = 1
                if(stop>=len(data_S)):
                    flag = 0 ## last fragments flag should be a 0
                p = NetworkPacket(dst_addr, stop, flag, source_num, data) ##"stop" is the offset
                print("SOURCE")
                print(p.source_addr);
                # print("CHECK THE OFFSET")
                # print(p.offset)
                self.out_intf_L[0].put(p.to_byte_S())  # send packets always enqueued successfully
                print('%s: sending packet "%s"' % (self, p))
                # update start and stop
                start = stop
                stop = start + 20


        else:  # length not a problem
            print("ELSE")
            p = NetworkPacket(dst_addr, 0, 0, source_num, data_S)
            self.out_intf_L[0].put(p.to_byte_S())  # send packets always enqueued successfully
            print('%s: sending packet "%s"' % (self, p))

    ## receive fragments from the network layer and put them back together into one packet?
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        full_data = '' #where to put this?
        global fragment_list
        global blank_count

        if pkt_S is not None:
            #print("NOT NONE")
                #Add the packet string to the fragment list
            fragment_list.append(pkt_S)
                #get the flag
            flag = int(pkt_S[NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length: NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length + NetworkPacket.flag_length])

            if (flag == 0):
                sorted_list = []
                while len(fragment_list) > 0:
                    smallest = 999999999
                    small_pkt = None
                    for i in fragment_list:
                        offset = int(i[NetworkPacket.dst_addr_S_length: NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length])
                        if offset < smallest:
                            smallest = offset
                            small_pkt = i
                    sorted_list.append(small_pkt)
                    fragment_list.remove(small_pkt)
                result_string = ''
                for j in sorted_list:
                    message = j[NetworkPacket.dst_addr_S_length + NetworkPacket.offset_length + NetworkPacket.flag_length  : ]
                    result_string += message

                print('%s: received packet "%s"' % (self, result_string))




    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return



## Implements a multi-interface router described in class
class Router:

    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size,table_rule):
        self.stop = False #for thread termination
        self.name = name
        self.table_rule = table_rule
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    if self.name is "A":
                        if p.sourc_addr is self.table_rule:
                            self.out_intf_L

                    self.out_intf_L[i].put(p.to_byte_S(), True)
                    print('%s: forwarding packet "%s" from interface %d to %d' % (self, p, i, i))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass

    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return
