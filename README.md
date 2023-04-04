# README #

### Introducción

Implementación de servidor hecho en Py3, utilizando librerías tales cómo:

* threading
* socket
* connection
* errno
* os
* base64
* genericpath
* optparse --> módulo deprecado

### Run

Arrancamos el servidor

```sh

python3 server.py

```

En otra consola, nos conectamos al servidor vía telnet:

```sh

telnet 0.0.0.0 19500

```

Envíamos request y vemos su devolución.

Request posibles:

- > get_metadata client.py   

- > get_slice client.py 0 1868

- > get_file_listing

- > quit


### Desarrollo ###

1. Comenzamos leyendo el enunciado y completando el archivo 'server.py' en clase, ahí fue donde leímos casi todo de Sockets de la documentación de Py, luego Andrés fue quien armó la estructura del archivo 'connection.py' donde elaboró el parser, luego fingimos una funcionalidad sólo para ver que la estructura funcionara, siguiendo con la filosofía de "código feo, que ande y después mejoramos", obteniendo así un código spaghetti que nos devolvía prints. Aún faltaba cumplir la consigna, asi que le dimos funcionalidad a los comandos (Juanes), algunas de éstas las hicimos en clase y otras fuera de clase(otra vez complicado separar quién hizo qué).

2. Terminada ésa etapa y teniendo ya nuestro código feo pero cumplidor de consigna, modularizamos la estructura, para pasar a un código lindo y cumplidor. Aplicamos PEP8 entre otras cuestiones de prolijidad ó de "estandarización" de código.
Ya con el lab terminado nos dedicamos a hacer el punto estrella y a escribir el readme. (Otra vez investigar y leer documentación)
Es muy complicado separar finamente quién hizo qué porque dos de los integrantes viven juntos y nos pasabamos información vía chats, entonces capaz hasta ideas y pequeñas partes de código eran de Pepito pero las redactaba y pusheaba Pepito1.
Más allá de eso, fue poca la autoría que tenemos respecto al código, ya que hay documentación en grandes cantidades y de muy buena calidad...
![Image](https://imgs.xkcd.com/comics/python.png)
Entonces fue comprender ¿para qué? y después usar código de documentación, o de posteos adaptándolo a nuestras necesidades.
Llevamos casi 2 años trabajando en conjunto por lo que no nos preocupa quién hace qué parte sino que el que puede mete mano donde puede y así vamos avanzando, lo que sí nos importa es comprender lo que se hace, por eso también llevamos (casi siempre) los links de la documentación o ej que vimos que nos ayudaron a armar el código.

### Modularización ###

Dividimos en módulos la conexión para que sea más prolija y entendible, dejando por un lado el parser, por otro quien se va a encargar de llamar a las funciones de los comnados y los va a mandar por el buffer.

### Herramientas de Programación ###

- Utilizamos vscode para la elaboracion del codigo
- Telnet para conectarnos al servidor

### Preguntas ###

1. ¿Qué estrategias existen para poder implementar este mismo servidor pero con
capacidad de atender múltiples clientes simultáneamente? Investigue y responda
brevemente qué cambios serían necesario en el diseño del código.

> Para poder implementar el mismo servidor pero con capacidad de atender múltiples clientes simultáneamente lo que hay que hacer es introducir un thread y por cada petición de conexión al socket armar un thread que lo atienda tambien se puede usar.
También se puede hacer con 'asyncro', y forks. 


2. Pruebe ejecutar el servidor en una máquina del laboratorio, mientras utiliza el cliente
desde otra, hacia la ip de la máquina servidor. ¿Qué diferencia hay si se corre el
servidor desde la IP “localhost”, “127.0.0.1” o la ip “0.0.0.0”?

> La dirección ip 0.0.0.0 representan todas direcciones ipv4 del server.
> La ip "localhost" se traduce a la ip "127.0.0.1", siendo ésta la primera del rango de las direcciones de la interfaz de red virtual IPv4.

### Conlcusiones

* Obtuvimos un cliente/servidor que acepta 4 comandos por medio de la programación de sockets y haciendo un multithred para poder aceptar a más de un cliente a la vez. 

### Otros Cambios

* Se podría abrir un puerto y hacer que se pueda conectar al servidor via internet.
* Se podría agregar otros comandos para que haya otras funcionalidades.
* Se podría implementar el multithread con asyncio.

### Bibliografía Complementaria ###

* [Socket](https://docs.python.org/es/3/library/socket.html)
* [Threads](https://docs.python.org/es/3.8/library/threading.html#thread-objects)
* [Multithreaded Server Socket Example](http://net-informations.com/python/net/thread.htm)
* [asyncio](https://docs.python.org/3/library/asyncio.html)
* [Tutorial asyncio](https://www.dabeaz.com/tutorials.html)
* [Seek, Read Files](https://docs.python.org/3/tutorial/inputoutput.html)
* [PEP8, Linting](https://code.visualstudio.com/docs/python/linting)
* [Manejo de Errores](https://docs.python.org/es/3/tutorial/errors.html)
* [Excepciones](https://docs.python.org/es/3.8/library/exceptions.html)

### Integrantes ###

* Juan Kersul
* Andres Doctors
* Juan Yornet 