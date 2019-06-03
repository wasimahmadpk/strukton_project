import pywt
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import chirp

# Define signal
fs = 128.0
sampling_period = 1 / fs
t = np.linspace(0, 2, 2 * fs)
x = chirp(t, 10, 2, 40, 'quadratic')

# Calculate continuous wavelet transform
coef, freqs = pywt.cwt(x, np.arange(1, 50), 'morl',
                       sampling_period=sampling_period)

# Show w.r.t. time and frequency
plt.figure(figsize=(5, 2))
plt.subplot(2, 1, 1)
plt.pcolor(t, freqs, coef)

# Set yscale, ylim and labels
plt.yscale('log')
plt.ylim([1, 100])
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (sec)')

plt.subplot(2, 1, 2)
plt.plot(t, x)
plt.show()