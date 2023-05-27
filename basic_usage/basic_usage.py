from flower import Flower
from actions.print_message import PrintMessage

schema_files = ['./resources/workflows.yml']

actions = {
    "print_message": PrintMessage()
}

flower = Flower(schema_files, actions=actions)

if __name__ == '__main__':
    flower.run("test_work_flow", {})
