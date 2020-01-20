import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import base64
import threading
import datetime
#use different dataset  depending
#on the locindex variable
def multi_line(locindex,client ):
   # changed the background of the graph

   fig = plt.figure()
   plt.ioff()
   ax = fig.add_subplot(1, 1, 1)
   ax.set(xlabel='Time (Hrs)', ylabel='Sunlight (kWh/sq m)',
       title="Andy's Graph")


   # creates graph template

   def create_random_walk():
       x = np.random.choice([-0.05, .1], size=100, replace=True)  # Sample with replacement from (-1, 1)
       return np.cumsum(x)  # Return the cumulative sum of the elements


   X = create_random_walk()
   Y = create_random_walk()
   Z = create_random_walk()

   # function to make graph animate
   # ani = animation.FuncAnimation(fig, animate, interval = 1000)

   plt.plot(X)
   plt.plot(Y)
   plt.plot(Z)

   buf = io.BytesIO()
   plt.gcf().savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   #uri = 'data:image/png;base64,' + urllib.parse.quote(string)
   #html = '<img src = "%s"/>' % uri
   plt.close()
   return string

   
#use different dataset  depending
#on the locindex variable
def water_line(locindex,client):
   # changed the background of the graph
   fig, ax = plt.subplots()
   ax.set(xlabel='Time (Hr:Min)', ylabel='Water level(cm)', title="Water Level")
   lock = threading.Lock()
   X= []
   Y = []
   lock.acquire()
   for block in client[locindex].chain.chain:
           X.append(block.sensor.water_level)
           Y.append(datetime.datetime.strptime(block.remote_time, "%m-%d-%Y:%H-%M-%S"))
   data = { 'level' : X,
                 'time'  : Y }
   plt.ioff()
   buf = io.BytesIO()
   df = pd.DataFrame(data)
   df.groupby(pd.Grouper(key='time', freq="min")).mean().plot(ax = ax, rot=0,  figsize=(15,10), fontsize=12)
   plt.savefig(buf, format='png')
   buf.seek(0)
   string = base64.b64encode(buf.read())
   #uri = 'data:image/png;base64,' + urllib.parse.quote(string)
   #html = '<img src = "%s"/>' % uri
   
   plt.close()
   lock.release()
   return string
'''def battery_life()
   battery = 12.4 - client[locindex].chain.chain[-1].v_battery
   if battery >12.4 :
        good
   if battery >12.4*.96 :
         green
   if battery >12.4*.92 :
       green
   if battery >12.4*.88 :
       yellow
   if battery >12.4*.84 :
       yellow
   if battery >12.4*.80 :
       red
   return
'''
if __name__ == "__main__":
   multi_line(1) 
