import yaml

from typing import List
from concurrent.futures import ThreadPoolExecutor


def load_schema(schema_files: List[str]):
    schema = dict()
    for schema_file in schema_files:
        schema = merge_dicts(dict(schema), yaml.load(open(schema_file), Loader=yaml.FullLoader))
    return dict(schema)


def merge_dicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(merge_dicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def parse_params(action_params: dict, context: dict, params: dict):
    parsed_params = dict()
    eval_context = {
        "context": context,
        "params": params
    }
    for key, value in action_params.items():
        if isinstance(value, dict):
            parsed_params[key] = parse_params(value, context, params)
        else:
            try:
                parsed_params[key] = eval(value, eval_context)
            except Exception as _:
                parsed_params[key] = value

    return parsed_params


def execute(fn, arr):
    with ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(fn, arr))
