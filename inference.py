from PIL import Image
import random

def predict_traffic(image_path):
    print("🔥 Received image:", image_path)

    try:
        image = Image.open(image_path).convert("RGB")
        print("✅ Image loaded successfully")

        traffic_levels = ["Low", "Medium", "High"]

        result = (
            random.choice(traffic_levels),
            round(random.uniform(0.7, 0.99), 2),
            random.randint(10, 100),
            round(random.uniform(0.1, 0.9), 2)
        )

        print("✅ Prediction:", result)
        return result

    except Exception as e:
        print("❌ ERROR in prediction:", str(e))
        return "Error", 0, 0, 0