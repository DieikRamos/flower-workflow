from fastapi import FastAPI, Header

from flower import Flower
from actions.print_message import PrintMessage

schema_files = ['./resources/base-workflows.yml', './resources/main-workflows.yml']

actions = {
    "print_message": PrintMessage()
}

flower = Flower(schema_files, actions=actions)

app = FastAPI()


@app.get("/field-summary/{field_id}")
def call_workflow(field_id: str, authorization: str = Header(alias="Authorization")):
    context = {
        "field_id": field_id,
        "authorization": authorization
    }

    result = flower.run("field_summary_flow", context)

    return result


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)

