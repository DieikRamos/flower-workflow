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
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def eval_param(expression: str, params: dict, context: dict):
    eval_context = {
        "context": context,
        "params": params
    }
    return eval(expression, eval_context)


def parse_params(action_params: dict, context: dict, params: dict):
    parsed_params = dict()
    for key, value in action_params.items():
        if isinstance(value, dict) and "expression" not in value:
            parsed_params[key] = parse_params(value, context, params)
        else:
            try:
                expression = value.get("expression") if isinstance(value, dict) else value
                parsed_params[key] = eval_param(expression, params, context)
            except Exception as _:
                parsed_params[key] = value.get("fallback_value") if isinstance(value, dict) else value

    return parsed_params


def execute(fn, arr):
    with ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(fn, arr))
