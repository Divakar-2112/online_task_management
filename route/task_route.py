from flask import Blueprint,request,jsonify
from model import db,Task,User
from datetime import datetime

tasks_route = Blueprint("tasks_route",__name__)

@tasks_route.route("/tasks",methods=["GET"])
@tasks_route.route("/tasks/<int:task_id>",methods=["GET"])
def get_task(task_id=None):
    if task_id:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status,
            "user_id": task.user_id
                        
        }
        return jsonify(task_data),200
    query = Task.query
    
    title = request.args.get("title")
    priority = request.args.get("priority")
    status = request.args.get("status")
    due_date = request.args.get("due_date")
    
    if title:
        query = query.filter(Task.title.ilike(f"%{title}%"))
    elif priority:
        query = query.filter(Task.priority == priority)
    elif status is not None:
        if status.lower() in ["true", "1"]:
            query = query.filter(Task.status.is_(True))
        elif status.lower() in ["false", "0"]:
            query = query.filter(Task.status.is_(False))
    elif due_date:
        try:    
            due_date_value = datetime.strptime(due_date, "%Y-%m-%d").date()
            query = query.filter(Task.due_date == due_date_value)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
        
    sort_by = request.args.get("sort_by", "id")  
    order = request.args.get("order", "asc")
    
    if hasattr(Task, sort_by):
        if order == "desc":
            query = query.order_by(getattr(Task, sort_by).desc())
        else:
            query = query.order_by(getattr(Task, sort_by).asc())

    tasks = query.all()
    tasks_list = [
        {
            "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "status": task.status,
                "user_id": task.user_id
                            
            } for task in tasks
        ]
    return jsonify(tasks_list),200

@tasks_route.route("/task",methods=["POST"])
def create_task():
    from model import User
    data = request.get_json()
    due_date_str = data.get("due_date")
    due_date = None
    if due_date_str:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        
        user = User.query.get(data.get('user_id'))
        if not user:
            return jsonify({"error": "User not found"}), 404
    
    new_task = Task(
        title=data["title"],
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
        due_date=due_date,
        status=data.get("status", "pending"),
        user_id=data["user_id"]
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created successfully", "task_id": new_task.id}), 200


@tasks_route.route("/task/<int:task_id>",methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get(task_id)    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if "user_id" in data:
        user = User.query.get(data["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        task.user_id = data["user_id"]
    
    if "due_date" in data:
        due_date_str = data["due_date"]
        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        else:
            task.due_date = None
    
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.priority = data.get("priority", task.priority)
    task.status = data.get("status", task.status)
    
    db.session.commit()
    
    return jsonify({"message": "Task updated successfully"}), 200

@tasks_route.route("/task/<int:task_id>",methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200

