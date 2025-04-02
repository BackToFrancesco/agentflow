# Re-import necessary libraries since the execution state was reset
import matplotlib.pyplot as plt
import numpy as np

# Test names (x-axis)
tests = ["Test 1", "Test 2", "Test 3"]

# Accuracy for each model in different tests (y-axis)
# accuracy_data = {
#     "Improved GPT-4o + Autoform [INPUT TOKEN]": [39940,41463,24456],
#     "Improved GPT-4o [INPUT TOKEN]": [28395,38582,37522],
#     "Improved GPT-4o-mini [INPUT TOKEN]": [20436,44358,42624],
#     "Improved GPT-4o-mini + Autoform [INPUT TOKEN]": [23328,49937,49463],
#     "Improved GPT-4o + Autoform [OUTPUT TOKEN]": [4065,4663,3351],
#     "Improved GPT-4o [OUTPUT TOKEN]": [4068,5058,4512],
#     "Improved GPT-4o-mini [OUTPUT TOKEN]": [3561,5606,5216],
#     "Improved GPT-4o-mini + Autoform [OUTPUT TOKEN]": [3416,5105,5495],
# }
# TOTAL TOKEN COMPARISON
accuracy_data = {
    "Multi-turn agents GPT-4o": [32563,43640,42034],
    "Multi-turn agents GPT-4o-mini": [23997,49964,47840],
    "Multi-turn agents GPT-4o + Autoform": [27807,46126,44005],
    "Multi-turn agents GPT-4o-mini + Autoform": [26744,55042,54558],
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
ax.set_ylabel("AVG Total Token Usage")
ax.set_title("AgentisFlow Total Token Usage Across Tests")
ax.legend(loc='lower right', fontsize="small")# Show the plot
plt.grid(True, axis='y')
plt.show()
