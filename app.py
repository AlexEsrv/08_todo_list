from flask import Flask, render_template, request
import json
from sqlalchemy import Column, Integer, String, Boolean, create_engine, select
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os

BaseORM = declarative_base()


class Task(BaseORM):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    done = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"Task (id={self.id} name={self.name})"

    def to_json(self):
        return {'id': self.id, 'name': self.name, 'done': self.done}


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

engine = create_engine(os.environ.get('DATABASE_URL'), connect_args={'check_same_thread': False})
BaseORM.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

db_session = Session()


def get_tasks(t_id=0):
    try:
        int_id = int(t_id)
        if int_id == 0:
            tasks_select = select(Task)
        else:
            tasks_select = select(Task).where(Task.id == int_id)
        result = db_session.execute(tasks_select).scalars().all()
        response = []
        for task in result:
            response.append(task.to_json())
        return {"status": "OK", "tasks": response}
    except Exception as e:
        return {"status": "error", "descr": str(e)}


def insert_task(data):
    try:
        new_task = Task(name=data['name'], done=False)
        db_session.add(new_task)
        db_session.commit()
        return {'status': 'OK', 'id': new_task.id, 'name': new_task.name}
    except Exception as e:
        return {"status": "error", "descr": str(e)}


def update_task(t_id, data):
    try:
        int_id = int(t_id)
        task = db_session.get(Task, int_id)
        if task is None:
            return {"status": "error", "descr": "task not found"}
        task.done = bool(data["done"])
        db_session.commit()
        return {"status": "OK"}
    except Exception as e:
        return {"status": "error", "descr": str(e)}


def delete_task(t_id):
    try:
        int_id = int(t_id)
        task = db_session.get(Task, int_id)
        if task is None:
            return {"status": "error", "descr": "task not found"}
        db_session.delete(task)
        db_session.commit()
        return {"status": "OK"}
    except Exception as e:
        return {"status": "error", "descr": str(e)}


@app.route('/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/tasks/<t_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def tasks(t_id=0):
    if request.method == 'GET':
        return json.dumps(get_tasks(t_id))
    elif request.method == 'POST':
        return json.dumps(insert_task(request.json))
    elif request.method == 'PUT':
        return json.dumps(update_task(t_id, request.json))
    if request.method == 'DELETE':
        return json.dumps(delete_task(t_id))


@app.route('/')
def home():
    tasks_response = get_tasks()
    if tasks_response["status"] == "OK":
        task_list = tasks_response["tasks"]
    else:
        task_list = []
    return render_template('index.html', tasks=task_list)


if __name__ == '__main__':
    app.run(debug=True)
