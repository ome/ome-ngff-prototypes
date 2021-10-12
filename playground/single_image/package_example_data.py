import json
import os

import imageio
import h5py
import numpy as np
import zarr


# collect the example data from the kreshuk lab and convert it to tifs
# to collect all example data in the same format and prepare for packaging it
def package_examples():
    os.makedirs("./example_data", exist_ok=True)
    metadata = {}

    def to_h5(data, name):
        out_path = f"./example_data/{name}"
        with h5py.File(out_path, mode="w") as f:
            f.create_dataset("data", data=data, compression="gzip")

    # example data for cyx, yx
    path = os.path.join("/g/kreshuk/data/covid/covid-data-vibor/20200405_test_images",
                        "WellC01_PointC01_0000_ChannelDAPI,WF_GFP,TRITC,WF_Cy5_Seq0216.tiff")
    data = imageio.volread(path)
    to_h5(data, "image_with_channels.h5")
    metadata["image_with_channels"] = {"voxel_size": None, "unit": None}

    # example data for zyx
    path = os.path.join("/g/kreshuk/pape/Work/mobie/covid-em-datasets/data",
                        "Covid19-S4-Area2/images/local/sbem-6dpf-1-whole-raw.n5")
    key = "setup0/timepoint0/s3"
    with zarr.open(path, mode="r") as f:
        data = f[key][:]
    to_h5(data, "volume.h5")
    # original voxel size is 8 nm (isotropic) and we use scale 3 (downsampled by 2^3 = 8)
    # -> voxel size is 64 nm
    metadata["volume"] = {"voxel_size": {"z": 64.0, "y": 64.0, "x": 64.0}, "unit": "nanometer"}

    # example data for tyx, tcyx, tczyx
    path1 = "/g/kreshuk/pape/Work/mobie/arabidopsis-root-lm-datasets/data/arabidopsis-root/images/local/lm-membranes.n5"
    path2 = "/g/kreshuk/pape/Work/mobie/arabidopsis-root-lm-datasets/data/arabidopsis-root/images/local/lm-nuclei.n5"
    timepoints = [32, 33, 34]
    data = []
    for tp in timepoints:
        key = f"setup0/timepoint{tp}/s2"
        with zarr.open(path1, mode="r") as f:
            d1 = f[key][:]
        with zarr.open(path2, mode="r") as f:
            d2 = f[key][:]
        data.append(np.concatenate([d1[None], d2[None]], axis=0)[None])
    data = np.concatenate(data, axis=0)
    to_h5(data, "timeseries_with_channels.h5")
    # original voxel size is 0.25 x 0.1625 x 0.1625 micrometer and we use cale 2 (downsampled by 2^2=4)
    metadata["timeseries_with_channels"] = {"voxel_size": {"z": 1.0, "y": 0.65, "x": 0.65}, "unit": "micrometer"}

    with open("./example_data/voxel_sizes.json", "w") as f:
        json.dump(metadata, f)


if __name__ == "__main__":
    package_examples()
