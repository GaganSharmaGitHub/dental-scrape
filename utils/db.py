from enum import Enum
from io import TextIOWrapper
import json
import logging
import os
from typing import List, Tuple

from pydantic import BaseModel

from utils.utils import dict_filter


class DBTables(str, Enum):
    dental_product_details = "dental_product_details"

    def get_file_path(self):
        return f"ignore/db/{self}.json"


class __DBManager:
    async def initialize(self):
        for table in DBTables:
            directory = os.path.dirname(table.get_file_path())
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            if not os.path.exists(table.get_file_path()):
                with open(table.get_file_path(), "w+") as file:
                    json.dump([], file)

    def __load_file_contents_or_empty(self, file: TextIOWrapper):
        try:
            return json.load(file)
        except Exception as e:
            logging.error(f"error while loading file {e}")
            return []

    async def add_entry(self, table: DBTables, data: BaseModel):
        rows = []
        with open(table.get_file_path(), "r+") as file:
            rows: list = self.__load_file_contents_or_empty(file)
            rows.append(data.model_dump(mode="python"))
            json.dump(rows, file)
        return data

    async def upsert_many_records(
        self, table: DBTables, filter_datas: List[Tuple[dict, dict]]
    ):
        counts = {
            "insert": 0,
            "updates": 0,
        }
        with open(table.get_file_path(), "w+") as file:
            rows: List[dict] = self.__load_file_contents_or_empty(file)

            for filter, data in filter_datas:
                is_update = False
                for row in rows:
                    if dict_filter(filter=filter, data=row):
                        is_update = True
                        row.update(data)
                        counts["updates"] = counts["updates"] + 1
                        break
                if not is_update:
                    to_insert = filter.copy()
                    to_insert.update(data)
                    rows.append(to_insert)
                    counts["insert"] = counts["insert"] + 1
            json.dump(rows, file)
        return counts

    async def terminate(self):
        print("DB Connection terminated.")


database = __DBManager()
