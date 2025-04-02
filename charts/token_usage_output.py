# Re-import necessary libraries since the execution state was reset
import matplotlib.pyplot as plt
import numpy as np

# Test names (x-axis)
tests = ["Test 1", "Test 2", "Test 3"]

# OUTPUT TOKEN COMPARISON
accuracy_data = {
    "Multi-turn agents GPT-4o": [4168,5058,4512],
    "Multi-turn agents GPT-4o-mini": [3561,5606,5216],
    "Multi-turn agents GPT-4o + Autoform": [3351,4663,4065],
    "ImproMulti-turn agentsved GPT-4o-mini + Autoform": [3416,5105,5095],
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
ax.set_ylabel("AVG Output Token Usage")
ax.set_title("AgentisFlow Average Output Token Usage Across Tests")
ax.legend(loc='lower center', fontsize="small")# Show the plot
plt.grid(True, axis='y')
plt.show()
