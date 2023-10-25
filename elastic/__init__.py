from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.client import XPackClient
import os
import uuid

elastic_url = os.environ.get('ELASTIC_URL')


def handler(data):
    index_name = "sapujagadv2_scheduler"
    # document_type = "scheduler"
    uuid4 = uuid.uuid4()
    document_id = uuid4

    try:
        es = Elasticsearch(hosts=elastic_url)
        es.index(index=index_name, document=data, id=document_id)
    except Exception as e:
        print(str(e))
