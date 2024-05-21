# data from https://allisonhorst.github.io/palmerpenguins/

import matplotlib.pyplot as plt
import numpy as np

#(14.754098360655737, 19.01639344262295, 16.721311475409838, 17.704918032786885, 9.180327868852459, 11.475409836065573, 11.147540983606557) alpha 0 beta 1
#(14.285714285714285, 20.816326530612244, 16.3265306122449, 17.142857142857142, 7.346938775510205, 10.204081632653061, 13.877551020408163) alpha 0.2 beta 0.8
#(13.654618473895583, 18.473895582329316, 15.261044176706829, 16.06425702811245, 7.630522088353414, 12.048192771084338, 16.867469879518072) alpha 1 beta 0 
#(14.963503649635038, 18.613138686131386, 17.153284671532848, 16.78832116788321, 9.124087591240876, 9.854014598540147, 13.503649635036496) alpha 0.8 beta 0.2 
#(15.579710144927535, 19.565217391304348, 17.02898550724638, 17.02898550724638, 8.695652173913043, 9.057971014492754, 13.043478260869565) alpha 0.5 beta 0.5

species = ('n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n<not1&2hop>')
edge_distribution = {
    'propagation scheme 1': (4.754098360655737, 19.01639344262295, 16.721311475409838, 17.704918032786885, 9.180327868852459, 11.475409836065573, 11.147540983606557),
    'propagation scheme 2': (14.285714285714285, 20.816326530612244, 16.3265306122449, 17.142857142857142, 7.346938775510205, 10.204081632653061, 13.877551020408163),

    'propagation scheme 3': (13.654618473895583, 18.473895582329316, 15.261044176706829, 16.06425702811245, 7.630522088353414, 12.048192771084338, 16.867469879518072),
    'propagation scheme 4': (14.963503649635038, 18.613138686131386, 17.153284671532848, 16.78832116788321, 9.124087591240876, 9.854014598540147, 13.503649635036496),

    'propagation scheme 5': (15.579710144927535, 19.565217391304348, 17.02898550724638, 17.02898550724638, 8.695652173913043, 9.057971014492754, 13.043478260869565),
}

x = np.arange(len(species))  # the label locations
width = 0.15  # the width of the bars
multiplier = 0

fig, ax = plt.subplots()

for attribute, measurement in edge_distribution.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    #ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Weight of Counts')
ax.set_title('Counts of Trapped Edges')
ax.set_xticks(x + width, species)
ax.legend(loc='upper left', ncols=1)
ax.set_ylim(0, 80)

#plt.xlabel('Test Distribution')

plt.show()


