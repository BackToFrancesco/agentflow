import matplotlib.pyplot as plt
import numpy as np

# Test names (x-axis)
tests = ["Test 1", "Test 2", "Test 3"]

# Accuracy for each model in different tests (y-axis)
accuracy_data = {
    "Multi-turn agents GPT-4o + Autoform": [0.0908, 0.1442, 0.1348],
    "Multi-turn agents GPT-4o": [0.1081, 0.1411, 0.1333],
    "Multi-turn agents GPT-4o-mini": [0.0049, 0.0096, 0.0091],
    "Multi-turn agents GPT-4o-mini + Autoform": [0.0053, 0.0101, 0.0100],
}

# Colors for each model
colors = [
    "darkred", "red",
    "darkblue", "orange",
]

# Marker styles for each model
markers = [
    's', 'o',
    's', 'o',
]

fig, ax = plt.subplots(figsize=(10, 6))

# Plot each model's accuracy over the tests
for (model, accuracies), color, marker in zip(accuracy_data.items(), colors, markers):
    linestyle = '--' if 'Autoform' in model else '-'  # Dashed line for Autoform configurations
    ax.plot(tests, accuracies, marker=marker, linestyle=linestyle, label=model, color=color)
    
    # Add cost labels
    for i, cost in enumerate(accuracies):
        if 'Autoform' in model:
            ax.text(tests[i], cost + 0.002, f"{cost:.3f}", ha='center', va='bottom', color=color, fontsize=9)
        else:
            ax.text(tests[i], cost - 0.002, f"{cost:.3f}", ha='center', va='top', color=color, fontsize=9)

# Labels and title
ax.set_ylabel("Cost in Euros (€)")
ax.set_title("AgentisFlow Average Cost Across Tests")
ax.legend(loc='center right', fontsize="small")
plt.grid(True, axis='y')
plt.show()
