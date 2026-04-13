from flask import Flask, request, jsonify, send_from_directory
import os
from inference import predict_traffic

app = Flask(__name__, static_folder=".", static_url_path="")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allocate_signal_times(vehicle_counts, emergency_road=None):
    """
    Dynamically allocate signal times based on vehicle counts.
    Minimum: 20 sec
    Maximum: 60 sec
    Emergency road gets highest priority.
    """
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


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/predict", methods=["POST"])
def predict():
    roads = ["road1", "road2", "road3", "road4"]

    predictions = {}
    confidences = {}
    vehicle_counts = {}
    density_scores = {}
    image_urls = {}

    emergency_road = request.form.get("emergencyRoad", "").strip()

    for road in roads:
        file = request.files.get(road)

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            traffic_level, confidence, vehicle_count, density_ratio = predict_traffic(filepath)

            road_name = road.replace("road", "Road")

            predictions[road_name] = traffic_level
            confidences[road_name] = confidence
            vehicle_counts[road_name] = vehicle_count
            density_scores[road_name] = density_ratio
            image_urls[road_name] = f"/uploads/{file.filename}"

    signal_times = allocate_signal_times(vehicle_counts, emergency_road=emergency_road)

    # Priority road logic
    if emergency_road and emergency_road in vehicle_counts:
        priority_road = emergency_road
    else:
        priority_road = max(vehicle_counts, key=vehicle_counts.get)

    return jsonify({
        "predictions": predictions,
        "confidences": confidences,
        "vehicle_counts": vehicle_counts,
        "density_scores": density_scores,
        "signal_times": signal_times,
        "priority_road": priority_road,
        "image_urls": image_urls,
        "emergency_road": emergency_road
    })


import os

port = int(os.environ.get("PORT", 10000))

app.run(host="0.0.0.0", port=port)