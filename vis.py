import random
from itertools import count
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import csv
import math

VOI = [
    # ("first_run", "%QX0.7"),
    ("flow_set", "%MW1"),
    ("a_setpoint", "%MW2"),
    ("pressure_sp", "%MW3"),
    ("override_sp", "%MW4"),
    ("level_sp", "%MW5"),
    ("f1_valve_pos", "%IW100"),
    ("f1_flow", "%IW101"),
    ("f2_valve_pos", "%IW102"),
    ("f2_flow", "%IW103"),
    ("purge_valve_pos", "%IW104"),
    ("purge_flow", "%IW105"),
    ("product_valve_pos", "%IW106"),
    ("product_flow", "%IW107"),
    ("pressure", "%IW108"),
    ("level", "%IW109"),
    ("a_in_purge", "%IW110"),
    ("b_in_purge", "%IW111"),
    ("c_in_purge", "%IW112"),
    ("f1_valve_sp", "%QW100"),
    ("f2_valve_sp", "%QW101"),
    ("purge_valve_sp", "%QW102"),
    ("product_valve_sp", "%QW103"),
    # ("hmi_pressure", "%MW20"),
    # ("hmi_level", "%MW21"),
    # ("hmi_f1_valve_pos", "%MW22"),
    # ("hmi_f1_flow", "%MW23"),
    # ("hmi_f2_valve_pos", "%MW24"),
    # ("hmi_f2_flow", "%MW25"),
    # ("hmi_purge_valve_pos", "%MW26"),
    # ("hmi_purge_flow", "%MW27"),
    # ("hmi_product_valve_pos", "%MW28"),
    # ("hmi_product_flow", "%MW29"),
    # ("scan_count", "%MW30"),
    # ("run_bit", "%QX0.5"),
    # ("attack", "%QX0.6"),
]

for i, (name, addr) in enumerate(VOI):
    if addr.startswith("%QX"):
        # print("COIL")
        VOI[i] = (name, addr, int(addr[5:]))
    elif addr.startswith("%QW"):
        # print("HOLDING REGISTER")
        VOI[i] = (name, addr, int(addr[3:]))
    elif addr.startswith("%MW"):
        # print("CONTROL REGISTER")
        VOI[i] = (name, addr, int(addr[3:]))
    elif addr.startswith("%IW"):
        # print("INPUT REGISTER")
        VOI[i] = (name, addr, int(addr[3:]))
        
# print(VOI)

variable_values = {}
fieldnames = [name for name, addr, tag in VOI]

data_path = os.path.join(os.getcwd(), 'data.csv')


if os.path.exists(data_path) == False:
    with open(data_path, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

plt.style.use('fivethirtyeight')

os.path.exists(data_path)

# Determine the number of subplots based on the length of VOI
num_vars = len(VOI)
cols = math.ceil(math.sqrt(num_vars))  # Calculate the number of columns
rows = math.ceil(num_vars / cols)      # Calculate the number of rows

fig, axs = plt.subplots(rows, cols, figsize=(10, 10))

index = count()

FS = 12
ymin = 0
ymax = 25000
def animate(i):
    data = pd.read_csv(data_path)
    
    # Downsample data if necessary (e.g., take every 10th row)
    data = data.iloc[::10, :]  # Adjust the step as needed
    
    # Clear all subplots before plotting
    for ax in axs.flat:
        ax.clear()
    
    # Calculate elapsed time
    elapsed_time = data['timestamp'] - data['timestamp'].iloc[0]  # Calculate elapsed time from the first timestamp
    
    # Iterate through each variable and plot
    for j, column in enumerate(data.columns[1:]):  # Skip the 'time' column
        row = j // cols  # Determine the row index
        col = j % cols   # Determine the column index
        axs[row, col].plot(elapsed_time, data[column], label=column)  # Plot each column against elapsed time
        
        # Set y-ticks font size
        axs[row, col].tick_params(axis='y', labelsize=8)  # Change 8 to your desired size
        axs[row, col].tick_params(axis='x', labelsize=8)  # Change 8 to your desired size

    # axs[-1, 0].set_xlabel('Elapsed Time [s]', fontsize=FS)  # Set xlabel for the last subplot


ani = FuncAnimation(plt.gcf(), animate, interval=10)
# axs[3].set_xlabel('Time [s]')

plt.tight_layout()
check = plt.show()

