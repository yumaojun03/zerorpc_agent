#!/usr/bin/env python


from gevent import monkey; monkey.patch_socket()
import gevent
import os
from datetime import datetime

import zerorpc
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

SECURE = True

base_dir = os.path.dirname(__file__)
keys_dir = os.path.join(base_dir, 'certificates')
public_keys_dir = os.path.join(base_dir, 'public_keys')
secret_keys_dir = os.path.join(base_dir, 'private_keys')


class Service(object):

    def hello(self, msg):
        print gevent.getcurrent(), datetime.now() # here do your work
        gevent.sleep(0)
        return "hello, %s" % msg


def run_server():
    endpoint = 'tcp://0.0.0.0:5555'
    print("endpoint: {}".format(endpoint))
    srv = zerorpc.Server(Service())

    ctx = zerorpc.Context.get_instance()
    auth = ThreadAuthenticator(ctx)
    auth.start()
    auth.allow('127.0.0.1')
    # Tell authenticator to use the certificate in a directory
    auth.configure_curve(domain='*', location=public_keys_dir)

    zmq_socket = srv._events._socket

    server_secret_file = os.path.join(secret_keys_dir, "server.key_secret")
    server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
    if SECURE:
        print("Secure transport")
        zmq_socket.curve_secretkey = server_secret
        zmq_socket.curve_publickey = server_public
        zmq_socket.curve_server = True

    srv.bind(endpoint)
    srv_task = gevent.spawn(srv.run)
    srv_task.join()


def main():
    run_server()


if __name__ == "__main__":
    main()