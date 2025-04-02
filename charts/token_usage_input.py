# Re-import necessary libraries since the execution state was reset
import matplotlib.pyplot as plt
import numpy as np

# Test names (x-axis)
tests = ["Test 1", "Test 2", "Test 3"]

# INPUT TOKEN COMPARISON
accuracy_data = {
    "Multi-turn agents GPT-4o": [28395,38582,37522],
    "Multi-turn agents GPT-4o-mini": [20436,44358,42624],
    "Multi-turn agents GPT-4o + Autoform": [24456,41463,39940],
    "Multi-turn agents GPT-4o-mini + Autoform": [23328,49937,49463],
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
ax.set_ylabel("AVG Input Token Usage")
ax.set_title("AgentisFlow Average Input Token Usage Across Tests")
ax.legend(loc='lower right', fontsize="small")# Show the plot
plt.grid(True, axis='y')
plt.show()
