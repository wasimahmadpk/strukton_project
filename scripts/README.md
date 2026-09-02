# Standalone analysis scripts

These scripts were used for camera overlay, labelled-image scoring, and
eddy-current / ultrasonic plots. They read measurement files from local
disks (or the paths in each script) and are not imported by the main
`railai` pipeline.

| Script | Purpose |
| --- | --- |
| `spot_anomaly.py` | draw detections on track images |
| `performance.py` | hit / false-alarm counts vs XML labels |
| `frequency_analysis.py` | FFT / spectrogram / wavelet examples |
| `ectdata.py` | eddy-current crack evolution plots |
| `ustdata.py` | ultrasonic inspection plots |
| `train_tonnage.py` | train load / speed summaries |
| `zedf.py` | ZOES `.ze` file helper |

Run from the repository root, for example:

```bash
python scripts/performance.py
```
