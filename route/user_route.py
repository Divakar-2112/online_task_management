from flask import Blueprint, request, jsonify
from model import db, User
import re
from datetime import datetime, timedelta
import jwt
from auth_middleware import check_token_expiry

secret_key = '123456'

users_route = Blueprint("users_route", __name__)

# ===================== Validation =========================
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def is_valid_password(password):
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password)

# ===================== GET USERS ==========================
@users_route.route("/users", methods=["GET"])
@users_route.route("/users/<int:user_id>", methods=["GET"])
@check_token_expiry
def get_users(user_id=None):
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }), 200

    query = User.query
    name = request.args.get("name")
    email = request.args.get("email")
    role = request.args.get("role")
    status = request.args.get("status")

    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if role:
        query = query.filter(User.role == role)
    if status is not None:
        if status.lower() in ["true", "1"]:
            query = query.filter(User.status.is_(True))
        elif status.lower() in ["false", "0"]:
            query = query.filter(User.status.is_(False))

    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")
    if hasattr(User, sort_by):
        if order == "desc":
            query = query.order_by(getattr(User, sort_by).desc())
        else:
            query = query.order_by(getattr(User, sort_by).asc())

    users = query.all()
    return jsonify([
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role, "status": u.status}
        for u in users
    ]), 200

# ===================== LOGIN ==========================
@users_route.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    expiry = datetime.utcnow() + timedelta(minutes=1)
    payload = {"email": email, "expiry_time": expiry.timestamp()}
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return jsonify({
        "user_id": user.id,
        "message": "Login successful",
        "user_details": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": user.status
        },
        "token": token
    }), 200

# ===================== CREATE USER ==========================
@users_route.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Weak password"}), 400

    new_user = User(name=name, email=email, role=data.get("role", ""), status=data.get("status", True))
    new_user.password = password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201

# ===================== UPDATE USER ==========================
@users_route.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if "email" in data:
        new_email = data["email"]
        if not is_valid_email(new_email):
            return jsonify({"error": "Invalid email format"}), 400
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({"error": "Email already in use"}), 400
        user.email = new_email

    user.name = data.get("name", user.name)
    user.role = data.get("role", user.role)
    user.status = data.get("status", user.status)

    if "password" in data:
        if not is_valid_password(data["password"]):
            return jsonify({"error": "Weak password"}), 400
        user.password = data["password"]

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

# ===================== DELETE USER ==========================
@users_route.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200
