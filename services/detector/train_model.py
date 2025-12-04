import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import random

# 1. Generate "Training Data" (Historical Normal Data)
# We need to teach the model what "Normal" looks like.
# We create 1000 "Legit" data points.
print("🧠 Generating historical training data...")

data = []

# 1. Generate "Average" Players (80% of data)
for _ in range(800):
    reaction_time = random.randint(150, 600)
    mouse_speed = random.randint(5, 20)
    accuracy = random.uniform(0.2, 0.8)
    data.append([reaction_time, mouse_speed, accuracy])

# 2. Generate "Pro" Players (20% of data) - CRITICAL FIX
# We teach the model that being fast (100ms) is rare, but LEGIT.
for _ in range(200):
    reaction_time = random.randint(100, 450) # Faster than average
    mouse_speed = random.randint(15, 30)     # Snappier aim
    accuracy = random.uniform(0.7, 0.95)     # High accuracy
    data.append([reaction_time, mouse_speed, accuracy])

# Convert to DataFrame
df = pd.DataFrame(data, columns=['reaction_time', 'mouse_speed', 'accuracy'])

# 2. Train the Model
# Isolation Forest works by isolating anomalies. 
# contamination=0.05 means "We expect about 5% of data to be weird."
print("🎓 Training Isolation Forest Model...")
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
model.fit(df)

# 3. Save the Model
# We serialize the math into a file so the other script can load it.
joblib.dump(model, 'cheat_detector_model.pkl')
print("✅ Model saved to 'cheat_detector_model.pkl'")

# Optional: Test it immediately
print("\n--- Quick Test ---")
test_legit = [[300, 10, 0.5]] # Normal stats
test_cheat = [[20, 100, 0.99]] # Aimbot stats

print(f"Legit Case Score: {model.predict(test_legit)[0]} (1 is Normal, -1 is Anomaly)")
print(f"Cheat Case Score: {model.predict(test_cheat)[0]} (1 is Normal, -1 is Anomaly)")