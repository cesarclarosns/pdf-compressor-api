# API para procesar documentos

Por el momento esta API solo sirve para comprimir archivos PDF.

## Requisitos

Tener Docker instalado.

## ¿Cómo implementar esta API?

Para correr esta API se hace uso del comando "docker-compose", el cual sirve para definir y ejecutar aplicaciones Docker de varios contenedores apartir de un archivo ".yml" que contendrá toda la configuración.

En este caso se hará uso del archivo "docker-compose.prod.yml".

Ejecutar este comando para iniciar la API en modo producción en segundo plano usando el flag "-d". La API podrá ser accesada en el puerto 5000 del host como se indica en el archivo "docker-compose.prod.yml".

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Para detener contenedores y eliminar contenedores, redes, volúmenes e imágenes creados por el anterior comando ejecutar:

```bash
docker-compose -f docker-compose.prod.yml down
```

Puedes acceder a la documentación de esta API en "/docs".

## ¿Cómo continuar con el desarrollo de esta API usando VSCode dentro de este contenedor?

## Aprender más sobre Docker

https://www.youtube.com/watch?v=3c-iBn73dDE&ab_channel=TechWorldwithNana
