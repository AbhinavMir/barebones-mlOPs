import matplotlib.pyplot as plt

# Read the values from the file and store them in a list
with open('results.txt') as f:
    values = [tuple(map(float, line.strip().split(','))) for line in f]

# Unpack the values into two separate lists for the x and y values
x, y = zip(*values)
print(x, y)

# Plot the x and y values
plt.bar (x, y)
plt.show()