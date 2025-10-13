from flask import request, jsonify
from functools import wraps
import jwt
from datetime import datetime

secret_key = '123456'

def check_token_expiry(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            token = auth.split(" ")[1]
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            expiry_timestamp = payload.get("expiry_time")
            expiry_time = datetime.fromtimestamp(expiry_timestamp)
            current_time = datetime.utcnow()

            if current_time > expiry_time:
                return jsonify({"message": "Token has expired!"}), 401

        except (jwt.DecodeError, IndexError):
            return jsonify({"message": "Invalid token!"}), 401

        return f(*args, **kwargs)
    return decorated
