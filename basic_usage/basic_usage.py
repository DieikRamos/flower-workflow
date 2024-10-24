from fastapi import FastAPI, Header

from flower import Flower
from actions.print_message import PrintMessage

schema_files = ["./resources/base-workflows.yml", "./resources/main-workflows.yml"]

actions = {"print_message": PrintMessage()}

flower = Flower(schema_files, actions=actions)

app = FastAPI()


@app.get("/author_summary/{author_key}")
def call_workflow(author_key: str, authorization: str = Header(alias="Authorization")):
    context = {"author_key": author_key, "authorization": authorization}

    result = flower.run("author_summary", context)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8080)
