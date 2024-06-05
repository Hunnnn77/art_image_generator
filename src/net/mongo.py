from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

from src.util import Util
from src.variables import Collections


class Mongo:
    def __init__(self, util: Util, db_name: str = "axa") -> None:
        self.util = util
        self.db_name = db_name
        self.client: MongoClient | None = None

    def conn(self):
        if self.client is None:
            uri = self.util.get_envs("MONGO")
            self.client = MongoClient(uri)

    def get_colls(self, coll_name: Collections) -> Collection:
        if self.client is not None:
            database = self.client.get_database(self.db_name)
            coll = database.get_collection(coll_name.value)
            return coll
        else:
            raise Exception("client is none")

    def insert_images(self, collections: Collections, data: list[dict[str, Any]]):
        coll = self.get_colls(collections)
        match collections:
            case Collections.Gallery:
                coll.insert_many(data)
            case _:
                raise NotImplementedError()

    def insert_many_links(self, collections: Collections, data: list[dict[str, Any]]):
        coll = self.get_colls(collections)
        coll.insert_many(data)
