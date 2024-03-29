# Spanning Tree project for GA Tech OMS-CS CS 6250 Computer Networks
#
# This defines a Switch that can can send and receive spanning tree 
# messages to converge on a final loop free forwarding topology.  This
# class is a child class (specialization) of the StpSwitch class.  To 
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm - 
# a non-distributed algorithm will not receive credit.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015, updated for new VM by Jared Scott and James Lohse

from Message import *
from StpSwitch import *


class Switch(StpSwitch):

    def __init__(self, idNum, topolink, neighbors):
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)

        # TODO: Define a data structure to keep track of which links are part of / not part of the spanning tree.
        self.claimedRoot: int = self.switchID
        self.distance: int = 0
        self.rootNeighbor: int = None
        self.activeLinks: Set[int] = set()

    def send_initial_messages(self):
        # TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
        #      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)
        for link in self.links:
            self.send_message(Message(self.claimedRoot, self.distance, self.switchID, link, False))
        return

    def process_message(self, message: Message):
        # TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.
        if message.pathThrough or message.origin == self.rootNeighbor:
            self.activeLinks.add(message.origin)
        else:
            self.activeLinks.discard(message.origin)

        newDistance: int = message.distance + 1

        # Found smaller root
        if message.root < self.claimedRoot:
            self.claimedRoot = message.root
            self.distance = newDistance
            self.rootNeighbor = message.origin
            self.activeLinks.add(message.origin)
            self.sendNeighborUpdates()
        elif message.root == self.claimedRoot:
            # Found shorter path to roots
            if newDistance < self.distance:
                self.distance = newDistance
                self.updateRootNeighbor(message.origin)
                self.sendNeighborUpdates()
            # Found path to root with smaller ID
            elif newDistance == self.distance and message.origin < self.rootNeighbor:
                self.updateRootNeighbor(message.origin)
                self.sendNeighborUpdates()

        return
    
    def updateRootNeighbor(self, newRoot: int):
        self.activeLinks.discard(self.rootNeighbor)
        self.rootNeighbor = newRoot
        self.activeLinks.add(newRoot)
    
    def sendNeighborUpdates(self):
        for link in self.links:
            if link == self.rootNeighbor:
                self.send_message(Message(self.claimedRoot, self.distance, self.switchID, link, True))
            else:
                self.send_message(Message(self.claimedRoot, self.distance, self.switchID, link, False))

    def generate_logstring(self):
        # TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked 
        #      only after the simulaton is complete.  Output the links included in the 
        #      spanning tree by increasing destination switch ID on a single line. 
        #      Print links as '(source switch id) - (destination switch id)', separating links 
        #      with a comma - ','.  
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string 
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project skeleton.
        return ", ".join(['{origin} - {link}'.format(origin=self.switchID, link=link) for link in sorted(self.activeLinks)])
