from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
# from .models import TestNovel, NovelsInfo
from elasticsearch_dsl.connections import connections 

connections.create_connection() 



@registry.register_document
class TestDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'test_novel'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 1}

    class Django:
        model = TestNovel # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'title',
            'author',
            'outline',
        ]


@registry.register_document
class NovelsDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'sto_novels_info'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 1}

    class Django:
        model = NovelsInfo # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'title',
            'author',
            'outline',
            'category',
            'tags',
            'year',
            'url',
            'website',
            'comment',
            'size',
            'date',
        ]