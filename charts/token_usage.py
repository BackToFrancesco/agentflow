from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Data for different test distributions
configurations = [
    "Improved GPT-4o + Autoform",
    "Improved GPT-4o",
    "Improved GPT-4o-mini",
    "Improved GPT-4o-mini + Autoform",
]

# Success breakdown for each configuration, scaled to 60000
breakdowns = {
    "Improved GPT-4o + Autoform": [(4065+4663+3351)/3, (39940+41463+24456)/3],
    "Improved GPT-4o": [(4068+5058+4512)/3, (28395+38582+37522)/3],
    "Improved GPT-4o-mini": [(3561+5606+5216)/3, (20436+44358+42624)/3],
    "Improved GPT-4o-mini + Autoform": [(3416+5105+5495)/3, (23328+49937+49463)/3],
}

colors = {
    "Improved GPT-4o-mini": ["lightgreen", "green", "darkgreen"],
    "Improved GPT-4o": ["lightgreen", "green", "darkgreen"],
    "Improved GPT-4o-mini + Autoform": ["lightgreen", "green", "darkgreen"],
    "Improved GPT-4o + Autoform": ["lightgreen", "green", "darkgreen"]
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
ax.set_ylabel('Average Cost')
ax.set_title('Token Usage Comparison with Breakdown')

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
