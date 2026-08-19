"""
Módulo de conexión y operaciones con AWS S3.

Provee una clase S3Client que encapsula las operaciones comunes:
- Conexión autenticada al bucket
- Subida de archivos
- Descarga de archivos
- Listado de objetos
- Eliminación de objetos
"""

import os
import logging
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger(__name__)


class S3Client:
    """Cliente para interactuar con un bucket de AWS S3."""

    def __init__(
        self,
        bucket_name: str | None = None,
        region: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        endpoint_url: str | None = None,
    ):
        """
        Inicializa el cliente S3.

        Los parámetros se resuelven en este orden de prioridad:
        1. Argumentos explícitos
        2. Variables de entorno (AWS_BUCKET_NAME, AWS_REGION, etc.)
        3. Credenciales del perfil AWS configurado (~/.aws/credentials)

        Parameters
        ----------
        bucket_name : str, optional
            Nombre del bucket. Por defecto usa AWS_BUCKET_NAME del entorno.
        region : str, optional
            Región AWS. Por defecto usa AWS_REGION del entorno.
        aws_access_key_id : str, optional
            Access key ID. Por defecto usa AWS_ACCESS_KEY_ID del entorno.
        aws_secret_access_key : str, optional
            Secret access key. Por defecto usa AWS_SECRET_ACCESS_KEY del entorno.
        endpoint_url : str, optional
            URL personalizada del endpoint (útil para LocalStack o MinIO).
        """
        self.bucket_name = bucket_name or os.getenv("AWS_BUCKET_NAME")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        session_kwargs = {}
        access_key = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")

        if access_key and secret_key:
            session_kwargs["aws_access_key_id"] = access_key
            session_kwargs["aws_secret_access_key"] = secret_key

        session = boto3.Session(region_name=self.region, **session_kwargs)

        client_kwargs = {}
        self._endpoint_url = endpoint_url or os.getenv("AWS_ENDPOINT_URL")
        if self._endpoint_url:
            client_kwargs["endpoint_url"] = self._endpoint_url

        self.s3 = session.client("s3", **client_kwargs)
        self.resource = session.resource("s3", **client_kwargs)

        logger.info(
            "S3Client inicializado — bucket=%s, region=%s",
            self.bucket_name,
            self.region,
        )

    # ------------------------------------------------------------------
    # Operaciones de archivos
    # ------------------------------------------------------------------

    def upload_file(
        self,
        local_path: str | Path,
        s3_key: str | None = None,
        extra_args: dict | None = None,
    ) -> str:
        """
        Sube un archivo local al bucket S3.

        Parameters
        ----------
        local_path : str | Path
            Ruta del archivo local a subir.
        s3_key : str, optional
            Clave (ruta) destino en S3. Si no se indica, se usa el nombre del archivo.
        extra_args : dict, optional
            Argumentos extra para la subida (e.g. ContentType, ACL).

        Returns
        -------
        str
            La clave S3 del objeto subido.

        Raises
        ------
        FileNotFoundError
            Si el archivo local no existe.
        ClientError
            Si ocurre un error en la API de S3.
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {local_path}")

        if s3_key is None:
            s3_key = local_path.name

        try:
            self.s3.upload_file(
                str(local_path),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args,
            )
            logger.info("Archivo subido: %s -> s3://%s/%s", local_path, self.bucket_name, s3_key)
            return s3_key
        except ClientError as e:
            logger.error("Error al subir archivo: %s", e)
            raise

    def download_file(self, s3_key: str, local_path: str | Path) -> Path:
        """
        Descarga un archivo desde S3 al sistema local.

        Parameters
        ----------
        s3_key : str
            Clave del objeto en S3.
        local_path : str | Path
            Ruta local donde guardar el archivo.

        Returns
        -------
        Path
            La ruta local del archivo descargado.

        Raises
        ------
        ClientError
            Si el objeto no existe o hay un error de permisos.
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.s3.download_file(self.bucket_name, s3_key, str(local_path))
            logger.info(
                "Archivo descargado: s3://%s/%s -> %s",
                self.bucket_name,
                s3_key,
                local_path,
            )
            return local_path
        except ClientError as e:
            logger.error("Error al descargar archivo: %s", e)
            raise

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[dict]:
        """
        Lista objetos en el bucket con un prefijo dado.

        Parameters
        ----------
        prefix : str
            Prefijo para filtrar objetos (simula carpetas).
        max_keys : int
            Número máximo de objetos a retornar.

        Returns
        -------
        list[dict]
            Lista de diccionarios con 'Key', 'Size', 'LastModified' de cada objeto.
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys,
            )
            objects = response.get("Contents", [])
            logger.info(
                "Listados %d objetos con prefijo '%s' en %s",
                len(objects),
                prefix,
                self.bucket_name,
            )
            return [
                {
                    "Key": obj["Key"],
                    "Size": obj["Size"],
                    "LastModified": obj["LastModified"],
                }
                for obj in objects
            ]
        except ClientError as e:
            logger.error("Error al listar objetos: %s", e)
            raise

    def delete_object(self, s3_key: str) -> None:
        """
        Elimina un objeto del bucket.

        Parameters
        ----------
        s3_key : str
            Clave del objeto a eliminar.
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info("Objeto eliminado: s3://%s/%s", self.bucket_name, s3_key)
        except ClientError as e:
            logger.error("Error al eliminar objeto: %s", e)
            raise

    def object_exists(self, s3_key: str) -> bool:
        """
        Verifica si un objeto existe en el bucket.

        Parameters
        ----------
        s3_key : str
            Clave del objeto a verificar.

        Returns
        -------
        bool
            True si el objeto existe, False en caso contrario.
        """
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Genera una URL pre-firmada para acceso temporal a un objeto.

        Parameters
        ----------
        s3_key : str
            Clave del objeto.
        expiration : int
            Tiempo de expiración en segundos (por defecto 1 hora).

        Returns
        -------
        str
            URL pre-firmada.
        """
        try:
            url = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error("Error generando URL pre-firmada: %s", e)
            raise
