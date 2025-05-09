import base64
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las credenciales y el bucket desde el archivo .env
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = "petid001"

def upload_file_to_s3_base64(file_base64: str, s3_key: str) -> str:
    """
    Sube un archivo a un bucket de S3 usando su contenido en Base64.

    :param file_base64: Contenido del archivo en formato Base64.
    :param s3_key: Nombre del archivo en el bucket.
    :return: URL del archivo subido.
    """
    try:
        # Verificar y eliminar el prefijo `data:image/...;base64,` si existe
        if file_base64.startswith("data:image"):
            file_base64 = file_base64.split(",")[1]

        # Limpiar el string Base64
        file_base64 = file_base64.strip().replace("\n", "").replace("\r", "")

        # Validar y corregir el padding del Base64
        missing_padding = len(file_base64) % 4
        if missing_padding:
            file_base64 += "=" * (4 - missing_padding)

        # Decodificar el contenido Base64
        file_bytes = base64.b64decode(file_base64)

        # Crear el cliente de S3
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

        # Subir el archivo al bucket
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes
        )

        # Generar la URL del archivo subido
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return file_url

    except NoCredentialsError:
        raise Exception("Credenciales de AWS no encontradas.")
    except Exception as e:
        raise Exception(f"Error al subir el archivo: {str(e)}")