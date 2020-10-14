from flask import Flask, request, abort
from datetime import datetime
from az_storage import upload_xml, to_archive_name, read_blob_meta
from util import retry
import tests

app = Flask(__name__)

@app.route("/")
def root():
    return "Price Feed\n Usage: /feed"

@app.route("/feed", methods=['GET'])
def feed():
    try:    
        upload_name, archive_name, meta, status = tests.test_price_feed()
    except Exception as ex:
        abort(400, ex)
        
    return f"upload_name={upload_name} \n archive_name={archive_name} \n meta={meta} \n status={status}"

