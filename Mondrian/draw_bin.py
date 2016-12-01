import matplotlib.pyplot as plt
import numpy as np

# Z is your data set
N = 50
Z = np.random.random((N,N))
#print(Z)
#Z = np.random.randint(2, size=(N, N))
#print(Z)
# G is a NxNx3 matrix
G = np.zeros((N,N,3))

# Where we set the RGB for each pixel
G[Z>0.3] = [1,1,1]
G[Z<0.3] = [0,0,0]

plt.imshow(G, interpolation='nearest')
plt.show()
