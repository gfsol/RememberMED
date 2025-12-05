# Manual de despligue en docker

Este manual te guiará paso a paso para desplegar tu aplicación de Telegram bot en Docker.

# Requisitos Previos

1\. Tener Docker instalado en tu máquina. Si no lo tienes, sigue las instrucciones de instalación en <https://docs.docker.com/get-docker/>.  
2\. Tener el archivo Dockerfile y la estructura de tu aplicación configurados correctamente (lo que se detallará más abajo).

# Paso 1: Crear el Dockerfile

Para poder construir tu imagen de Docker, primero necesitas crear un archivo Dockerfile en la raíz de tu proyecto. El Dockerfile está incluido en este repositorio.

# Paso 2: Crear el archivo requirements.txt

Asegúrate de que las dependencias necesarias están listadas en un archivo requirements.txt en tu proyecto. 
El archivo requirements.txt está incluido en este repositorio.

# Paso 3: Construir la imagen de Docker

Con el archivo Dockerfile y requirements.txt en su lugar, ya puedes construir la imagen de Docker.  
Abre la terminal, navega al directorio donde se encuentra tu aplicación y ejecuta el siguiente comando para construir la imagen:

docker build -t telegram-bot .

# Paso 4: Ejecutar la imagen en un contenedor Docker

Una vez construida la imagen, puedes ejecutar el contenedor con el siguiente comando:

docker run -d -p 2001:5000 --name telegram-bot-container telegram-bot

# Paso 5: Configuración de ngrok en Docker

Para que tu aplicación sea accesible desde el exterior (Telegram), necesitamos configurar ngrok dentro del contenedor. Puedes seguir estos pasos para hacerlo:

1\. Instalar ngrok dentro del contenedor:  
Los comandos para instalar Docker en el contendor, están incluídos en el archivo Dockerfile.

2\. Iniciar ngrok:

Primero, accede al contenedor:

docker exec -it telegram-bot-container /bin/bash

Una vez que tu contenedor esté corriendo, conecta ngrok al puerto 5000 para exponer la aplicación;:

ngrok http 5000

Esto generará una URL pública, como <https://randomstring.ngrok.io>, que podrás usar para configurar el webhook de Telegram.

# Paso 6: Configurar el Webhook de Telegram

Con la URL pública de ngrok, configura el webhook de Telegram con el siguiente comando, reemplazando &lt;URL_NGROK&gt; y &lt;TOKEN_TELEGRAM&gt; por los valores correspondientes:

curl -F "url=https://&lt;URL_NGROK&gt;/telegram?token=&lt;TOKEN_TELEGRAM&gt;" <https://api.telegram.org/bot&lt;TOKEN_TELEGRAM&gt;/setWebhook>  

# Paso 7: Acceder a la Aplicación

La aplicación Flask estará disponible en el contenedor en <http://127.0.0.1:5000/> y será accesible de manera pública mediante la URL de ngrok generada. Solo tienes que abrir esa URL en tu navegador.

# Conclusión

Siguiendo estos pasos, habrás desplegado tu bot de Telegram en un contenedor Docker y lo habrás expuesto a través de ngrok, permitiendo que Telegram se conecte a tu bot sin necesidad de configuraciones adicionales en tu red local.  
Si tienes dudas o problemas, revisa los pasos anteriores para asegurarte de que todo está configurado correctamente.  
¡Buena suerte con tu despliegue!
