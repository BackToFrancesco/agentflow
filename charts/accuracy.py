from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Data for different test distributions
configurations = [
    "Multi-turn agents GPT-4o + Autoform",
    "Multi-turn agents GPT-4o",
    "Multi-turn agents GPT-4o-mini",
    "Multi-turn agents GPT-4o-mini + Autoform",
    #"Basic Agents GPT-4o",
    #"Basic Agents GPT-4o + Autoform",
    #"Basic Agents GPT-4o-mini + Autoform",
    #"Basic Agents GPT-4o-mini", 
]

# Overall success rate
success_rates = [33.33, 80, 60, 93.33, 40, 73.3, 60, 100]

# Success breakdown for each configuration
breakdowns = {
    "Multi-turn agents GPT-4o + Autoform": [33.33, 33.33, 33.33],
    "Multi-turn agents GPT-4o": [33.33, 33.33, 26.67],
    "Multi-turn agents GPT-4o-mini": [26.67, 26.67, 26.67],
    "Multi-turn agents GPT-4o-mini + Autoform": [20, 20, 28.57],
    "Basic Agents GPT-4o": [26.67, 33.33],
    "Basic Agents GPT-4o + Autoform": [33.33, 20.00],
    "Basic Agents GPT-4o-mini + Autoform": [26.67, 13.33],
    "Basic Agents GPT-4o-mini": [33.33],
}

colors = {
    "Basic Agents GPT-4o-mini": ["lightgreen", "green", "darkgreen"],
    "Basic Agents GPT-4o": ["lightgreen", "green", "darkgreen"],
    "Multi-turn agents GPT-4o-mini": ["lightgreen", "green", "darkgreen"],
    "Multi-turn agents GPT-4o": ["lightgreen", "green", "darkgreen"],
    "Basic Agents GPT-4o-mini + Autoform": ["lightgreen", "green", "darkgreen"],
    "Basic Agents GPT-4o + Autoform": ["lightgreen", "green", "darkgreen"],
    "Multi-turn agents GPT-4o-mini + Autoform": ["lightgreen", "green", "darkgreen"],
    "Multi-turn agents GPT-4o + Autoform": ["lightgreen", "green", "darkgreen"]
}

fig, ax = plt.subplots(figsize=(12, 6))
x_pos = np.arange(len(configurations))

for i, config in enumerate(configurations):
    start = 0
    for j, (test_success, color) in enumerate(zip(breakdowns[config], colors[config])):
        ax.bar(x_pos[i], test_success, bottom=start, color=color, edgecolor='black', label=f"{config} - Test {j+1}" if i == 2 else "")
        start += test_success

ax.set_xticks(x_pos)
ax.set_xticklabels(configurations, rotation=45, ha="right")
ax.set_ylabel('Success Rate (%)')
ax.set_title('Success Rate Comparison with Breakdown')

# Creating a legend for the color descriptions
legend_patches = [
    mpatches.Patch(color="lightgreen", label="Test 1"),
    mpatches.Patch(color="green", label="Test 2"),
    mpatches.Patch(color="darkgreen", label="Test 3")
]
ax.legend(handles=legend_patches, loc='upper right', fontsize='small')

# Display the chart
plt.tight_layout()
plt.show()
