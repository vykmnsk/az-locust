import os, random, uuid, time
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
from azure.cosmosdb.table.tableservice import TableService
from util import retry


load_dotenv(find_dotenv())

az_conn_in = os.environ['PLT_AZ_STORAGE_CONN_STRING']
blob_service = BlobServiceClient.from_connection_string(az_conn_in)

az_conn_out = os.environ['PLT_AZ_STORAGE_OUT_CONN_STRING']
table_service = TableService(connection_string=az_conn_out)


def upload_xml(folderName: str, countryCode: str, time: datetime) -> str:
    azContainer = 'pricing'
    template = f'data/{folderName}.templ.xml'
    markerTBatchId = '[TransmissionBatchID]'
    markerExtractDateTime = '[ExtractDateTime]'
    tBatchId = time.strftime('%Y%m%d')
    extractDateTime=datetime.now().isoformat()
    fname = f'{folderName}/{countryCode}_{uuid.uuid4()}.xml'

    with open(template, "r") as f:
        content = f.read() \
            .replace(markerTBatchId, tBatchId) \
            .replace(markerExtractDateTime, extractDateTime)
    assert content

    bClient = blob_service.get_blob_client(container=azContainer, blob=fname)
    bClient.upload_blob(content)

    return(fname)

def to_archive_name(uploade_name: str, folder: str, country: str, upload_time: datetime) -> str:
    prefix = f'{folder}/{country}'
    tstamp = upload_time.strftime('%Y%m%d%H')
    assert uploade_name.startswith(prefix)
    return uploade_name.replace(prefix, f'{prefix}_{tstamp}')

def read_blob_meta(bname: str) -> dict:
    azContainer = 'pricing-archive'
    bClient = blob_service.get_blob_client(container=azContainer, blob=bname)
    properties = bClient.get_blob_properties()
    return properties.metadata

def fetch_table_value(table: str, column_key: str, column_select: str, row_key: str) -> str:
    result = table_service.query_entities(
        table, filter=f"{column_key} eq '{row_key}'", select=column_select)
    assert result, 'No result object'
    rows = result.items
    assert len(rows) == 1, f'No results for row_key={row_key}'
    value = rows[0][column_select]
    return value