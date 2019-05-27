import numpy as np
import pywt
from scipy.signal import chirp
import matplotlib.pyplot as plt

healthy_data = np.load('C:/Users/Waseem/Desktop/Semiotic Labs/healthy.npy')
faulty_data = np.load('C:/Users/Waseem/Desktop/Semiotic Labs/bb_data.npy')

print("Shape of healthy dataset: ", np.shape(healthy_data))
print("Shape of faulty dataset: ", np.shape(faulty_data))

# plt.subplot(2,1,1)
# plt.ylabel('Amp')
# plt.plot(healthy_data)
# plt.subplot(2,1,2)
# plt.ylabel('Amp')
# plt.plot(faulty_data)
# plt.xlabel('Time')
# plt.show()

# Define signal
fs = 22050.0                               # sampling rate
sampling_period = 1 / fs                   # sampling interval
t = np.linspace(0, 5, 5 * fs)              # time vector
xhealthy = healthy_data[0:110250, 1]       # vibration signal from healthy bearings
xfaulty = faulty_data[0:110250, 1]         # vibration signal from faulty bearings


# fast fourier transform
def plot_fourier(data, fs):
    n = len(data)            # length of the signal
    k = np.arange(n)
    T = n/fs
    frq = k/T                    # two sides frequency range
    frq = frq[range(int(n/2))]   # one side frequency range

    Y = np.fft.fft(data)/n   # fft computing and normalization
    Y = Y[range(int(n/2))]

    plt.figure()
    # plt.plot(t, xhealthy)
    plt.plot(frq, abs(Y), 'b')   # plotting the spectrum for healthy bearings
    # plt.xlabel('Time')
    # plt.ylabel('Amplitude')
    plt.xlabel('Freq (Hz)')
    plt.ylabel('|Y(freq)|')
    plt.show()
    plt.savefig(r'C:\Users\Waseem\Desktop\Semiotic Labs\fourier_analysis.png', dpi=150)
# ////////////////////////////////////////////////////////////////////

# Plot spectrogram of both the signals


def plot_specgram(data, title='', x_label='', y_label='', fig_size=None):
    fig = plt.figure()
    if fig_size != None:
        fig.set_size_inches(fig_size[0], fig_size[1])
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    pxx,  freq, tt, cax = plt.specgram(data, Fs=fs)
    fig.colorbar(cax).set_label('Intensity [dB]')

# # Calculate continuous wavelet transform


def plot_wavelet(data, scale, wavelet, sampling_period):

    coef, freqs = pywt.cwt(xhealthy, scale, wavelet,  #'morl'
                           sampling_period=sampling_period)

    print(t.shape, xhealthy.shape, coef.shape, freqs.shape)

    # Show w.r.t. time and frequency
    plt.figure()
    plt.pcolor(t, freqs, coef)

    # Set yscale, ylim and labels
    # plt.yscale('log')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (sec)')
    plt.show()
    plt.savefig(r'C:\Users\Waseem\Desktop\Semiotic Labs\wavelet_analysis.png', dpi=150)

# ////////////////////////////////////////


plot_fourier(xhealthy, fs)
plot_fourier(xfaulty, fs)

plot_specgram(xhealthy, title='Spectrogram', x_label='time (in seconds)', y_label='frequency', fig_size=(14, 8))
plot_specgram(xfaulty, title='Spectrogram', x_label='time (in seconds)', y_label='frequency', fig_size=(14, 8))

plot_wavelet(xhealthy, np.arange(1, 15), 'gaus1', sampling_period)
plot_wavelet(xfaulty, np.arange(1, 15), 'gaus1', sampling_period)