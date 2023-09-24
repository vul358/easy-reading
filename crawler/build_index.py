from elasticsearch import Elasticsearch
import json
from django.conf import settings

es = Elasticsearch(
    f"https://{settings.es_host}",
    ssl_assert_fingerprint= settings.es_ssl,
    basic_auth=(settings.es_usr, settings.es_psw)
    )


def create_index(es):
    body = dict()
    body['settings'] = get_setting()
    body['mappings'] = get_mappings()
    print(json.dumps(body)) #可以用json.dumps輸出來看格式有沒有包錯
    es.indices.create(index='sto_novels_info', body=body)


def get_setting():
    settings = {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }
    }
    return settings


def mappings():
    mappings = {
        "properties": {
            "title": {
                "type": "text"
            },
            "author": {
                "type": "keyword"
            },
            "outline": {
                "type": "text"
            },
            "category": {
                "type": "text"
            },
            "tags": {
                "type": "text"
            },
            "year":{
                "type": "integer"
            },
            "url":{
                "type": "keyword"
            },
            "website":{
                "type": "keyword"
            },
            "comment":{
                "type": "integer"
            },
            "size":{
                "type": "integer"
            },
            "date":{
                "type": "date"
            }
        }
    }
    return mappings    


if __name__ == "__main__":
    create_index(es)
    # result = es.indices.get(index='sto_novels_info') #index指定要get哪個index的資訊
    # tryexist = es.indices.exists(index='sto_novels_info')
    # print(tryexist)