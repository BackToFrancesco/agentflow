# Re-import necessary libraries since the execution state was reset
import matplotlib.pyplot as plt
import numpy as np

# Test names (x-axis)
tests = ["Test 1", "Test 2", "Test 3"]

# Accuracy for each model in different tests (y-axis)
accuracy_data = {
    "Improved GPT-4o + Autoform": [100, 100, 100],
    "Improved GPT-4o": [100, 100, 80],
    "Improved GPT-4o-mini": [80, 80, 80],
    "Improved GPT-4o-mini + Autoform": [60, 80, 80],
    "Basic GPT-4o": [100, 80, 0],
    "Basic GPT-4o + Autoform": [100, 60, 0],
    "Basic GPT-4o-mini + Autoform": [100, 60, 0],
    "Basic GPT-4o-mini": [80, 40, 0],
}

# Colors for each model
colors = [
    "darkblue", "blue", "deepskyblue", "cyan",
    "darkgreen", "green", "lightgreen", "lime"
]

fig, ax = plt.subplots(figsize=(10, 6))

# Plot each model's accuracy over the tests
for (model, accuracies), color in zip(accuracy_data.items(), colors):
    ax.plot(tests, accuracies, marker='o', linestyle='-', label=model, color=color)

# Labels and title
ax.set_xlabel("Tests")
ax.set_ylabel("Accuracy (%)")
ax.set_title("Model Accuracy Across Tests")
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize="small")
# Show the plot
plt.grid(True, axis='y')
plt.show()
