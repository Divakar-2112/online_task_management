# from pymongo import MongoClient
# from flask import request,jsonify,Flask

# client = MongoClient("mongodb://localhost:27017/")

# db = client["taskmanagement"]

# table = db["User"]

# table.insert_one({"name":"balaji","role":"IT","email":"balaji@gmail.com"})

# @users_route.route("/user",methods=["POST"])
# def create_user():
#     data = request.get_json()
#     if not data or not all(k in data for k in ("name", "email", "password")):
#         return jsonify({"error": "Missing required fields"}), 400

#     if User.query.filter_by(email=data["email"]).first():
#         return jsonify({"error": "Email already exists"}), 400

#     new_user = User(
#         name=data["name"],
#         email=data["email"],
#         role=data.get("role", ""),
#         status=data.get("status", True)
#     )
#     new_user.password = data["password"]

#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201