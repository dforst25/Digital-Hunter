import logging
import os

from shared.mongo_client import MongoConnector
from shared.kafka.consumer import KafkaConsumer
from shared.kafka.producer import KafkaProducer
from validation import MessageValidator
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("intel-service")


def main():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    coll_name = os.getenv("COLL_NAME", "damage")
    mongo_client = MongoConnector(mongo_uri, coll_name, logger)
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = os.getenv("TOPIC_NAME", "damage")
    error_topic_name = os.getenv("ERROR_TOPIC_NAME", "damage_signals_dlq")
    group_id = os.getenv("GROUP_ID", "damage-service")
    consumer = KafkaConsumer(bootstrap_servers, topic_name, group_id, logger)
    producer = KafkaProducer(logger, bootstrap_servers, error_topic_name)
    validator = MessageValidator(mongo_client, logger)
    while True:
        message = consumer.start_callback()
        try:
            validator.validate(message)
        except ValueError as e:
            print(message)
            error_message = {'message': message, 'reason': str(e)}
            producer.publish(error_message)
            continue
        mongo_client.insert_status(message.get("entity_id"), message.get("result"))
        mongo_client.insert_to_curr_coll(message)


if __name__ == "__main__":
    main()
