import pysolr
import os

solr_url = os.environ.get('SOLR_URL')


def handler(data):
    try:
        solr = pysolr.Solr(f"{solr_url}/pipeline",
                           always_commit=True, timeout=10)
        solr.add([data])

        solr.commit()
    except Exception as e:
        print(str(e))
