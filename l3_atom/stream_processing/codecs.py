from schema_registry.client import SchemaRegistryClient, Auth
from schema_registry.serializers.faust import FaustSerializer
from faust.serializers import codecs
from l3_atom.helpers.read_config import get_kafka_config
from l3_atom.stream_processing.records import record_mapping


def initialise():
    """Initialises the serialisation codecs for Faust"""
    config = get_kafka_config()

    client = SchemaRegistryClient(url=config['SCHEMA_REGISTRY_URL'], auth=Auth(
        username=config['SCHEMA_REGISTRY_API_KEY'], password=config['SCHEMA_REGISTRY_API_SECRET']))

    schemas = {
        feed: client.get_schema(feed).schema for feed in record_mapping.keys()
    }

    for feed, schema in schemas.items():
        codecs.register(
            feed, FaustSerializer(
                schema=schema,
                schema_registry_client=client,
                schema_subject=feed
            )
        )
