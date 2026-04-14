from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
from inference import predict_traffic

app = Flask(__name__, static_folder=".", static_url_path="")

# Upload folder setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------------
# Signal Time Logic
# -------------------------------
def allocate_signal_times(vehicle_counts, emergency_road=None):
    min_time = 20
    max_time = 60

    total_vehicles = sum(vehicle_counts.values())

    if total_vehicles == 0:
        signal_times = {road: min_time for road in vehicle_counts}
    else:
        signal_times = {}
        for road, count in vehicle_counts.items():
            proportion = count / total_vehicles
            signal_time = int(min_time + proportion * (max_time - min_time) * 4)
            signal_time = max(min_time, min(signal_time, max_time))
            signal_times[road] = signal_time

    # Emergency override
    if emergency_road and emergency_road in signal_times:
        signal_times[emergency_road] = max_time

    return signal_times


# -------------------------------
# Routes
# -------------------------------

# Home page
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# Serve uploaded images
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# Prediction route
@app.route("/predict", methods=["GET", "POST"])
def predict():
    print("🔥 Predict route hit")

    if request.method == "GET":
        return "Use POST request", 200

    roads = ["road1", "road2", "road3", "road4"]

    predictions = {}
    vehicle_counts = {}
    signal_times = {}
    image_urls = {}

    emergency_road = request.form.get("emergencyRoad", "").strip()

    print("📥 Files received:", request.files)

    for road in roads:
        file = request.files.get(road)

        if file and file.filename != "":
            # Unique filename
            filename = str(uuid.uuid4()) + ".jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            print(f"📸 Saved: {filepath}")

            try:
                traffic_level, confidence, vehicle_count, density_ratio = predict_traffic(filepath)

                print("✅ Prediction:", traffic_level)

                road_name = road.replace("road", "Road")

                predictions[road_name] = traffic_level
                vehicle_counts[road_name] = vehicle_count
                image_urls[road_name] = f"/uploads/{filename}"

            except Exception as e:
                print("❌ Prediction error:", str(e))

    # Allocate signal times
    if vehicle_counts:
        signal_times = allocate_signal_times(vehicle_counts, emergency_road)

    # Determine priority road
    if emergency_road and emergency_road in vehicle_counts:
        priority_road = emergency_road
    elif vehicle_counts:
        priority_road = max(vehicle_counts, key=vehicle_counts.get)
    else:
        priority_road = None

    return jsonify({
        "predictions": predictions,
        "vehicle_counts": vehicle_counts,
        "signal_times": signal_times,
        "priority_road": priority_road,
        "image_urls": image_urls
    })


# -------------------------------
# Run (for local only)
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)