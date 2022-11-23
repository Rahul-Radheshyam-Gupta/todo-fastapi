import json
from fastapi import FastAPI, status, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
import models
import sqlite3
from starlette.requests import Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# DB initialization
Base.metadata.create_all(engine)

templates = Jinja2Templates(directory="templates")

# Render Todo Home Page
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/todos")
def read_todo_list(start_date: str, end_date: str, status: int = 0):
    """
    This function returns the list of todos as per the query params.
    :param start_date: start date for tasks
    :param end_date:   end date for tasks
    :param status:     Its either 0 or 1 where 1 for complete and 0 for pending
    :return: List of todos
    """
    con = sqlite3.connect("todo.db", check_same_thread=False)
    cur = con.cursor()

    raw_sql = f'''
            select * from todos as t where 
            strftime('%Y-%m-%d', t.created_at)>='{start_date}' and 
            strftime('%Y-%m-%d', t.created_at)<='{end_date}' and is_completed={status} order by t.created_at desc
        '''
    print("todo_list", start_date, end_date, status, raw_sql)

    cur.execute(raw_sql)
    todo_list = cur.fetchall()
    con.close()
    # todo_list = session.query(models.ToDo).filter(models.ToDo.is_completed==1)
    print("todo_list", todo_list)
    data = {
        'todos': todo_list
    }
    return JSONResponse(content=data, status_code=200)


@app.get("/static")
def load_static():
    """
    This function return the pending and completed task count.
    :return: Dict that contains pending and complete count
    """
    static_dict = {
        'pending_count': 0,
        'completed_count': 0,
    }
    with sqlite3.connect("todo.db", check_same_thread=False) as con:
        cur = con.cursor()
        raw_sql_for_pending_task = f'''select count(t.is_completed) from todos as t where t.is_completed=0 limit 1'''
        no_of_pending_task = cur.execute(raw_sql_for_pending_task).fetchall()
        raw_sql_for_complete_task = f'''select count(t.is_completed) from todos as t where t.is_completed=1 limit 1'''
        no_of_completed_task = cur.execute(raw_sql_for_complete_task).fetchall()
        static_dict = {
            'pending_count': no_of_pending_task[0][0],
            'completed_count': no_of_completed_task[0][0],
        }
    print("todo_list", static_dict)
    return JSONResponse(content=static_dict, status_code=200)


@app.post("/todos_post", status_code=200)
async def common_todo_action_function(request: Request):
    """
    This function is a common post function that perform different functionalities based on the action.
    Action       Required Field           Function Description
    ----------------------------------------------------------------------------
    add                 -                 add a task to database table todos
    update             task_id            update a task
    complete           task_id            mark a task complete
    delete             task_id            delete a task

    :param request: request instance of Request class
    :return: None if action is delete else return the current task object
    """
    # create request data dictionary from the post data
    request_body = await request.body()
    request_body_list = request_body.decode('utf-8').split('&')
    request_data_dict = {}
    for item in request_body_list:
        key_value_pair = item.split('=')
        request_data_dict[key_value_pair[0]] = key_value_pair[1]

    # Set required variables to perform desired action
    action = request_data_dict.get('action')
    task = request_data_dict['task'].replace('%20', ' ') if request_data_dict.get('task') else ''
    task_id = request_data_dict.get('task_id')
    print(action, task_id, task, sep='|')

    current_todo = None
    with SessionLocal() as session:
        if action == "add":
            # create an instance of the ToDo database model
            current_todo = models.ToDo(task=task)
            session.add(current_todo)

        elif task_id:
            current_todo = session.query(models.ToDo).get(task_id)
            if action == "update":
                current_todo.task = task
            elif action == "complete":
                current_todo.is_completed = 1
            elif action == "delete":
                session.delete(current_todo)

        else:
            raise HTTPException(status_code=400, detail="Invalid Action!")

        # Commit changes
        session.commit()
        if action == 'add' and current_todo:
            session.refresh(current_todo)

    data = {'todo': current_todo if action != 'delete' else None}
    return data

