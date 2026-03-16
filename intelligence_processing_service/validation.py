from datetime import datetime
from logging import Logger

from shared.mongo_client import MongoConnector
from model import IntelMessage


class MessageValidator:
    def __init__(self, mongo_client: MongoConnector, logger: Logger):
        self.mongo_client = mongo_client
        self.logger = logger

    def target_exists(self, target_id) -> bool:
        target = self.mongo_client.get_target(target_id)
        return target is not None

    def target_destroyed(self, target_id):
        if self.target_exists(target_id):
            target = self.mongo_client.get_target(target_id)
            return target.get("status", "") == "destroyed"
        else:
            return False

    def check_timestamp_validation(self, target_id, timestamp: datetime):
        if self.target_exists(target_id):
            target = self.mongo_client.get_target(target_id)
            return target.get("last_update", timestamp) <= timestamp
        else:
            return True

    def validate(self, intel_message: dict):
        self.logger.info("the validation started...")
        try:
            message = IntelMessage(**intel_message).dict()
        except Exception as e:
            raise ValueError(f"not valid message: {str(e)}")

        target_id = message['entity_id']

        if self.target_destroyed(target_id):
            raise ValueError(f"the target with id: {target_id} is destroyed already")

