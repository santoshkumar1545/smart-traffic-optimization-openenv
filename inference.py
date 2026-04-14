from PIL import Image
import random

def predict_traffic(image_path):
    image = Image.open(image_path).convert("RGB")

    traffic_levels = ["Low", "Medium", "High"]

    return (
        random.choice(traffic_levels),  # traffic_level
        round(random.uniform(0.7, 0.99), 2),  # confidence
        random.randint(10, 100),  # vehicle_count
        round(random.uniform(0.1, 0.9), 2)  # density
    )