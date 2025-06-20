from flask import Blueprint, render_template, request, jsonify
import models  # Import the whole models file

app_routes = Blueprint("app_routes", __name__)

@app_routes.route("/")
def home():
    return render_template("index.html")


@app_routes.route("/book", methods=["POST"])
def book_car():
    data = request.json
    success = models.add_booking(
        data.get("user_id"),
        data.get("car_id"),
        data.get("start_date"),
        data.get("end_date"),
        data.get("total_cost"),
    )
    return jsonify({"success": success})
