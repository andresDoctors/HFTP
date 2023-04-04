# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import os
from base64 import b64encode
from genericpath import getsize, isfile
from constants import *

send_messages = {
    CODE_OK: (str(CODE_OK) + ' ' + error_messages[CODE_OK] + '\r\n').encode("ascii"),
    BAD_EOL: (str(BAD_EOL) + ' ' + error_messages[BAD_EOL] + '\r\n').encode("ascii"),
    BAD_REQUEST: (str(BAD_REQUEST) + ' ' + error_messages[BAD_REQUEST] + '\r\n').encode("ascii"),
    INTERNAL_ERROR: (str(INTERNAL_ERROR) + ' ' + error_messages[INTERNAL_ERROR] + '\r\n').encode("ascii"),
    INVALID_COMMAND: (str(INVALID_COMMAND) + ' ' + error_messages[INVALID_COMMAND] + '\r\n').encode("ascii"),
    INVALID_ARGUMENTS: (str(INVALID_ARGUMENTS) + ' ' + error_messages[INVALID_ARGUMENTS] + '\r\n').encode("ascii"),
    FILE_NOT_FOUND: (str(FILE_NOT_FOUND) + ' ' + error_messages[FILE_NOT_FOUND] + '\r\n').encode("ascii"),
}


MAX_MESSAGE_SIZE = 2**30


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.client_socket = socket
        self.directory = directory
        self.recieved_message = b''
        self.recieved_message_size = 0

        self.command_methods = {
            b'get_file_listing': self.get_file_listing,
            b'get_metadata': self.get_metadata,
            b'get_slice': self.get_slice,
            b'quit': self.quit,
        }

    def recieve_commands(self):
        """
        Cumple la funcion de un parser, recibe los comandos en un string,
        los parsea dividiendo en palabras
        y colocandolos en una lista para despues ser ejecutada
        """
        client_disconnection = False
        buffer_overflow = False
        commands_list = []
        while True:

            min_size = min(MAX_MESSAGE_SIZE - self.recieved_message_size, 1000)

            try:
                last_recieved_message = self.client_socket.recv(min_size)
            except ConnectionResetError:
                client_disconnection = True
                break

            if last_recieved_message == b'':
                client_disconnection = True
                break

            self.recieved_message += last_recieved_message
            self.recieved_message_size += len(last_recieved_message)

            if self.recieved_message.count(b'\n') > 0:

                commands_list = self.recieved_message.split(b'\r\n')
                self.recieved_message = commands_list.pop()
                self.recieved_message_size = len(self.recieved_message)

                break

            if self.recieved_message_size == MAX_MESSAGE_SIZE:

                self.recieved_message = b''
                self.recieved_message_size = 0
                buffer_overflow = True

                break

        return client_disconnection, buffer_overflow, commands_list

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """

        leave = False
        while not leave:

            (client_disconnection,
                buffer_overflow,
                commands_list,
             ) = self.recieve_commands()

            if client_disconnection:
                break

            if buffer_overflow:
                self.client_socket.send(send_messages[BAD_REQUEST])
                break

            leave = self.execute_commands(commands_list)

        self.client_socket.close()
        return leave

    def execute_commands(self, commands_list):
        """"
        Descripción del método execute_commands
        """
        leave = False
        for command in commands_list:

            if command.count(b'\n') != 0:
                send_message = send_messages[BAD_EOL]

            else:
                argv = command.split(b' ')
                argc = len(argv)
                cmd = argv[0]

                if cmd in self.command_methods:
                    leave, send_message = self.command_methods[cmd](argc, argv)
                else:
                    send_message = send_messages[INVALID_COMMAND]

        self.client_socket.send(send_message)
        return leave

    def get_file_listing(self, argc, argv):
        """
        Este comando no recibe argumentos y busca obtener la lista de
        archivos que están actualmente disponibles. El servidor responde
        con una secuencia de líneas terminadas en \r\n, cada una con el
        nombre de uno de los archivos disponible. Una línea sin texto
        indica el fin de la lista
        """
        if argc != 1:
            return False, send_messages[INVALID_ARGUMENTS]

        # Aqui la idea sería enviar la lista de archivos disponibles en directory
        send_message = send_messages[CODE_OK]
        list_of_files = os.listdir(self.directory)
        for file in list_of_files:
            send_message += file.encode("ascii") + b'\r\n'
        send_message += b'\r\n'

        return False, send_message

    def get_metadata(self, argc, argv):
        """
        Este comando recibe un argumento FILENAME especificando un
        nombre de archivo del cual se pretende averiguar el tamaño.
        El servidor responde con una cadena indicando su valor en bytes.
        """

        if argc != 2:
            return False, send_messages[INVALID_ARGUMENTS]

        # Recordar que para usar ésto hay que crear el directorio 'testdata'
        # (lo debería crear el server)
        # Y dentro del directorio crear un archivo para poder pasarlo como argumento.
        filename = argv[1]
        path = self.directory + "/" + filename.decode("ascii")

        if not isfile(path):
            return False, send_messages[FILE_NOT_FOUND]

        filename_size = str(getsize(path))
        send_message = send_messages[CODE_OK]
        # ---> TypeError fijarse de usar alguna conversión o algo.
        send_message += (str(filename_size)).encode("ascii")
        send_message += b'\r\n'

        return False, send_message

    def get_slice(self, argc, argv):
        """
        Este comando recibe en el argumento FILENAME el nombre de
        archivo del que se pretende obtener un slice o parte. La parte se
        especifica con un OFFSET (byte de inicio) y un SIZE (tamaño de la
        parte esperada, en bytes), ambos no negativos . El servidor
        responde con el fragmento de archivo pedido codificado en
        base64 y un \r\n.
        """
        if argc != 4:
            return False, send_messages[INVALID_ARGUMENTS]

        try:
            offset = int(argv[2])
            size = int(argv[3])
        except:
            return False, send_messages[INVALID_ARGUMENTS]

        filename = argv[1]
        # De ésta forma generamos el path y lo unimos, también lo traducimos,
        # para que nos quede 'testdata/test.txt' == 'directory/filename'
        path = self.directory+"/"+(filename.decode("ascii"))

        if not isfile(path):
            return False, send_messages[FILE_NOT_FOUND]

        file_size = getsize(path)

        # Si el offset indicado y el tamaño son más grandes que el tamñano del archivo ---> Error.
        if (offset + size) > file_size:
            send_message = send_messages[BAD_OFFSET]
            self.client_socket.send(send_message)

        # Con open abrimos un archivo pasandole el path y la opción 'rb'
        # (R=read, B=binary) para buscar la data.
        # No estoy del todo seguro para que funciona with, pero entiendo
        # que es la forma "segura" y economizadora de abrir archivos ya que los cierra luego de
        # abrirlos.
        with open(path, 'rb') as file_data:
            # seek nos permite ir recorriendo el archivo desde el offset, y por default su segundo
            # parámetro se setea en cero para arrancar desde el principio.
            # Go to the Offset-th byte in the file
            file_data.seek(offset)
            buffer = bytearray()
            data = file_data.read(size)     # Leemos hasta size
            buffer.extend(data)             # Agregamos al bytearray

        buffer = b64encode(buffer)
        send_message = send_messages[CODE_OK]
        send_message += buffer
        send_message += b'\r\n'

        return False, send_message

    def quit(self, argc, argv):
        """
        Este comando no recibe argumentos y busca terminar la
        conexión. El servidor responde con un resultado exitoso (0 OK) y
        luego cierra la conexión.
        """
        if argc != 1:
            return False, send_messages[INVALID_ARGUMENTS]

        return True, send_messages[CODE_OK]
