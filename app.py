from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS
from datetime import datetime

app = Flask(__name__)

# Enable CORS to allow requests from frontend
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_sugar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class BloodSugarLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    blood_sugar = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.String(50), nullable=True)  # e.g., Breakfast, Lunch, etc.

    def to_dict(self):
        return {
            "id": self.id,
            "date_time": self.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            "blood_sugar": self.blood_sugar,
            "meal_type": self.meal_type
        }

# Routes
@app.route('/log', methods=['POST'])
def add_log():
    if not request.is_json:
        return jsonify({"error": "Invalid request format. JSON data required."}), 400

    data = request.get_json()
    blood_sugar = data.get('blood_sugar')
    meal_type = data.get('meal_type')

    if blood_sugar is None:
        return jsonify({"error": "Blood sugar value is required"}), 400

    log = BloodSugarLog(blood_sugar=blood_sugar, meal_type=meal_type)
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Log added successfully", "log": log.to_dict()}), 201

@app.route('/logs', methods=['GET'])
def get_logs():
    logs = BloodSugarLog.query.order_by(BloodSugarLog.date_time.desc()).all()
    return jsonify([log.to_dict() for log in logs])

@app.route('/log/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    log = BloodSugarLog.query.get(log_id)
    if not log:
        return jsonify({"error": "Log not found"}), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": "Log deleted successfully"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized!")
    app.run(host='0.0.0.0', port=5000, debug=True)
