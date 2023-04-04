#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import errno
import optparse
import socket
import threading
from typing import Any
import sys
import connection
from constants import *


class ClientThread(threading.Thread):
    """
    Es quien maneja los hilos y atiende distintas peticiones.
    """

    def __init__(self, clientAddress, clientsocket, directory):
        threading.Thread.__init__(self)
        self.socket_server = clientsocket
        self.directory = directory
        print(f"Connection from {clientAddress[0]}")

    def run(self):
        try:
            server_connection = connection.Connection(
                self.socket_server, self.directory)
            server_connection.handle()
            self.socket_server.close()
        except BrokenPipeError as s_closed:
            print("Disonnection from client")
            # Si se cerró la tubería y no podemos escribir --> Error y close().
            if s_closed.errno == errno.ESHUTDOWN:
                server_connection.close()


class Server(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print(f"Serving {directory} on {addr}:{port}.")
        self.num_of_clients = 0
        self.directory = directory
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Linea:32 es un flag que le dice al kernel que reutilice el socket y
        # que no espere el tiempo de expiración.
        # Más información en el readme.md link de sockets.
        self.socket_server.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_server.bind((addr, port))
        self.socket_server.listen(5)
        self.server_connection = Any

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        try:
            while True:
                client_socket, address_info = self.socket_server.accept()
                new_thread = ClientThread(
                    address_info, client_socket, self.directory)
                new_thread.start()
        except KeyboardInterrupt:
            print("KeyboardInterrupt:Disconect")
            self.socket_server.close()


def main():
    """Parsea los argumentos y lanza el server"""

    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar", default=DEFAULT_PORT)
    parser.add_option(
        "-a", "--address",
        help="Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option(
        "-d", "--datadir",
        help="Directorio compartido", default=DEFAULT_DIR)

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            f"Numero de puerto invalido: {repr(options.port)}\n")
        parser.print_help()
        sys.exit(1)

    server = Server(options.address, port, options.datadir)
    server.serve()


if __name__ == '__main__':
    main()
