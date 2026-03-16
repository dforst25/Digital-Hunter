import json
from logging import Logger

from confluent_kafka import Consumer


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, topic_name: str, group_id: str, logger: Logger):
        self.bootstrap_servers = bootstrap_servers
        self.topic_name = topic_name
        self.group_id = group_id
        self.logger = logger
        self.consumer = None

    def start_callback(self):
        if self.consumer is None:
            consumer_config = {
                "bootstrap.servers": self.bootstrap_servers,
                "group.id": self.group_id,
                "auto.offset.reset": "earliest"
            }

            self.consumer = Consumer(consumer_config)
        self.consumer.subscribe([self.topic_name])
        self.logger.info("Listening for kafka to catch messages...")
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                self.logger.error(f"Error: {msg.error()}")
                continue
            value = msg.value().decode("utf-8")
            try:
                value_json = json.loads(value)
            except Exception:
                return value
            self.logger.info(f"Got message:\ntarget_id: {value_json.get('entity_id', 'no id')}")
            return value_json

