import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, decimate, lfilter, detrend
from scipy.interpolate import interp1d

#

## documented in time tdms file
Fs = 25.6E3
dt = 1 / Fs
datap = 'F:\strukton_pro'

starti = int(2.5E6);
stopi = int(1E7)
timedat = pd.read_hdf(datap + 'Prorail17092808si12.time.h5', 'time', mode='r',start=starti,stop=stopi)
syncdat = pd.read_hdf(datap + 'Prorail17092808si12.time.h5', 'sync', mode='r');

Par = .002;
fnyq=Fs/2;                  
frel=Par/fnyq;             
Amp=1/(2*np.pi*Par);          
[B,A]=butter(1,frel);  
#B=1/2/Fs*np.array([1, 1]);A=np.array([1., -1.]);Amp=1;    
#velchab3=Amp*lfilter(B,A,detrend(timedat.CHA3));
#dispchab3=Amp*lfilter(B,A,detrend(velchab3));
velchab3=Amp*lfilter(B,A,(timedat.CHA3));
dispchab3=Amp*lfilter(B,A,(velchab3));

get_ext = interp1d(syncdat.IntCnt[2:-2],syncdat.ExtCnt[2:-2])
timedat.EXTCNT = get_ext(timedat.INTCNT)
newext = np.arange(np.ceil(timedat.EXTCNT[0]/10)*10,np.floor(timedat.EXTCNT[-1]/10)*10,10)
distsamp = interp1d(timedat.EXTCNT,dispchab3)
newdisp = distsamp(newext)

fsd = 100;
fnd = fsd/2;
b, a = butter(4, [1/3/fnd, 1/1/fnd], btype='band')

D0 = lfilter(b,a,newdisp)

b, a = butter(4, [1/25/(fnd/4), 1/3/(fnd/4)], btype='band')
D1 = lfilter(b,a,decimate(newdisp,4,zero_phase=True));

b, a = butter(4, [1/70/(fnd/20), 1/25/(fnd/20)], btype='band')
D2 = lfilter(b,a,decimate(decimate(newdisp,4,zero_phase=True),5,zero_phase=True));

fig = plt.figure(1,figsize=(8,5))
plt.clf()
plt.plot(newext,newdisp)
#plt.plot(newext,D0)
#plt.plot(newext[::4],D1)
#plt.plot(newext[::20],D2)


fig = plt.figure(3,figsize=(8,5))
plt.clf()
#plt.plot(newext,newdisp)
plt.plot(newext,D0)
plt.plot(newext[::4],D1)
#plt.plot(newext[::20],D2)
plt.axvline(45276459, color='green') 
plt.axvline(45346879, color='green') 
plt.axvline(45379059, color='green') 
plt.axvline(45379059, color='green') 

fig = plt.figure(4,figsize=(8,5))
plt.clf()
#plt.plot(newext,newdisp)
#plt.plot(newext,D0)
#plt.plot(newext[::4],D1)
plt.plot(newext[::20],D2)