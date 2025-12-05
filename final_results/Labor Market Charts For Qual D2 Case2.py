#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


# ##### Case 1

# In[9]:


fig, ax = plt.subplots(1, 1,figsize=(6.5,5))
####plot demand 
#####################
xs=np.array([1,2,3,4,5])
ys=np.array([108,55,28,13,6.25])+8

model=make_interp_spline(xs, ys)
xss=np.linspace(1,5,500)
yss=model(xss)
plt.plot(xss, yss,color='black',linestyle='-')

####plot skilled demand shift
###############

x=np.array([1.0,2.0,3.0,4.0,5.0])
y=np.array([100,50,25,12.5,6.25])

model=make_interp_spline(x, y)
xs=np.linspace(1,5,500)
ys=model(xs)
plt.plot(xs, ys,color='blue',linestyle="--",label='Demand Shift: Skilled Exit')

####plot unskilled demand shift
###############
x=np.array([1.0,2.0,3.0,4.0,5.0])
y=np.array([99,49,25,12.5,6.25])-7.5

model=make_interp_spline(x, y)
xs=np.linspace(1,5,500)
ys=model(xs)
plt.plot(xs, ys,color='orange',linestyle="--",label='Demand Shift: Unskilled Exit')


####draw supply + supply shift
#####################
##new supply
ax.vlines(x=1.3, ymin=0, ymax=135, linewidth=1, color='black',linestyle="--")
###old supply
ax.vlines(x=2, ymin=0, ymax=135, linewidth=1, color='black',linestyle="-")


##label supply
plt.text(1.2,-14, '$S^{I}_{sk}$', fontsize = 10)
plt.text(1.9,-14, '$S_{sk}$', fontsize = 10)

##label demand
plt.text(4.7,18, '$D_{sk}$', fontsize = 10)

######draw price lines

####old price

ax.hlines(y=73, xmin=.8, xmax=1.3, linewidth=1, color='black',linestyle="--")
plt.text(0.6,74, '$P^{I}_{sk}$', fontsize = 10)

###new price
ax.hlines(y=64, xmin=.8, xmax=2, linewidth=1, color='black',linestyle="--")
plt.text(0.6,64, '$P_{sk}$', fontsize = 10)

#####title and axes
plt.title("Skilled Labor Market")
plt.xlabel("Skilled Labor",loc='right')
plt.ylabel(r"$Pl_{sk}$",loc='top',rotation=0)

x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])

plt.margins(x=0)
plt.legend()
plt.show()



# In[14]:


fig, ax = plt.subplots(1, 1,figsize=(6.5,5))
####plot demand 
#####################
xs=np.array([1,2,3,4,5])
ys=np.array([108,55,28,13,6.25])+8

model=make_interp_spline(xs, ys)
xss=np.linspace(1,5,500)
yss=model(xss)
plt.plot(xss, yss,color='black',linestyle='-')

####plot skilled demand shift
###############

x=np.array([1.0,2.0,3.0,4.0,5.0])
y=np.array([100,50,25,12.5,6.25])

model=make_interp_spline(x, y)
xs=np.linspace(1,5,500)
ys=model(xs)
plt.plot(xs, ys,color='blue',linestyle="--",label='Demand Shift: Skilled Exit')

####plot unskilled demand shift
###############
x=np.array([1.0,2.0,3.0,4.0,5.0])
y=np.array([99,49,25,12.5,6.25])-7.5

model=make_interp_spline(x, y)
xs=np.linspace(1,5,500)
ys=model(xs)
plt.plot(xs, ys,color='orange',linestyle="--",label='Demand Shift: Unskilled Exit')


####draw supply + supply shift
#####################
ax.vlines(x=1.1, ymin=0, ymax=135, linewidth=1, color='black',linestyle="--")
ax.vlines(x=2, ymin=0, ymax=135, linewidth=1, color='black',linestyle="-")


##label supply
plt.text(1.1,-14, '$S^{I}_{unsk}$', fontsize = 10)
plt.text(2,-14, '$S_{unsk}$', fontsize = 10)

##label demand
plt.text(4.7,18, '$D_{unsk}$', fontsize = 10)

######draw price lines

####new price

ax.hlines(y=85, xmin=.8, xmax=1.1, linewidth=1.1, color='black',linestyle="--")
plt.text(0.5,85, '$P^{I}_{unsk}$', fontsize = 10)

###old price
ax.hlines(y=64, xmin=.8, xmax=2, linewidth=1, color='black',linestyle="--")
plt.text(0.5,64, '$P_{unsk}$', fontsize = 10)

#####title and axes
plt.title("Unskilled Labor Market")
plt.xlabel("Unskilled Labor",loc='right')
plt.ylabel(r"$Pl_{unsk}$",loc='top',rotation=0)

x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])

plt.margins(x=0)
plt.legend()
plt.show()



# In[523]:


get_ipython().run_line_magic('pinfo', 'plt.ylabel')


# In[325]:


###plot isoquants
fig, ax = plt.subplots(1, 1,figsize=(7,5))

x1=np.array([1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7])
x2=np.array([1,1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4])
y1=-x1**(2.5)
y2=-x2**(3)

plt.plot(x1, y1,color='black')
plt.plot(x2, y2,color='black')

plt.title("Autarky")
plt.xlabel("Good 1 (Skill Intensive)")
plt.ylabel("Good 2 (Unkkilled Intensive)")

plt.ylim(-49,10)
plt.xlim(1,6)

####plot price lines

#shallow price line
px1 = np.arange(1.5,4.6,1)
py1 = 19-(11.5*px1)
plt.plot(px1, py1,color='black',linewidth=.9)

#steep price line
px1 = np.arange(1.5,4.4,1)
py1 = 31-18.5*px1
plt.plot(px1, py1,color='black',linewidth=.9)



####plot labels 

plt.plot([2.5], [-15.2], marker="o", markersize=5, markeredgecolor="black", markerfacecolor="black")
plt.plot([2.7], [-12], marker="o", markersize=5, markeredgecolor="black", markerfacecolor="black")

####plot text

plt.text(2.5,-15.2, '$A^{1}_{a}$', fontsize = 10)
plt.text(2.7,-12, '$A^{2}_{a}$', fontsize = 10)

plt.text(3.4,-48, '$R^{1}$', fontsize = 10)
plt.text(4.7,-48, '$R^{2}$', fontsize = 10)

plt.text(3.6,-36, '$P^1_{1}/P^1_{2}$', fontsize = 10)
plt.text(4.4,-31, '$P^2_{1}/P^2_{2}$', fontsize = 10)

###formatting axes
x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])
plt.show()


# In[450]:


###plot isoquants
fig, ax = plt.subplots(1, 1,figsize=(7,5))

x1=np.array([1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7])
x2=np.array([1,1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75,4])
y1=-x1**(2.5)
y2=-x2**(3)

plt.plot(x1, y1,color='black')
plt.plot(x2, y2,color='black')

plt.title("Autarky")
plt.xlabel("Good 1 (Skill Intensive)")
plt.ylabel("Good 2 (Unkkilled Intensive)")

plt.ylim(-49,10)
plt.xlim(1,6)

####plot price lines

#shallow price line
px1 = np.arange(1.5,5,1)
py1 = 30-(15*px1)
plt.plot(px1, py1,color='red',linewidth=.9)

#steep price line
px1 = np.arange(1.5,4.500001,1)
py1 = 24-15.4*px1
plt.plot(px1, py1,color='red',linewidth=.9)



####plot production markers 

plt.plot([2.2], [-10.7], marker="o", markersize=4, markeredgecolor="red", markerfacecolor="red")
plt.plot([3.25], [-15], marker="o", markersize=4, markeredgecolor="red", markerfacecolor="red")

####plot consumption markers 

plt.plot([2.2], [-3], marker="o", markersize=4, markeredgecolor="red", markerfacecolor="red")
plt.plot([3.25], [-26], marker="o", markersize=4, markeredgecolor="red", markerfacecolor="red")

####plot old markers

plt.plot([2.46], [-15.2], marker="o", markersize=4, markeredgecolor="black", markerfacecolor="black")
plt.plot([2.7], [-12], marker="o", markersize=4, markeredgecolor="black", markerfacecolor="black")
####plot text

####old autarkey labels
plt.text(2.2,-16.2, '$A^{1}_{a}$', fontsize = 9)
plt.text(2.7,-12, '$A^{2}_{a}$', fontsize = 9)


####plot production labels
plt.text(2,-12.2, '$B^{1}_{t}$', fontsize = 10,color='red')
plt.text(3.3,-20, '$B^{2}_{t}$', fontsize = 10,color='red')

####plot consumption labels
plt.text(2,-5, '$C^{2}_{t}$', fontsize = 10,color='red')
plt.text(3.1,-29, '$C^{1}_{t}$', fontsize = 10,color='red')

####plot ppf labels
plt.text(3.4,-48, '$R^{1}$', fontsize = 10)
plt.text(4.7,-48, '$R^{2}$', fontsize = 10)

plt.text(3.9,-44, '$P^1_{1}/P^1_{2}$', fontsize = 10)
plt.text(4.3,-33, '$P^2_{1}/P^2_{2}$', fontsize = 10)

###plot dotted lines
#r1
ax.vlines(x=2.2, ymin=-26, ymax=-12.2, linewidth=1, color='red',linestyle='--')
ax.hlines(y=-26, xmin=2.2, xmax=3.2, linewidth=1, color='red',linestyle='--')

#r2
ax.vlines(x=2.2, ymin=-19, ymax=-3, linewidth=1, color='red',linestyle='--')
ax.hlines(y=-19, xmin=2.2, xmax=3.2, linewidth=1, color='red',linestyle='--')

###formatting axes
x_axis = ax.axes.get_xaxis()
x_axis.set_ticks([])

y_axis = ax.axes.get_yaxis()
y_axis.set_ticks([])
plt.show()


# In[73]:





# In[199]:


plt.arrow(5, 3, .75,0,head_width=.15)


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




