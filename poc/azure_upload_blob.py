import os, random
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

#config
conn_str = os.environ['PLT_AZ_STORAGE_CONN_STRING']
container_name = os.environ['PLT_AZ_CONTAINER_NAME']
templ_name = './file_templ.txt'
placeholder = 'xxx'
uniq_part = str(random.randint(1000, 9999))
blob_name = f'file_{uniq_part}.txt'

with open(templ_name, "r") as f:
    content = f.read().replace(placeholder, uniq_part) 

assert content
blobservice_client = BlobServiceClient.from_connection_string(conn_str)
blobservice_client.create_container(container_name)
blob_client = blobservice_client.get_blob_client(container=container_name, blob=blob_name)
blob_client.upload_blob(content)
