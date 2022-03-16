import argparse
import os
from glob import glob

import imageio
import ome_zarr
import ome_zarr.scale
import ome_zarr.writer
import zarr
from tqdm import tqdm


def write_as_ome_zarr(mip, group, resolution, units, axis_names, name):

    # specify the scale metadata (it would be nice to determine this dynamically, but for now we hard-code it
    is_scaled = {"c": False, "z": False, "y": True, "x": True}
    trafos = [
        [{
            "scale": [resolution[ax] * 2**scale_level if is_scaled[ax] else resolution[ax] for ax in axis_names],
            "type": "scale"
        }]
        for scale_level in range(len(mip))
    ]

    axes = []
    for ax in axis_names:
        axis = {"name": ax, "type": "channel" if ax == "c" else "space"}
        unit = units.get(ax, None)
        if unit is not None:
            axis["unit"] = unit
        axes.append(axis)

    # provide additional storage options for zarr
    chunks = (1, 1, 512, 512) if len(axes) == 4 else (1, 512, 512)
    assert len(chunks) == len(axis_names)
    storage_opts = {"chunks": chunks}
    assert mip[0].ndim == len(axes), f"{mip[0].shape}, {len(axes)}"

    # write the data to ome.zarr
    ome_zarr.writer.write_multiscale(
        mip, group, axes=axes,
        coordinate_transformations=trafos, storage_options=storage_opts,
    )
    # this should be supported by wrte_multiscale, see
    # https://github.com/ome/ome-zarr-py/issues/176
    multiscales = group.attrs["multiscales"]
    multiscales[0]["name"] = name
    group.attrs["multiscales"] = multiscales


def convert_image_data(in_path, group, resolution, units, name):
    # load the input data from ome.tif
    vol = imageio.volread(in_path)

    # the data is stored as 'zcyx'. This is currently not allowed by ome.zarr, so we reorder to 'czyx'
    vol = vol.transpose((1, 0, 2, 3))

    # create scale pyramid
    # how do we set options for the scaling?
    # (in this case the defaults are fine, but it should be possible to over-ride this in general)
    scaler = ome_zarr.scale.Scaler()
    mip = scaler.local_mean(vol)

    # specify the axis metadata
    axis_names = tuple("czyx")
    write_as_ome_zarr(mip, group, resolution, units, axis_names, name)


def convert_label_data(in_path, group, resolution, units, label_name, colors=None):
    # load the input data from ome.tif
    vol = imageio.volread(in_path)
    if vol.ndim != 3:
        print("Labels have unexpected shape", vol.shape, "for", in_path, label_name)
        print("Adding these labels will be skipped")
        return

    # create scale pyramid
    scaler = ome_zarr.scale.Scaler()
    mip = scaler.nearest(vol)

    # specify the axis metadata
    axis_names = tuple("zyx")
    write_as_ome_zarr(mip, group, resolution, units, axis_names, name=label_name)

    # there should be convenience functions for adding labels instead, that takes care of this, see
    # https://github.com/ome/ome-zarr-py/issues/171
    group.attrs["labels"] = label_name
    label_metadata = {"source": {"image": "../.."}}
    if colors is not None:
        label_metadata["colors"] = colors
    group.attrs["image_label"] = label_metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", "-i", default="./example_data")
    parser.add_argument("--output_folder", "-o", default="./data")
    parser.add_argument("--embryo", default="embryo3")
    args = parser.parse_args()

    input_folder, output_folder = args.input_folder, args.output_folder
    input_folders = [os.path.join(input_folder, name) for name in ("images", "cells", "nuclei")]
    assert all(os.path.exists(folder) for folder in input_folders)
    image_folder, cell_folder, nucleus_folder = input_folders
    embryo = args.embryo
    assert embryo in ("embryo1_embryo2", "embryo3"), embryo

    os.makedirs(output_folder, exist_ok=True)
    images = glob(os.path.join(image_folder, "*.ome.tif"))

    # the xy-resolution is different for the two embryos
    if embryo == "embryo3":
        resolution = {"c": 1.0, "z": 4.0, "y": 0.17, "x": 0.17}
    else:
        resolution = {"c": 1.0, "z": 4.0, "y": 0.11, "x": 0.11}

    # the labels are downsampled by a factor of 4 in xy
    label_resolution = {ax: res * 4 if ax in "xy" else res for ax, res in resolution.items()}
    units = {"c": None, "z": "micrometer", "y": "micrometer", "x": "micrometer"}

    # do we store each position as a single ome.zarr
    for image in tqdm(images, desc=f"Convert images from {input_folder} to ngff"):
        name = os.path.basename(image)
        out_name = name.replace(".ome.tif", ".ome.zarr")
        out_path = os.path.join(output_folder, out_name)

        loc = ome_zarr.io.parse_url(out_path, mode="w")
        group = zarr.group(loc.store)
        convert_image_data(image, group, resolution, units, name="image")

        label_root = group.create_group("labels")
        cell_segmentation = os.path.join(cell_folder, name)
        label_group = label_root.create_group("cells")
        assert os.path.exists(cell_segmentation)
        convert_label_data(cell_segmentation, label_group, label_resolution, units, label_name="cells")

        nucleus_segmentation = os.path.join(nucleus_folder, name)
        assert os.path.exists(nucleus_segmentation)
        label_group = label_group.create_group("labels")
        colors = [{"label-value": 1, "rgba": [0, 0, 255, 255]}]
        convert_label_data(nucleus_segmentation, label_group, label_resolution, units,
                           label_name="nuclei", colors=colors)

        # there should be convenience functions for adding labels instead, that takes care of this, see
        # https://github.com/ome/ome-zarr-py/issues/171
        label_root.attrs["labels"] = ["cells", "nuclei"]


if __name__ == "__main__":
    main()
