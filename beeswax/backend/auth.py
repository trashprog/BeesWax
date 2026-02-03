from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime
from bson import ObjectId

auth_bp = Blueprint("auth", __name__)

def init_auth(db):
    users = db["users"]

    @auth_bp.route("/auth/register", methods=["POST"])
    def register():
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Missing fields"}), 400

        if users.find_one({"email": email}):
            return jsonify({"error": "User already exists"}), 409

        hashed = hashpw(password.encode(), gensalt())

        users.insert_one({
            "email": email,
            "password": hashed,
            "trust_score": 0,
            "created_at": datetime.utcnow()
        })

        return jsonify({"message": "User created"}), 201

    @auth_bp.route("/auth/login", methods=["POST"])
    def login():
        data = request.json
        email = data.get("email")
        password = data.get("password")

        user = users.find_one({"email": email})
        if not user or not checkpw(password.encode(), user["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=str(user["_id"]))
        return jsonify({"access_token": token})
    

    @auth_bp.route("/auth/me", methods=["GET"])
    @jwt_required()  # require a valid JWT
    def get_current_user():
        user_id = get_jwt_identity()  # this is the _id stored in JWT
        user = users.find_one({"_id": ObjectId(user_id)}, {"password": 0})  # exclude password
        if not user:
            return jsonify({"error": "User not found"}), 404

        user["_id"] = str(user["_id"])  # convert ObjectId to string
        return jsonify({"user": user})
    


    

