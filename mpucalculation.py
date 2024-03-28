import matplotlib.pyplot as plt
import numpy as np

mc_blocks_adv=np.array([4, 10, 9])
mc_blocks=np.array([23, 17, 10])
tot_blocks_adv=np.array([13, 12, 9])
tot_blocks=np.array([52, 42, 23])
hashing_power=np.array([20, 30, 50])

mpu_adv=mc_blocks_adv/ mc_blocks
mpu_overall=tot_blocks_adv/ tot_blocks

# Plotting
plt.figure(figsize=(8, 6))

# Plot mpu_adv
plt.plot(hashing_power, mpu_adv, label='mpu_adv', marker='o')

# Plot mpu_overall
plt.plot(hashing_power, mpu_overall, label='mpu_overall', marker='s')

# Labeling and titles
plt.xlabel('Hashing Power')
plt.ylabel('MPU')
plt.title('MPU vs Hashing Power')
plt.legend()

# Display the plot
plt.grid(True)
plt.show()
