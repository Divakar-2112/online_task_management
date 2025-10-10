from flask import Blueprint,request,jsonify
from model import db,User

users_route = Blueprint("users_route",__name__)

@users_route.route("/users", methods=["GET"])
@users_route.route("/users/<int:user_id>", methods=["GET"])
def get_users(user_id=None):
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }
        return jsonify(user_data), 200

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

    users_list = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }
        for user in users
    ]
    
    return jsonify(users_list), 200


@users_route.route("/user",methods=["POST"])
def create_user():
    data = request.get_json()
    
    new_user = User(
        name=data["name"],
        email=data["email"],
        role=data.get("role", ""),
        status=data.get("status", True)
    )
    new_user.password = data["password"]

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201


@users_route.route("/user/<int:user_id>",methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.role = data.get("role", user.role)
    user.status = data.get("status", user.status)
    
    if "password" in data:
        user.password = data["password"]
    
    db.session.commit()
    
    return jsonify({"message": "User updated successfully"}), 200


@users_route.route("/user/<int:user_id>",methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "User deleted successfully"}), 200
    


