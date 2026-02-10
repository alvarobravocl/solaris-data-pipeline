# Usamos una imagen base oficial de Python ligera
FROM python:3.9-slim

# Evita que Python genere archivos .pyc y fuerza la salida por consola (bueno para logs de Docker)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Primero copiamos los requirements para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código fuente y carpetas necesarias
COPY src/ ./src/
# (Nota: Las carpetas 'data' se montan como volumen en el docker-compose, no hace falta copiarlas aquí)

# Comando por defecto (mantiene el contenedor vivo para depuración, tal como definimos en el compose)
CMD ["tail", "-f", "/dev/null"]