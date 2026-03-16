from logging import Logger
from validation import MessageValidator, MongoConnector
from shared.haversine import haversine_km

class Processor:
    def __init__(self, logger: Logger, validator: MessageValidator, mongo_client: MongoConnector):
        self.logger = logger
        self.validator = validator
        self.mongo_client = mongo_client

    def intersect_data(self, intel_message: dict):
        target_id = intel_message["entity_id"]
        if not self.validator.target_exists(target_id):
            intel_message["priority_level"] = 99
        timestamp = intel_message.get("timestamp")
        if timestamp:
            self.mongo_client.insert_last_update(target_id, timestamp)

    def insert_movement_distance(self, intel_message: dict):
        target_id = intel_message["entity_id"]
        target = self.mongo_client.get_target(target_id)
        if target is not None:
            lon1 = intel_message.get("reported_lon")
            lat1 = intel_message.get("reported_lat")
            lon2 = target["lon"]
            lat2 = target["lat"]
            distance = haversine_km(lat1, lon1, lat2, lon2)
        else:
            distance = 0.0
        self.mongo_client.insert_move_distance(target_id, distance)
