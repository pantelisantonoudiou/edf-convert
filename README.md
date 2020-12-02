# edf-convert
Conversion of edf files to csv or h5 format

---
## How to use
    python edf_convert.py
    
---
### :snake: Dependencies

- [numpy](https://numpy.org/)
- [scipy](https://www.scipy.org/)
- [pytables](https://www.pytables.org/)
- [pyedflib](https://pyedflib.readthedocs.io/en/latest/)
- [tqdm](https://github.com/tqdm/tqdm)

---
## Configuration settings

    - win : window size in seconds, Default = 5
    - fs : sampling rate (samples per second), Default = 2000
    - new_fs : sampling rate after decimation (samples per second), Default = 100
    - scale : signal scaling factor, Default = 1

