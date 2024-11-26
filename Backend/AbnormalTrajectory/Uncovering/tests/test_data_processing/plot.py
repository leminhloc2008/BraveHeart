import matplotlib.pyplot as plt
import numpy as np
import time

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
print("Hello")
plt.show(block=True)

plt.pause(3)

plt.close()

print ("End of script") 
