from flask import Blueprint, request, jsonify
from model import db, Task, User
from datetime import datetime
from auth_middleware import check_token_expiry

tasks_route = Blueprint("tasks_route", __name__)

# ===================== GET TASKS ==========================
@tasks_route.route("/tasks", methods=["GET"])
@tasks_route.route("/tasks/<int:task_id>", methods=["GET"])
@check_token_expiry
def get_task(task_id=None):
    if task_id:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status,
            "user_id": task.user_id
        }), 200

    query = Task.query
    title = request.args.get("title")
    priority = request.args.get("priority")
    status = request.args.get("status")
    due_date = request.args.get("due_date")

    if title:
        query = query.filter(Task.title.ilike(f"%{title}%"))
    if priority:
        query = query.filter(Task.priority == priority)
    if status:
        query = query.filter(Task.status == status)
    if due_date:
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
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status,
            "user_id": t.user_id
        } for t in tasks
    ]), 200

# ===================== CREATE TASK ==========================
@tasks_route.route("/task", methods=["POST"])
@check_token_expiry
def create_task():
    data = request.get_json()
    user = User.query.get(data.get("user_id"))
    if not user:
        return jsonify({"error": "User not found"}), 404

    due_date = None
    if data.get("due_date"):
        due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()

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
    return jsonify({"message": "Task created successfully", "task_id": new_task.id}), 201

# ===================== UPDATE TASK ==========================
@tasks_route.route("/task/<int:task_id>", methods=["PUT"])
@check_token_expiry
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
        if data["due_date"]:
            task.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        else:
            task.due_date = None

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.priority = data.get("priority", task.priority)
    task.status = data.get("status", task.status)

    db.session.commit()
    return jsonify({"message": "Task updated successfully"}), 200

# ===================== DELETE TASK ==========================
@tasks_route.route("/task/<int:task_id>", methods=["DELETE"])
@check_token_expiry
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200
