from elasticsearch import Elasticsearch
import json
import os
from dotenv import load_dotenv

load_dotenv()

es_host = os.getenv('ES_host')
es_usr = os.getenv('ES_usr')
es_psw = os.getenv('ES_psw')
es_ssl = os.getenv('ES_ssl')
es_cert = os.getenv('ES_cert')


es = Elasticsearch(
    f"https://{es_usr}:{es_psw}@{es_host}",
    # ssl_assert_fingerprint= es_ssl,
    # basic_auth=(es_usr, es_psw),
    ca_certs = es_cert,
    verify_certs = True
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


def get_mappings():
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