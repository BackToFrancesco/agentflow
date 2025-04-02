from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Data for different test distributions
configurations = [
    "Multi-turn agents GPT-4o",
    "Multi-turn agents GPT-4o-mini",
    "Basic Agents GPT-4o",
    "Basic Agents GPT-4o-mini",
]

# Success breakdown for each configuration
# Each value represents the number of tests passed out of 5
breakdowns = {
    "Multi-turn agents GPT-4o": [5, 5, 4],  # 5/5, 5/5, 4/5
    "Multi-turn agents GPT-4o-mini": [4, 4, 4],  # 4/5, 4/5, 4/5
    "Basic Agents GPT-4o": [4, 5],  # 4/5, 5/5
    "Basic Agents GPT-4o-mini": [5],  # 5/5
}

colors = {
    "Basic Agents GPT-4o-mini": ["#a1d99b", "#31a354", "#006d2c"],
    "Basic Agents GPT-4o": ["#a1d99b", "#31a354", "#006d2c"],
    "Multi-turn agents GPT-4o-mini": ["#a1d99b", "#31a354", "#006d2c"],
    "Multi-turn agents GPT-4o": ["#a1d99b", "#31a354", "#006d2c"],
}

fig, ax = plt.subplots(figsize=(12, 6))
x_pos = np.arange(len(configurations))
bar_width = 0.6

for i, config in enumerate(configurations):
    start = 0
    for j, (tests_passed, color) in enumerate(zip(breakdowns[config], colors[config])):
        ax.bar(x_pos[i], tests_passed * (100 / 15), bottom=start, color=color, edgecolor='black', width=bar_width)
        ax.text(x_pos[i], start + (tests_passed * (100 / 15)) / 2, f"Test {j+1}\n{tests_passed}/5", ha='center', va='center', color='white', fontsize=10)
        start += tests_passed * (100 / 15)

ax.set_xticks(x_pos)
ax.set_xticklabels(configurations, rotation=0, ha="center")
ax.set_ylabel('Success Rate (%)')
ax.set_title('Success Rate Comparison Across Configurations')
ax.set_ylim(0, 100)  # Set y-axis max to 100%
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Creating a legend for the color descriptions
legend_patches = [
    mpatches.Patch(color="#a1d99b", label="Test 1"),
    mpatches.Patch(color="#31a354", label="Test 2"),
    mpatches.Patch(color="#006d2c", label="Test 3")
]
ax.legend(handles=legend_patches, loc='upper right', fontsize='small')

# Display the chart
plt.tight_layout()
plt.show()
