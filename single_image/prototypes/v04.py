import skimage.transform
import zarr

from .v03 import _get_chunks, _downscale

AXES_TYPE_DICT = {
    "x": "space",
    "y": "space",
    "z": "space",
    "t": "time",
    "c": "channel"
}


def create_ngff_metadata(g, name, axes_names, scale=None, units=None, type_=None, metadata=None):

    # axes metadata
    axes = [
        {"name": name, "type": AXES_TYPE_DICT[name]} for name in axes_names
    ]
    if units is not None:
        assert len(units) == len(axes_names)
        for ax, unit in zip(axes, units):
            ax["unit"] = unit

    # dataset metadata including transformations
    spatial_dims = [i for i, ax in enumerate(axes_names) if ax in "xyz"]
    if scale is None:
        scale = [1.0] * len(spatial_dims)
    else:
        scale = [scale[ax] for ax in axes_names if ax in "xyz"]

    # TODO read this from the downscaling args
    scale_factor = 2

    # NOTE we might need a half pixel offset for proper scale alignment here (via a translation)
    transforms = [
        [{"type": "scale", "scale": [sc * scale_factor**i for sc in scale], "axisIndices": spatial_dims}]
        for i in range(len(g))
    ]
    datasets = [
        {"path": name, "transformations": trafo} for name, trafo in zip(g, transforms)
    ]

    ms_entry = {
        "axes": axes,
        "datasets": datasets,
        "name": name,
        "version": "0.4"
    }
    if type_ is not None:
        ms_entry["type"] = type_
    if metadata is not None:
        ms_entry["metadata"] = metadata

    metadata = g.attrs.get("multiscales", [])
    metadata.append(ms_entry)
    g.attrs["multiscales"] = metadata

    # write the array dimensions for compat with xarray:
    # https://xarray.pydata.org/en/stable/internals/zarr-encoding-spec.html?highlight=zarr
    for ds in g.values():
        ds.attrs["_ARRAY_DIMENSIONS"] = axes_names


def write_ome_zarr(data, path, axes_names, name, n_scales,
                   key=None, chunks=None,
                   downscaler=skimage.transform.rescale,
                   kwargs={"scale": (0.5, 0.5, 0.5), "order": 0, "preserve_range": True},
                   scale=None, units=None,
                   dimension_separator="/"):
    """Write numpy data to ome.zarr format.
    """
    assert dimension_separator in (".", "/")
    assert 2 <= data.ndim <= 5
    assert len(axes_names) == data.ndim

    chunks = _get_chunks(axes_names) if chunks is None else chunks
    if dimension_separator == "/":
        store = zarr.NestedDirectoryStore(path, dimension_separator=dimension_separator)
    else:
        store = zarr.DirectoryStore(path, dimension_separator=dimension_separator)

    with zarr.open(store, mode="a") as f:
        g = f if key is None else f.require_group(key)
        g.create_dataset("s0", data=data, chunks=chunks, dimension_separator=dimension_separator)
        for ii in range(1, n_scales):
            data = _downscale(data, axes_names, downscaler, kwargs)
            g.create_dataset(f"s{ii}", data=data, chunks=chunks, dimension_separator=dimension_separator)
        function_name = f"{downscaler.__module__}.{downscaler.__name__}"
        create_ngff_metadata(g, name, axes_names,
                             type_=function_name, metadata=kwargs,
                             scale=scale, units=units)
