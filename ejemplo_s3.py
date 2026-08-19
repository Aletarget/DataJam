"""
Ejemplo de uso del cliente S3 para el proyecto DataJam.

Antes de ejecutar:
1. Copia .env.example a .env y llena tus credenciales:
   cp .env.example .env

2. Instala dependencias:
   pip install -r requirements.txt

3. Ejecuta este script:
   python ejemplo_s3.py
"""

import logging
from s3_client import S3Client

# Configurar logging para ver las operaciones
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def main():
    # Inicializar cliente (usa credenciales del .env automáticamente)
    client = S3Client()

    # ------------------------------------------------------------------
    # 1. Listar objetos en el bucket
    # ------------------------------------------------------------------
    print("\n--- Objetos en el bucket ---")
    objetos = client.list_objects(prefix="", max_keys=20)
    for obj in objetos:
        print(f"  {obj['Key']}  ({obj['Size']} bytes)")

    if not objetos:
        print("  (bucket vacío)")

    # ------------------------------------------------------------------
    # 2. Subir un archivo
    # ------------------------------------------------------------------
    print("\n--- Subiendo archivo ---")
    archivo_local = "resultados_analisis/CONCLUSIONES_FINALES.txt"
    s3_key = client.upload_file(
        local_path=archivo_local,
        s3_key="datajam/resultados/CONCLUSIONES_FINALES.txt",
    )
    print(f"  Subido como: {s3_key}")

    # ------------------------------------------------------------------
    # 3. Verificar que existe
    # ------------------------------------------------------------------
    print("\n--- Verificando existencia ---")
    existe = client.object_exists(s3_key)
    print(f"  ¿Existe '{s3_key}'? {existe}")

    # ------------------------------------------------------------------
    # 4. Generar URL pre-firmada (acceso temporal sin credenciales)
    # ------------------------------------------------------------------
    print("\n--- URL pre-firmada (válida 1 hora) ---")
    url = client.generate_presigned_url(s3_key, expiration=3600)
    print(f"  {url}")

    # ------------------------------------------------------------------
    # 5. Descargar archivo
    # ------------------------------------------------------------------
    print("\n--- Descargando archivo ---")
    destino = client.download_file(s3_key, local_path="outputs/descargado.txt")
    print(f"  Guardado en: {destino}")

    # ------------------------------------------------------------------
    # 6. Eliminar objeto (descomentar si quieres probar)
    # ------------------------------------------------------------------
    # print("\n--- Eliminando objeto ---")
    # client.delete_object(s3_key)
    # print(f"  Eliminado: {s3_key}")


if __name__ == "__main__":
    main()
