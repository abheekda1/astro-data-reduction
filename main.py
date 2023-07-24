from astropy.io import fits
import numpy as np
import os
import matplotlib.pyplot as plt

DARKS_DIR = "darks"
LIGHTS_DIR = "lights"
FLATS_DIR = "flats"
MASTER_DIR = "master"
DARKSFORFLATS_DIR = "darks_for_flats"
REDUCED_DIR = "reduced"

def list_files(dir) -> list[str]:
    return [f"{dir}/{f}" for f in os.listdir(dir) if not f.split('/')[-1].startswith('.')]

def gen_median(files) -> np.ndarray:
    darks = list(map(lambda x: fits.getdata(x), files))
    mdark = np.median(darks, axis=0)

    return mdark

def gen_mflat(dark_for_flats_files, flat_files) -> tuple[np.ndarray, np.float64]:
    mdark_for_flats = gen_median(dark_for_flats_files)
    unnorm_mflat = gen_median(flat_files)

    unnorm_mflat -= mdark_for_flats
    avg_flat_val = np.mean(unnorm_mflat, dtype=np.float64)

    return (unnorm_mflat, avg_flat_val)


def main() -> int:
    for folder in [DARKS_DIR, LIGHTS_DIR, FLATS_DIR, MASTER_DIR, REDUCED_DIR]:
        os.makedirs(folder, exist_ok=True)

    dark_files = list_files(DARKS_DIR)

    if len(dark_files) == 0:
        return 1
    
    mdark = gen_median(dark_files)
    fits.writeto(f"{MASTER_DIR}/mdark.fits", mdark, overwrite=True)

    
    dark_for_flat_files = list_files(DARKSFORFLATS_DIR)
    flat_files = list_files(FLATS_DIR)

    unnorm_mflat, avg_flat_val = gen_mflat(dark_for_flat_files, flat_files)
    fits.writeto(f"{MASTER_DIR}/mflat.fits", unnorm_mflat, overwrite=True)

    norm_mflat = unnorm_mflat / avg_flat_val
    light_files = list_files(LIGHTS_DIR)
    for file in light_files:
        fdata, _ = fits.getdata(file, header=True)
        # plt.imshow(fdata, cmap='gray', vmin=1850, vmax=1950)
        # plt.colorbar()
        # plt.show()
        reduced = (fdata - mdark) / norm_mflat
        # plt.imshow(reduced, cmap='gray', vmin=850, vmax=950)
        # plt.colorbar()
        # plt.show()
        fits.writeto(f"{REDUCED_DIR}/{file[file.find('/')+1:file.find('.')]}.red.fits", reduced, overwrite=True)
        print(f"FINISHED REDUCING TO {REDUCED_DIR}/{file[file.find('/')+1:file.find('.')]}.red.fits")

    print("IMAGES HAVE BEEN REDUCED\nPLEASE PRESS ENTER TO CONTINUE:")
    input()

    return 0

if __name__ == "__main__":
    exit(main())
