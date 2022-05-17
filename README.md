# API para procesar documentos

Por el momento esta API desarrollada con Quart framework solo sirve para comprimir archivos PDF en base64.

## Requisitos

Tener Docker instalado (Docker Engine).

## ¿Cómo llevar a producción esta API?

Esta API se puede correr de dos formas actualmente:

En la primer forma solo se necesita correr el siguiente comando. El cual descargará la imagen del contenedor (la aplicación) desde el repositorio de imágenes de contenedores Docker Hub, mapeará el puerto "5000" del host con el puerto "5000" del contenedor (-p "5000:5000") y mantendrá el contenedor corriendo en segundo plano con el flag "-d" :

```docker
docker run -p "5000:5000" -d cesarclarosns/pdf-compressor-api:0.1
```

En la segunda forma se hace uso de "docker-compose" el cual sirve para definir y ejecutar aplicaciones Docker de varios contenedores apartir de un archivo ".yml" que contendrá toda la configuración. En este caso se usará el archivo "docker-compose.prod.yml", la configuración que está en este archivo es la misma que en el comando con `docker run`.

```docker
docker-compose -f docker-compose.prod.yml up -d
```

Si ejecutas el siguiente comando deberías de poder ver el contenedor corriendo.

```docker
docker ps
```

En este caso se observa que el puerto 5000 en el contenedor (5000/tcp) está siendo mapeado con el puerto 5000 del host (0.0.0.0:5000):

![docker-ps](./static/docker-ps.png)

Para detener contenedores y eliminar contenedores, redes, volúmenes e imágenes creados por el anterior comando ejecutar:

```bash
docker-compose -f docker-compose.prod.yml down
```

Puedes acceder a la documentación de esta API en la ruta "/docs".
![Docs](./static/docs.png)

## ¿Cómo continuar con el desarrollo de esta API usando VSCode dentro de este contenedor?

Para esto se debe tener instalado VSCode y la extensión para VSCode "Remote - Containers".

En este caso se iniciará el contenedor usando el archivo "docker-compose.dev.yml":

```bash
docker-compose -f docker-compose.dev.yml up -d
```

El siguiente paso es adjuntar VSCode al contenedor remoto. Para esto se abre la ventana de comandos de VSCode (CTRL + SHIFT + P en Windows), se escribe "attach to running container" y se selecciona la opción que nos da la extensión "Remote-Containers".

![Attach to running container](./static/attach-to-running-container.png)

Y se selecciona el contenedor.
![Select container](./static/select-container.png)

Por último se selecciona el directorio de trabajo, el cual es "/usr/src" en el contenedor:
![Select workir](./static/select-workdir.png)

Y listo, ya se tendrá el mismo entorno de producción para desarrollo con las paqueterías cargadas. Debido al binding que se hace, los cambios que realices en este entorno se verán reflejados en el directorio local donde tienes el repositorio.
![Dev env](./static/dev-env.png)

## Consideraciones al construir la imágen del contenedor que se usará en producción para subirla a un repositorio

No incluir los archivos que no se necesiten para correr la aplicación haciendo uso del archivo ".dockerignore".

En este caso se está usando `pipenv` para manejar las dependencias.

## Aprender más sobre Docker

https://www.youtube.com/watch?v=3c-iBn73dDE&ab_channel=TechWorldwithNana
