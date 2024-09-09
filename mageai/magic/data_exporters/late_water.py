if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

import pandas as pd
from elasticsearch import Elasticsearch


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    es_client = Elasticsearch('http://127.0.0.1:9200', request_timeout=500) 

    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "description": {"type": "text"},
                "category": {"type": "text"},
                "description_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
            }
        }
    }

    index_name = "categories"

    if not es_client.indices.exists(index=index_name):
        print('creating index')
        es_client.indices.create(index=index_name, body=index_settings)
        print('index created')
        print(es_client.indices.get_settings(index=index_name))
    

    docs = data.to_dict('records')

    for doc in docs:
        try:
            es_client.index(index=index_name, document=doc)
            doc['indexed'] = True
        except Exception as e:
            doc['indexed'] = True

    new_data = pd.DataFrame(docs)

    return new_data


