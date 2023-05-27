import yaml

from typing import List


def load_schema(schema_files: List[str]):
    schema = dict()
    for schema_file in schema_files:
        schema.update(yaml.load(open(schema_file), Loader=yaml.FullLoader))
    return schema
