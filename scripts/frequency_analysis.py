import os

import matplotlib.pyplot as plt
import numpy as np
import pywt


# Defaults match the original Semi-otic Labs checkout; override with env vars.
_HEALTHY = os.environ.get(
    "STRUKTON_HEALTHY_NPY", r"C:/Users/Waseem/Desktop/Semiotic Labs/healthy.npy"
)
_FAULTY = os.environ.get(
    "STRUKTON_FAULTY_NPY", r"C:/Users/Waseem/Desktop/Semiotic Labs/bb_data.npy"
)
_FIG_DIR = os.environ.get(
    "STRUKTON_FIGURES", r"C:\Users\Waseem\Desktop\Semiotic Labs"
)

fs = 22050.0
sampling_period = 1 / fs
t = np.linspace(0, 5, int(5 * fs))
xhealthy = None
xfaulty = None


def plot_fourier(data, fs):
    n = len(data)
    k = np.arange(n)
    T = n / fs
    frq = k / T
    frq = frq[range(int(n / 2))]

    Y = np.fft.fft(data) / n
    Y = Y[range(int(n / 2))]

    plt.figure()
    plt.plot(frq, abs(Y), "b")
    plt.xlabel("Freq (Hz)")
    plt.ylabel("|Y(freq)|")
    plt.show()
    plt.savefig(os.path.join(_FIG_DIR, "fourier_analysis.png"), dpi=150)


def plot_specgram(data, title="", x_label="", y_label="", fig_size=None):
    fig = plt.figure()
    if fig_size != None:
        fig.set_size_inches(fig_size[0], fig_size[1])
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    pxx, freq, tt, cax = plt.specgram(data, Fs=fs)
    fig.colorbar(cax).set_label("Intensity [dB]")


def plot_wavelet(data, scale, wavelet, sampling_period):
    coef, freqs = pywt.cwt(xhealthy, scale, wavelet, sampling_period=sampling_period)

    print(t.shape, xhealthy.shape, coef.shape, freqs.shape)

    plt.figure()
    plt.pcolor(t, freqs, coef)
    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (sec)")
    plt.show()
    plt.savefig(os.path.join(_FIG_DIR, "wavelet_analysis.png"), dpi=150)


def main():
    global xhealthy, xfaulty
    healthy_data = np.load(_HEALTHY)
    faulty_data = np.load(_FAULTY)

    print("Shape of healthy dataset: ", np.shape(healthy_data))
    print("Shape of faulty dataset: ", np.shape(faulty_data))

    xhealthy = healthy_data[0:110250, 1]
    xfaulty = faulty_data[0:110250, 1]

    plot_fourier(xhealthy, fs)
    plot_fourier(xfaulty, fs)
    plot_specgram(xhealthy, title="Spectrogram", x_label="time (in seconds)", y_label="frequency", fig_size=(14, 8))
    plot_specgram(xfaulty, title="Spectrogram", x_label="time (in seconds)", y_label="frequency", fig_size=(14, 8))
    plot_wavelet(xhealthy, np.arange(1, 15), "gaus1", sampling_period)
    plot_wavelet(xfaulty, np.arange(1, 15), "gaus1", sampling_period)


if __name__ == "__main__":
    main()
