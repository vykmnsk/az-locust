from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import os, time

conn_str = os.environ['PLT_AZ_STORAGE_CONN_STRING']
table_service = TableService(connection_string=conn_str)

table_name = 'pricetable'

# create and populate
table_service.create_table(table_name)
time.sleep(20)

def insert_price(partition, key, type, name, value):
    p = Entity()
    p.PartitionKey = partition
    p.RowKey = str(key)
    p.type = type
    p.name = name 
    p.value = value
    table_service.insert_or_replace_entity(table_name, p) 

seq = 0
seq += 1
insert_price('melb', seq, 'retail', 'Hammer', '5.99')
seq += 1
insert_price('melb', seq, 'retail', 'Screwdriver', '3.95')
seq += 1
insert_price('melb', seq, 'retail', 'Shovel', '21.50')
seq += 1
insert_price('melb', seq, 'team', 'Hammer', '0.99')


# query
rows = table_service.query_entities(
    table_name, filter="type eq 'retail'", select="name, value")
for r in rows:
    print(r)

table_service.delete_table(table_name)
