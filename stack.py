import numpy as np
from astropy.io import fits
import os

def gen_median(files) -> np.ndarray:
    datas = list(map(lambda x: fits.getdata(x), files))
    median = np.median(datas, axis=0)

    return median

os.makedirs("median", exist_ok=True)
for i in ['b', 'r', 'v']:
    files = [f"reduced/{filename}" for filename in os.listdir("reduced") if filename.endswith(f"{i}.red.fits")]
    fits.writeto(f"median/{i}.fits", gen_median(files))
