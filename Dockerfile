# Imagen base de Python 3.9
FROM python:3.9

# Configurar directorio de trabajo
WORKDIR /app

# Copiar los archivos al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Exponer el puerto 8000
EXPOSE 8000

# Comando para ejecutar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
