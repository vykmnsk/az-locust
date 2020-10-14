from datetime import datetime
from util import retry
from az_storage import upload_xml, to_archive_name, read_blob_meta, fetch_table_value

def test_price_feed():
    folder = 'ProductMaster'
    country = 'AU'
    upload_time = datetime.today()
    upload_name = upload_xml(folder, country, upload_time)
    print(f"upload_name={upload_name}")
    
    archive_name = to_archive_name(upload_name, folder, country, upload_time)
    print(f"archive_name={archive_name}")
    
    meta = retry(15, 2, read_blob_meta, archive_name)
    print(f"meta={meta}")
    batchid = meta['batchid']
    
    def find_status_completed_record(key_value: str) -> None:
        table = 'MyTaskHubInstances'
        column_key = 'PartitionKey'
        column_select = 'RuntimeStatus'
        status = fetch_table_value(table, column_key, column_select, key_value)
        assert status.upper() == 'COMPLETED', f'status={status} for key={key_value} '
        return status
        
    final_status = retry(50, 6, find_status_completed_record, f'{folder}_{batchid}')
    print(f"final status={final_status}")
    
    return (upload_name, archive_name, meta, final_status)
    
if __name__ == "__main__":
    test_price_feed()