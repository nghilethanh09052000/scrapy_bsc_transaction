# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
import pyarrow.parquet as pq
from google.cloud import storage
from io import BytesIO
import uuid
from datetime import datetime


class UploadToCloudStoragePipeline:
    def process_item(
            self,
            item,
            spider
        ):
        
        snapshot_date = datetime.now().strftime("%Y-%m-%d")
        df = pd.DataFrame([item])
        # parquet_data = BytesIO()
        parquet_data = df.to_parquet(engine='pyarrow')
        
        client = storage.Client.from_service_account_json(
            'data-platform-387707-testing.json'
        )
        
        bucket = client.bucket('atherlabs-test')
        blob_name = f'raw_bscscan_transaction/snapshot_date={snapshot_date}/{uuid.uuid4()}.parquet'

        blob = bucket.blob(blob_name=blob_name)
        blob.upload_from_string(parquet_data)
        return item
