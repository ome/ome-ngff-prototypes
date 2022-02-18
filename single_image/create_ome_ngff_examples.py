import argparse
import json
import os

import h5py
import numpy as np


def _kwargs_2d():
    return {"scale": (0.5, 0.5), "order": 0, "preserve_range": True}


def _kwargs_3d():
    return {"scale": (0.5, 0.5, 0.5), "order": 0, "preserve_range": True}


def _create_examples(writer, root):
    os.makedirs(root, exist_ok=True)

    with open("./example_data/voxel_sizes.json") as f:
        voxel_sizes = json.load(f)

    def create(path, axes, bb=np.s_[:],
               voxel_size=None, unit=None,
               time_scale=None, time_unit=None,
               prefix=None, ax_name=None, out_path=None):
        ax_name = "".join(axes) if ax_name is None else ax_name
        out_path = os.path.join(root, f"{ax_name}.ome.zarr") if out_path is None else out_path
        print("Create", out_path)
        if os.path.exists(out_path) and prefix is None:
            print("Example data at", out_path, "is already present")
            return
        with h5py.File(path, "r") as f:
            data = f["data"][bb]
        assert data.ndim == len(axes)
        kwargs = _kwargs_3d() if axes[-3:] == ("z", "y", "x") else _kwargs_2d()
        if unit is None and time_unit is None:
            units = None
        else:
            units = []
            for ax in axes:
                ax_unit = None
                if ax in ("z", "y", "x"):
                    ax_unit = unit
                elif ax == "t":
                    ax_unit = time_unit
                units.append(ax_unit)
        writer(
            data, out_path, axes, ax_name,
            n_scales=3, kwargs=kwargs, scale=voxel_size, units=units, time_scale=time_scale,
            prefix=prefix
        )

    # yx example data
    create("./example_data/image_with_channels.h5", ("y", "x"), np.s_[0])
    # cyx example data
    create("./example_data/image_with_channels.h5", ("c", "y", "x"))

    # zyx example data
    voxel_size = voxel_sizes["volume"]["voxel_size"]
    unit = voxel_sizes["volume"]["unit"]
    create("./example_data/volume.h5", ("z", "y", "x"), unit=unit, voxel_size=voxel_size)

    # tyx example data
    voxel_size = voxel_sizes["timeseries_with_channels"]["voxel_size"]
    unit = voxel_sizes["timeseries_with_channels"]["unit"]
    create("./example_data/timeseries_with_channels.h5", ("t", "y", "x"), np.s_[:, 0, 200],
           unit=unit, voxel_size=voxel_size, time_unit="second", time_scale=10)
    # tcyx example data
    create("./example_data/timeseries_with_channels.h5", ("t", "c", "y", "x"), np.s_[:, :, 200],
           unit=unit, voxel_size=voxel_size, time_unit="second", time_scale=10)
    # tczyx example data
    create("./example_data/timeseries_with_channels.h5", ("t", "c", "z", "y", "x"),
           unit=unit, voxel_size=voxel_size, time_unit="second", time_scale=10)

    # this is not supported in the 0.3 code yet
    if "0.3" in root:
        return
    # create example with multiple images
    path = "./example_data/image_with_channels.h5"
    with h5py.File(path, "r") as f:
        n_channels = f["data"].shape[0]
    out_path = os.path.join(root, "multi-image.ome.zarr")
    for chan in range(n_channels):
        name = f"image-{chan}"
        create(path, ("y", "x"), np.s_[chan], ax_name=name, out_path=out_path, prefix=name)


def create_v03():
    from prototypes.v03 import write_ome_zarr
    root = "v0.3"
    _create_examples(write_ome_zarr, root)


def create_v04():
    from prototypes.v04 import write_ome_zarr
    root = "v0.4"
    _create_examples(write_ome_zarr, root)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", type=str)
    args = parser.parse_args()
    version = args.version.lstrip("v")
    if version == "0.3":
        create_v03()
    elif version == "0.4":
        create_v04()
    else:
        raise ValueError(f"Invalid version: {args.version}")


if __name__ == "__main__":
    main()
