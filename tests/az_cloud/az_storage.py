import os, requests
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableClient


load_dotenv(find_dotenv())
AZ_CONN_IN_STR = os.environ['PLT_AZ_STORAGE_CONN_STRING']
AZ_CONN_OUT_STR = os.environ['PLT_AZ_STORAGE_OUT_CONN_STRING']
AZ_CONN_OUT_TABLE = os.environ['PLT_AZ_STORAGE_OUT_CONN_TABLE']

CONN_POOL_SIZE=int(os.environ['PLT_CONN_POOL_SIZE'])


sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_maxsize=CONN_POOL_SIZE)
sess.mount('https://', adapter)

blob_service = BlobServiceClient.from_connection_string(AZ_CONN_IN_STR, session=sess)
table_service = TableClient.from_connection_string(conn_str=AZ_CONN_OUT_STR, table_name=AZ_CONN_OUT_TABLE, session=sess)


def upload_file(fname: str, content: str):
    az_container = 'pricing'
    with blob_service.get_blob_client(container=az_container, blob=fname) as client:
        client.upload_blob(content)

def read_blob_meta(bname: str) -> dict:
    props = None
    az_container = 'pricing-archive'
    with blob_service.get_blob_client(container=az_container, blob=bname) as client:
        props = client.get_blob_properties()
    return props.metadata


def fetch_table_value(column_key: str, column_select: str, row_key: str) -> str:
    result = table_service.query_entities(
        query_filter=f"{column_key} eq '{row_key}'",
        select=column_select)
    assert result, 'No result object'
    rows = [row for row in result]
    assert len(rows) == 1, f'No results for row_key={row_key}'
    value = rows[0][column_select]
    return value
