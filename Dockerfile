# Usa una imagen base de Python
FROM python:3.9

# Crear el directorio donde se alojará la aplicación
RUN mkdir /remembermed

# Establece el directorio de trabajo en /remembermed
WORKDIR /remembermed

# Añadir todo el contenido del proyecto al contenedor
ADD . /remembermed

# Instala las dependencias de la aplicación
RUN pip install -r requirements.txt

# Instala ngrok desde el repositorio oficial
RUN apt-get update && apt-get install -y wget curl gnupg
RUN curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
RUN echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list
RUN apt-get update && apt-get install -y ngrok

# Expone el puerto 5000 para la aplicación Flask
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "/remembermed/app.py"]
