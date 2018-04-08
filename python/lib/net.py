#!/usr/bin/python

__all__ = [
    "socketConnect",
    "socketRecv",
    "socketSend",
]

import sys
import pickle
import socket
import struct
import time

def socketConnect(
    peer,
    lg = None,
    sleep = 1,
    retry = True,
    timeout = None,
    logon = "",
    service = "5TM"
):
    if lg:
        lg.info("connecting to %s:%s" % peer)
    first = True
    while first or retry:
        first = False
        try:
            ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ss.settimeout(timeout)
            ss.connect(peer)
            break
        except socket.error as e:
            if lg:
                lg.warn("socket.error %s" % e.__str__())
            time.sleep(sleep)
    if lg:
        lg.info("successfully connected to %s:%s" % peer)
    return [ss, peer]

def socketSend(
    s,
    data,
    retry = True,
    lg = None,
    timeout = None
):
    peer = None
    (ss, peer) = s
    first = True
    success = False
    while 1:
        try:
            try:
                p = pickle.dumps(data)
            except:
                lg.error("aborting: data cannot be pickled")
                return success
            ss.send(struct.pack("Q", len(p)))
            success = ss.send(p)
            break
        except socket.error as e:
            if lg:
                lg.warn("socket.error while sending: %s" % e.__str__())
            if peer and (first or retry):
                first = False
                (ss, peer) = s[:] = socketConnect(
                    peer,
                    lg,
                    retry = retry,
                    timeout = timeout,
                )
                if retry:
                    time.sleep(0.2)
            else:
                break
    return success

def socketRecv(s, reconnect = True, lg = None, timeout = None):
    data = b''
    input = True
    peer = None
    ret = None
    (ss, peer) = s
    try:
        bytes = struct.unpack("Q", ss.recv(8))[0]
        while len(data) < bytes:                
            buflen = min(4096, bytes-len(data))
            input = ss.recv(buflen)
            if input == '':
                raise RuntimeError("Socket is broken.")
            data += input
        ret = pickle.loads(data)
    except socket.error as e:
        if lg:
            lg.warn("socket.error while receiving: %s" % e.__str__())
    except struct.error as e:
        if lg:
            lg.warn("struct.error: %s\n%s\n" % (e.__str__(),data))
    if peer and reconnect and not ret:
        s[:] = socketConnect(peer, lg, timeout = timeout)
    return ret
