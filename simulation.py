#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Week 5"""

import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--file', help='csv file name')
parser.add_argument('--servers', help='number of servers')
args = parser.parse_args()

class Queue(object):
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)


class Server:
    def __init__(self):
        self.currentRequest = None
        self.timeRemaining = 0
        self.queue = Queue()

    def getQueue(self):
        return self.queue

    def tick(self):
        if self.currentRequest != None:
            self.timeRemaining = self.timeRemaining - 1
            if self.timeRemaining <= 0:
                self.currentRequest = None

    def busy(self):
        if self.currentRequest != None:
            return True
        else:
            return False

    def startNext(self,newRequest):
        self.currentRequest = newRequest
        self.timeRemaining = newRequest.getProcessingTime()

class Request:
    def __init__(self,request):
        self.timestamp = int(request[0])
        self.processingTime = int(request[2])

    def getStamp(self):
        return self.timestamp

    def getProcessingTime(self):
        return self.processingTime

    def waitTime(self, currenttime):
        return currenttime - self.timestamp


def simulateOneServer(fileName):
    server = Server()
    queue = server.getQueue()

    requestDict ={}
    waitingtimes = []
    # Opens the csv, makes dict with key[timestamp]
    # since more than 1 req can come in at once
    with open(fileName, 'rb') as csvFile:
        requestReader = csv.reader(csvFile)
        for request in requestReader:
            timestamp = int(request[0])
            if timestamp in requestDict:
                requestDict[timestamp].append(request)
            else:
                requestDict[timestamp] = [request]

    currentSecond = 0
    while True:
        currentSecond += 1
        # add any requests for the currentSecond to queue and 
        # delete request from array of request arrays
        # Once counter hits the req time from dict key:
        if currentSecond in requestDict:
            for request in requestDict[currentSecond]:
                queue.enqueue(Request(request))
            del requestDict[currentSecond]

        if (not server.busy()) and (not queue.isEmpty()):
            nextRequest = queue.dequeue()
            waitingtimes.append(nextRequest.waitTime(currentSecond))
            server.startNext(nextRequest)

        server.tick()

        if (not server.busy()) and (queue.isEmpty()) and (
            len(requestDict) == 0):
            break

    averageWait=sum(waitingtimes)/float(len(waitingtimes))
    print("Average Wait %6.2f secs for %3d requests"%(
        averageWait,len(waitingtimes)))

def simulateManyServer(fileName, numServers):
    servers = []
    serverCnt = 0

    # create n servers
    while serverCnt < numServers:
        servers.append(Server())
        serverCnt += 1

    requestDict ={}
    waitingtimes = []

    with open(fileName, 'rb') as csvFile:
        requestReader = csv.reader(csvFile)
        for request in requestReader:
            timestamp = int(request[0])
            if timestamp in requestDict:
                requestDict[timestamp].append(request)
            else:
                requestDict[timestamp] = [request]

    currentSecond = 0
    nextServer = 0
    while True:
        currentSecond += 1
        if currentSecond in requestDict:
            for request in requestDict[currentSecond]:
                servers[nextServer].getQueue().enqueue(Request(request))
            del requestDict[currentSecond]

            # move to next server
            if nextServer == numServers - 1:
                nextServer = 0
            else:
                nextServer += 1

        for server in servers:
            queue = server.getQueue()
            if (not server.busy()) and (not queue.isEmpty()):
                nextRequest = queue.dequeue()
                waitingtimes.append(nextRequest.waitTime(currentSecond))
                server.startNext(nextRequest)
            server.tick()

        if len(requestDict) == 0:
            done = 0
            for server in servers:
                if (not server.busy()) and (server.getQueue().isEmpty()):
                    done += 1
            if (done == numServers):
                break

    averageWait=sum(waitingtimes)/float(len(waitingtimes))
    print("Average Wait %6.2f secs for %3d requests"%(
        averageWait,len(waitingtimes)))


def main():
    csvFile = args.file
    servers = args.servers
    if servers == None:
        simulateOneServer(csvFile)
    else:
        simulateManyServer(csvFile, int(servers))


if __name__ == '__main__':
    main()
