from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json, os, threading

app = FastAPI()
lock = threading.Lock()
TODO_FILE = "todo.json"

# To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False
    priority: str = "medium"   # "low" | "medium" | "high"
    dueDate: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)

# ✅ 목록 조회 (검색/정렬 지원 가능)
@app.get("/todos", response_model=list[TodoItem])
def get_todos(completed: Optional[bool] = Query(None)):
    todos = load_todos()
    if completed is not None:
        todos = [t for t in todos if t["completed"] == completed]

    # 완료 X 먼저, 그 안에서 high > medium > low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    todos.sort(key=lambda t: (t["completed"], priority_order.get(t["priority"], 1)))
    return todos

# ✅ 추가
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    with lock:
        todos = load_todos()
        next_id = max([t["id"] for t in todos], default=0) + 1
        todo.id = next_id
        todos.append(todo.model_dump())
        save_todos(todos)
    return todo

# ✅ 수정
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    with lock:
        todos = load_todos()
        for idx, t in enumerate(todos):
            if t["id"] == todo_id:
                updated = updated_todo.model_dump()
                updated["id"] = todo_id
                todos[idx] = updated
                save_todos(todos)
                return updated
    raise HTTPException(status_code=404, detail="To-Do item not found")

# ✅ 삭제
@app.delete("/todos/{todo_id}", response_model=MessageResponse)
def delete_todo(todo_id: int):
    with lock:
        todos = load_todos()
        new_todos = [t for t in todos if t["id"] != todo_id]
        if len(new_todos) == len(todos):
            raise HTTPException(status_code=404, detail="To-Do item not found")
        save_todos(new_todos)
    return {"message": "To-Do item deleted"}

# ✅ HTML 서빙
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
