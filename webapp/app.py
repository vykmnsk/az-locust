from flask import Flask, request, abort
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
import os


app = Flask(__name__)

@app.route("/feed/", methods=['GET'])
def feed():
    uniq = request.args.get('uniq')
    if not uniq:
        abort(400)    
        
    blob_name = f'file_{uniq}.txt'    
    content = f"test content {uniq}"
        
    conn_str = os.environ['PLT_AZ_STORAGE_CONN_STRING']
    container_name = os.environ['PLT_AZ_CONTAINER_NAME']
   
        
    blobservice_client = BlobServiceClient.from_connection_string(conn_str)
    try:
        blobservice_client.create_container(container_name)
    except ResourceExistsError:
        pass
        
    blob_client = blobservice_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(content)
        
    return f"Fed {uniq}."

