from flower import ActionProtocol
from flower.core.functions import parse_params, eval_param


class BasicMapping(ActionProtocol):
    should_parse_params = True

    def __call__(self, context, workflow_context, params):
        return params


class ListMapping(ActionProtocol):
    should_parse_params = False

    def __call__(self, context, workflow_context, params):
        input_list = eval_param(params["input"], params, context)

        mapping_output = params["output"]

        filter_expression = params.get("filter", None)

        if filter_expression:
            input_list = filter(lambda x: eval_param(filter_expression, x, context), input_list)

        output_results = []
        for item in input_list:
            output_results.append(parse_params(mapping_output, context, item))

        return output_results
