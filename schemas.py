from pydantic import BaseModel


# Create ToDoRequest from parent class Base Model(Pydantic Model) that defines the valid inputs
class ToDo(BaseModel):
    task_id: int = 0
    action: str = 'add'
    task: str = 'Your Task'
    is_completed: bool = False
