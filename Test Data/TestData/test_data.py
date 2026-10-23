import numpy as np
from matplotlib import pyplot as plt

ta = np.genfromtxt("TA_Test_Data.csv")
test_data = np.genfromtxt("test_data.csv", delimiter=',')

fig,ax = plt.subplots()
# ax.contourf(ta)
ax.contourf(test_data)