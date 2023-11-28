from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.client import XPackClient
import os
import uuid

elastic_url = os.environ.get('ELASTIC_URL', 'http://103.127.97.245:9200')
print(elastic_url)

def handler(data):
    index_name = "sapujagadv2_scheduler"
    # document_type = "scheduler"
    uuid4 = uuid.uuid4()
    document_id = uuid4

    try:
        es = Elasticsearch(hosts=elastic_url)
        es.index(index=index_name, document=data, id=document_id)
        print("Success insert data to elastic")
    except Exception as e:
        print("Error insert data to elastic")
        print(str(e))

# handler({
#     "id": "1",
#     "name": "test",
#     "status": "running",
#     "lastRun": "2020-09-29T15:00:00.000Z",
#     "nextRun": "2020-09-29T15:00:00.000Z",
#     "cronExpression": "0 0 0 * * *",
#     "type": "notebook",
#     "notebook": "test.ipynb",
#     "notebookParams": {
#         "param1": "value1",
#         "param2": "value2"
#     },
# })