#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt


# ##### make producer and consumer indifference curves

# In[3]:


import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt 

fig, ax = plt.subplots(1, 1,figsize=(5,5))
x=np.array([1,2,3,4,5,6,7])
y=np.array([100,50,25,12.5,6.25,3.125,1.5625])

model=make_interp_spline(x, y)

xs=np.linspace(1,7,500)
ys=model(xs)

plt.plot(xs, ys,color='black')
plt.title("Producer Isoquants")
plt.xlabel("Skilled Labor Input")
plt.ylabel("Unskilled Labor Input")

ax.hlines(y=2.1, xmin=4, xmax=6.5, linewidth=2, color='black',linestyle="--")
ax.vlines(x=4, ymin=2.1, ymax=11, linewidth=2, color='black',linestyle="--")


ax.hlines(y=11, xmin=2, xmax=4, linewidth=2, color='black',linestyle="--")
ax.vlines(x=2, ymin=11, ymax=51, linewidth=2, color='black',linestyle="--")


# ax1 = plt.axes()
x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])
plt.show()


# In[22]:


# Importing packages
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots(1, 1,figsize=(6,5))
# Define x and y values
x1 = np.arange(0,10,1)
x2 = np.arange(0,10,1)


y1 = 10-1*x1
y2 = 1+1*x2

y3 = 3+1*x2

y4 = 9-1*x1

x_axis = ax1.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax1.axes.get_yaxis()
y_axis.set_ticks([])


# Plot a simple line chart between two points (7, 8) and (42, 44)
plt.text(7,7.7, '$S_{skl}$', fontsize = 10)

plt.text(7,9.5, '$S_{skl^{1}}$', fontsize = 10)

plt.text(7,3, "$D_{skl}$", fontsize = 10)

plt.text(7,.8, "$D_{skl^{1}}$", fontsize = 10)


ax.set_xlabel("q")

ax.set_ylabel("w")


ax.hlines(y=6, xmin=-1, xmax=3, linewidth=2, color='black')
ax.hlines(y=5.5, xmin=-1, xmax=4.5, linewidth=2, color='black')

plt.text(0,6.2, "$p^1$", fontsize = 10)

plt.text(0,5, "$p$", fontsize = 10)

plt.ylim(0,11)
plt.plot(x1, y1, linewidth=2, color='black')
plt.plot(x2, y2, linewidth=2, color='black')
plt.plot(x2, y3, linewidth=2, color='black',linestyle="--")
plt.plot(x1, y4, linewidth=2, color='black',linestyle="--")
plt.show()



# In[73]:


# Importing packages
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 1,figsize=(6,5))
# Define x and y values
x1 = np.arange(0,10,1)
x2 = np.arange(0,10,1)


y1 = 10-1*x1
y2 = 1+1*x2

y3 = 2+1*x2

y4 = 8.5-1*x1

y5 = 8-1*x1

x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])


# Plot a simple line chart between two points (7, 8) and (42, 44)
plt.text(7,7.8, '$S_{unskl}$', fontsize = 10)

plt.text(7,10, '$S_{unskl^{1}}$', fontsize = 10)

plt.text(7,3, "$D_{unskl}$", fontsize = 10)

plt.text(7,1.5, "$D_{unskl^{1}}$", fontsize = 10)



ax.set_xlabel("q")

ax.set_ylabel("w")


ax.hlines(y=5, xmin=-1, xmax=3, linewidth=2, color='black')
ax.hlines(y=5.5, xmin=-1, xmax=4.5, linewidth=2, color='black')


plt.text(0,5.7, "$p$", fontsize = 10)
plt.text(0,4.5, "$p^1$", fontsize = 10)


plt.arrow(5, 3, .75,0,head_width=.15)

plt.ylim(0,11)
plt.plot(x1, y1, linewidth=2, color='black')
plt.plot(x2, y2, linewidth=2, color='black')
plt.plot(x2, y3, linewidth=2, color='black',linestyle="--")
plt.plot(x1, y4, linewidth=2, color='black',linestyle="--")
plt.plot(x1, y5, linewidth=2, color='black',linestyle="--")
plt.show()


# In[87]:


# Importing packages
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 1,figsize=(6,5))
# Define x and y values
x1 = np.arange(0,10,1)
x2 = np.arange(0,10,1)


y1 = 10-1*x1
y2 = 1+1*x2

y3 = 3+1*x2

y4 = 7.5-1*x1

x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])


# Plot a simple line chart between two points (7, 8) and (42, 44)
plt.text(7,7.7, '$S_{sg}$', fontsize = 10)

plt.text(7,9.5, '$S_{sg^{1}}$', fontsize = 10)

plt.text(7,3, "$D_{sg}$", fontsize = 10)

plt.text(7,.8, "$D_{sg^{1}}$", fontsize = 10)


ax.set_xlabel("q")

ax.set_ylabel("p")


ax.hlines(y=5.2, xmin=-1, xmax=2.4, linewidth=2, color='black')
ax.hlines(y=5.5, xmin=-1, xmax=4.5, linewidth=2, color='black')

plt.text(0,4.5, "$p^1$", fontsize = 10)

plt.text(0,5.7, "$p$", fontsize = 10)

plt.ylim(0,11)
plt.plot(x1, y1, linewidth=2, color='black')
plt.plot(x2, y2, linewidth=2, color='black')
plt.plot(x2, y3, linewidth=2, color='black',linestyle="--")
plt.plot(x1, y4, linewidth=2, color='black',linestyle="--")
plt.show()


# In[50]:


# Importing packages
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 1,figsize=(6,5))
# Define x and y values
x1 = np.arange(0,10,1)
x2 = np.arange(0,10,1)


y1 = 10-1*x1
y2 = 1+1*x2

y3 = 2+1*x2

y4 = 9.5-1*x1

y5 = 8-1*x1

x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])


# Plot a simple line chart between two points (7, 8) and (42, 44)
plt.text(7,7.8, '$S_{ug}$', fontsize = 10)



plt.text(7,3, "$D_{ug}$", fontsize = 10)

plt.text(7,1.5, "$D_{ug^{1}}$", fontsize = 10)



ax.set_xlabel("q")

ax.set_ylabel("p")


ax.hlines(y=5.3, xmin=-1, xmax=4.2, linewidth=2, color='black')
ax.hlines(y=5.5, xmin=-1, xmax=4.5, linewidth=2, color='black')

plt.text(0,4.8, "$p^1$", fontsize = 10)
plt.text(0,6, "$p$", fontsize = 10)


plt.arrow(5, 3, 1,0,head_width=.15)

plt.ylim(0,11)
plt.plot(x1, y1, linewidth=2, color='black')
plt.plot(x2, y2, linewidth=2, color='black')
# plt.plot(x2, y3, linewidth=2, color='black',linestyle="--")
plt.plot(x1, y4, linewidth=2, color='black',linestyle="--")
plt.plot(x1, y5, linewidth=2, color='black',linestyle="--")
plt.show()


# In[278]:


# Importing packages
import matplotlib.pyplot as plt

# Define x and y values
#x1 = np.arange(0,10,1)
#y1 = (11/1.5)-(2/3)*x1


x1 = np.arange(0,3,1)
x2 = np.arange(2,8,1)
x3 = np.arange(2,6.05,1)

y1 = 10-2*x1
y2 = (11/1.5)-(2/3)*x2
#y3 = (6.5/(3/4))-(4/3)*x2

y3=8.8571-(10/7)*x3


ax1 = plt.axes()
x_axis = ax1.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax1.axes.get_yaxis()
y_axis.set_ticks([])


# Plot a simple line chart between two points (7, 8) and (42, 44)
plt.text(.6,10, '$D_{total}$', fontsize = 10)


ax1.hlines(y=2, xmin=0, xmax=5.2, linewidth=2, color='black')

ax1.vlines(x=5.2, ymin=0, ymax=3.4, linewidth=2, color='black',linestyle='--')

ax1.hlines(y=3.4, xmin=5.2, xmax=10, linewidth=2, color='black')
#ax1.hlines(y=3.4, xmin=0, xmax=10, linewidth=2, color='black',linestyle=":")

plt.text(-.1,3.5, '$p_{mc}$', fontsize = 12)
plt.text(-.1,2.1, '$p_{1}$', fontsize = 12)

###plot vertical lines for consumption
ax1.vlines(x=4.85, ymin=0, ymax=2, linewidth=2, color='black')
ax1.vlines(x=6, ymin=0, ymax=3.4, linewidth=2, color='black')


###plot labels lines for consumption
plt.text(4.65,-.7, "$\overline{w}''$", fontsize = 12)

plt.text(5.2,-.7, "$w_1$", fontsize = 12)

plt.text(5.9,-.7, "$\overline{w}$", fontsize = 12)


#ax1.set_xlabel("w")

#ax1.set_ylabel("p")

plt.ylim(0,11)
plt.xlim(.5,7)
plt.plot(x1, y1, linewidth=2, color='black')
plt.plot(x2, y2, linewidth=2, color='black')
plt.plot(x3, y3, linewidth=2, color='black',linestyle='--')
plt.show()


# #### Uniform Price Scenario

# In[274]:


x1 = np.arange(0,10,1)
y1 = x1

ax1 = plt.axes()
x_axis = ax1.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax1.axes.get_yaxis()
y_axis.set_ticks([])


# Plot a simple line chart between two points (7, 8) and (42, 44)

plt.text(6.5,6, "$C^{'}(u)$", fontsize = 10)


plt.text(-1.5,4.5, '$\\theta p_{mc}$', fontsize = 12)
ax1.hlines(y=4.5,xmin=0, xmax=10, linewidth=2, color='black',linestyle='-')

###plot vertical lines for consumption
ax1.vlines(x=4.45, ymin=0, ymax=4.5, linewidth=2, color='black',linestyle='--')
plt.text(4.45,-.4, "u*", fontsize = 12)

###plot labels lines for consumption
plt.ylim(0,7)
plt.plot(x1, y1, linewidth=2, color='black')

plt.show()


# #### Costs sufficiently convex

# In[277]:


x1 = np.arange(0,10,1)
y1 = 2.5*x1

ax1 = plt.axes()
x_axis = ax1.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax1.axes.get_yaxis()
y_axis.set_ticks([])

## label cost curve
plt.text(2.75,6, "$C^{'}(u)$", fontsize = 10)

#label second price tier
plt.text(-1.5,4.5, '$\\theta p_{mc}$', fontsize = 12
        )
# draw horizontal line for second price tier
ax1.hlines(y=4.5,xmin=0, xmax=2, linewidth=2, color='black',linestyle='-')


#label first price tier
plt.text(-1.5,3, '$\\theta p_{1}$', fontsize = 12
        )
# draw horizontal line for first price tier
ax1.hlines(y=3,xmin=2, xmax=10, linewidth=2, color='black',linestyle='-')


###plot vertical line connecting two price tiers
ax1.vlines(x=2, ymin=3, ymax=4.5, linewidth=2, color='black',linestyle='--')


###plot vertical line for consumption star
ax1.vlines(x=1.8, ymin=0, ymax=4.5, linewidth=2, color='black',linestyle='--')
plt.text(1.8,-.4, "u*", fontsize = 12)

#plot
plt.ylim(0,7)

plt.plot(x1, y1, linewidth=2, color='black')

plt.show()


# #### benchmark

# In[271]:


x1 = np.arange(0,10,1)
y1 = x1

ax1 = plt.axes()
x_axis = ax1.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax1.axes.get_yaxis()
y_axis.set_ticks([])

## label cost curve
plt.text(6.5,6, "$C^{'}(u)$", fontsize = 10)

#label second price tier
plt.text(-1.5,4.5, '$\\theta p_{mc}$', fontsize = 12
        )
# draw horizontal line for second price tier
ax1.hlines(y=4.5,xmin=0, xmax=2, linewidth=2, color='black',linestyle='-')


#label first price tier
plt.text(-1.5,3, '$\\theta p_{1}$', fontsize = 12
        )
# draw horizontal line for first price tier
ax1.hlines(y=3,xmin=2, xmax=10, linewidth=2, color='black',linestyle='-')


###plot vertical line connecting two price tiers
ax1.vlines(x=2, ymin=3, ymax=4.5, linewidth=2, color='black',linestyle='--')


###plot vertical line for consumption star
ax1.vlines(x=3, ymin=0, ymax=3, linewidth=2, color='black',linestyle='--')
plt.text(3,-.4, "u*", fontsize = 12)

#plot

plt.ylim(0,7)

plt.plot(x1, y1, linewidth=2, color='black')

plt.show()


# In[272]:


x1 = np.arange(0,10,1)
y1 = x1

ax1 = plt.axes()
x_axis = ax1.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax1.axes.get_yaxis()
y_axis.set_ticks([])

## label cost curve
plt.text(6.5,6, "$C^{'}(u)$", fontsize = 10)

#label second price tier
plt.text(-1.5,4.5, '$\\theta p_{mc}$', fontsize = 12
        )
# draw horizontal line for second price tier
ax1.hlines(y=4.5,xmin=0, xmax=2, linewidth=2, color='black',linestyle='-')


#label first price tier
plt.text(-1.5,3, '$\\theta p_{1}$', fontsize = 12
        )
# draw horizontal line for first price tier
ax1.hlines(y=3,xmin=2, xmax=10, linewidth=2, color='black',linestyle='-')


###plot vertical line connecting two price tiers
ax1.vlines(x=2, ymin=3, ymax=4.5, linewidth=2, color='black',linestyle='--')


###plot vertical line for consumption star
ax1.vlines(x=3, ymin=0, ymax=3, linewidth=2, color='black',linestyle='--')
plt.text(3,-.4, "u*", fontsize = 12)

#plot

plt.ylim(0,7)

plt.plot(x1, y1, linewidth=2, color='black')

plt.show()


# #### Plot wbar really high

# In[273]:


x1 = np.arange(0,10,1)
y1 = x1

ax1 = plt.axes()
x_axis = ax1.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax1.axes.get_yaxis()
y_axis.set_ticks([])

## label cost curve
plt.text(6.5,6, "$C^{'}(u)$", fontsize = 10)

#label second price tier
plt.text(-1.5,4.5, '$\\theta p_{mc}$', fontsize = 12
        )
# draw horizontal line for second price tier
ax1.hlines(y=4.5,xmin=0, xmax=6, linewidth=2, color='black',linestyle='-')


#label first price tier
plt.text(-1.5,3, '$\\theta p_{1}$', fontsize = 12
        )
# draw horizontal line for first price tier
ax1.hlines(y=3,xmin=6, xmax=10, linewidth=2, color='black',linestyle='-')


###plot vertical line connecting two price tiers
ax1.vlines(x=6, ymin=3, ymax=4.5, linewidth=2, color='black',linestyle='--')


###plot vertical line for consumption star
ax1.vlines(x=4.5, ymin=0, ymax=4.5, linewidth=2, color='black',linestyle='--')
plt.text(4.3,-.4, "u*", fontsize = 12)

#plot

plt.ylim(0,7)

plt.plot(x1, y1, linewidth=2, color='black')

plt.show()


# In[ ]:




