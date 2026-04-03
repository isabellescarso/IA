from minio import Minio
from minio.error import S3Error

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

buckets_para_remover = ["bronze", "silver", "gold"]

for bucket_name in buckets_para_remover:
    try:
        if client.bucket_exists(bucket_name):
            objects = client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                client.remove_object(bucket_name, obj.object_name)
            
            client.remove_bucket(bucket_name)
    except S3Error as e:
        print(f"Erro ao acessar {bucket_name}: {e}")