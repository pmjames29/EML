from datetime import datetime
from flask import Flask, request, jsonify, json
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "webapp"
app.config[
    "MONGO_URI"
] = "mongodb://pmjames29:philippians413@mongo:27017/webapp?authSource=admin"

## The secret key will accept any key to ensure protection of access
## to the API endpoint in questions
app.config["JWT_SECRET_KEY"] = "my-secret-token"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)


## API Endpoint for registering a user into the system
@app.route("/users/register", methods=["POST"])
def register():
    users = mongo.db["users"]
    first_name = request.get_json()["first_name"]
    last_name = request.get_json()["last_name"]
    email = request.get_json()["email"]
    password = bcrypt.generate_password_hash(request.get_json()["password"]).decode(
        "utf-8"
    )
    created = datetime.utcnow()

    raw_user = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "created": created,
    }

    user_id = users.insert_one(raw_user).inserted_id

    new_user = users.find_one_or_404({"_id": user_id})

    result = {"email": new_user["email"] + " registered"}

    return jsonify({"result": result})


## API Endpoint for logging in a user to the system
@app.route("/users/login", methods=["POST"])
def login():
    users = mongo.db["users"]
    email = request.get_json()["email"]
    password = request.get_json()["password"]
    result = ""

    response = users.find_one({"email": email})

    if response:
        if bcrypt.check_password_hash(response["password"], password):
            access_token = create_access_token(
                identity={
                    "first_name": response["first_name"],
                    "last_name": response["last_name"],
                    "email": response["email"],
                }
            )
            result = jsonify({"token": access_token})
        else:
            result = jsonify({"error": "Invalid username and password"})
    else:
        result = jsonify({"result": "No results found"})
    return result


if __name__ == "__main__":
    app.run(debug=True)
