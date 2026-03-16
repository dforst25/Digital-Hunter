from logging import Logger
from pymongo import MongoClient
import os
from shared.target_bank import TARGET_BANK


class MongoConnector:
    def __init__(self, mongo_uri, coll_name, logger: Logger):
        self.logger = logger
        self.db_name = os.getenv("DATABASE_NAME", "targets_db")
        self.mongo_uri = mongo_uri
        self.coll_name = coll_name
        self.client = None
        try:
            self.logger.info("connecting to mongo...")
            self.client = MongoClient(self.mongo_uri)
            self.client.admin.command('ping')
        except Exception as e:
            self.logger.exception(f"Server not available: {e}")

    def init_db(self):
        collection = self.client[self.db_name]["target_bank"]
        self.logger.info("Initialize the db")
        try:
            collection.insert_many(TARGET_BANK)
        except Exception as e:
            self.logger.exception(f"Failed initialize the db: {e}")

    def get_db(self):
        if self.db_name not in self.client.list_database_names():
            self.logger.warning(f"the database '{self.db_name}' doesn't exist, creating a new empty database")
            self.init_db()
        return self.client[self.db_name]

    def get_bank_coll(self):
        return self.get_db()["target_bank"]

    def get_coll(self):
        db = self.get_db()
        if self.coll_name not in db.list_collection_names():
            self.logger.warning(f"the collection '{self.coll_name}' doesn't exist, creating a new collection")
        return self.get_db()[self.coll_name]

    def get_target(self, entity_id):
        query = {"entity_id": entity_id}
        return self.get_bank_coll().find_one(query, {"_id": 0})

    def insert_target_to_the_target_bank(self, target: dict):
        collection = self.get_bank_coll()
        self.logger.info("Insert a new target to the bank")
        target["_id"] = target.get("entity_id")
        collection.insert_one(target)

    def insert_last_update(self, target_id, timestamp):
        collection = self.get_bank_coll()
        collection.update_one(
            {"entity_id": target_id},
            {"$set": {"last_update": timestamp}}
        )

    def insert_move_distance(self, target_id, distance):
        collection = self.get_bank_coll()
        collection.update_one(
            {"entity_id": target_id},
            {"$set": {"move_distance": distance}}
        )

    def insert_to_curr_coll(self, doc):
        collection = self.get_coll()
        self.logger.info("Insert a new message to the intel collection")
        collection.insert_one(doc)

    def insert_is_attacked(self, target_id):
        collection = self.get_bank_coll()
        collection.update_one(
            {"entity_id": target_id},
            {"$set": {"is_attacked": True}}
        )
