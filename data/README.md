# Measurement data

ABA HDF5 files, SEG/POI route CSVs, and track images are not stored in git.

Place a local copy of a measurement here, for example:

```
data/
  Groningen/
    Prorail17112805si12/
      ABA/...
    Routefile/
      Prorail17112805si12_seg.csv
      Prorail17112805si12_poi.csv
```

Then point the pipeline at it:

```bash
export STRUKTON_DATA_ROOT="$PWD/data/Groningen"
export STRUKTON_COUNTERS="$PWD/data/Groningen/Prorail17112805si12/ABA/Prorail17112805si12/counter_data"
```
