import numpy as np
import skimage.transform
import zarr

AXES_NAMES = {"t", "c", "z", "y", "x"}


def _get_chunks(axes_names):
    if len(axes_names) == 2:
        chunks = (256, 256)
    elif len(axes_names) == 3:
        chunks = 3*(64,) if axes_names[0] == "z" else (1, 256, 256)
    elif len(axes_names) == 4:
        chunks = (1, 1, 256, 256) if axes_names[:2] == ("t", "c") else (1, 64, 64, 64)
    else:
        chunks = (1, 1, 64, 64, 64)
    # make 5d
    if len(chunks) < 5:
        chunks = (5 - len(chunks)) * (1,) + chunks
    assert len(chunks) == 5
    return chunks


def _validate_axes_names(ndim, axes_names):
    assert len(axes_names) == ndim
    val_axes = tuple(axes_names)
    if ndim == 2:
        assert val_axes == ("y", "x"), str(val_axes)
    elif ndim == 3:
        assert val_axes in [("z", "y", "x"), ("c", "y", "x"), ("t", "y", "x")], str(val_axes)
    elif ndim == 4:
        assert val_axes in [("t", "z", "y", "x"), ("c", "z", "y", "x"), ("t", "c", "y", "x")], str(val_axes)
    else:
        assert val_axes == ("t", "c", "z", "y", "x"), str(val_axes)


def _downscale(data, axes_names, downscaler, kwargs):
    is_spatial = [ax in ("z", "y", "x") for ax in axes_names]
    # downscaling is easy if we only have spatial axes
    if all(is_spatial):
        data = downscaler(data, **kwargs).astype(data.dtype)
    else:
        spatial_start = [i for i, spatial in enumerate(is_spatial) if spatial][0]
        assert spatial_start in (1, 2), str(spatial_start)
        if spatial_start == 1:
            downscaled_data = []
            for d in data:
                ds = downscaler(d, **kwargs).astype(data.dtype)
                downscaled_data.append(ds[None])
            data = np.concatenate(downscaled_data, axis=0)
        else:
            downscaled_data = []
            for time_slice in data:
                downscaled_channel = []
                for channel_slice in time_slice:
                    ds = downscaler(channel_slice, **kwargs).astype(data.dtype)
                    downscaled_channel.append(ds[None])
                downscaled_channel = np.concatenate(downscaled_channel, axis=0)
                downscaled_data.append(downscaled_channel[None])
            data = np.concatenate(downscaled_data, axis=0)
    return data


def expand_data(data, axes_names):
    target_axes = tuple("tczyx")
    singletons = tuple(np.s_[:] if ax in axes_names else np.s_[None] for ax in target_axes)
    expanded = data[singletons]
    assert expanded.ndim == len(target_axes)
    return expanded


def write_ome_zarr(data, path, axes_names, name, n_scales,
                   key=None, chunks=None,
                   downscaler=skimage.transform.rescale,
                   kwargs={"scale": (0.5, 0.5, 0.5), "order": 0, "preserve_range": True},
                   dimension_separator="/", **extra_kwargs):
    """Write numpy data to ome.zarr format.
    """
    assert dimension_separator in (".", "/")
    assert 2 <= data.ndim <= 5
    _validate_axes_names(data.ndim, axes_names)

    chunks = _get_chunks(axes_names) if chunks is None else chunks
    if dimension_separator == "/":
        store = zarr.NestedDirectoryStore(path, dimension_separator=dimension_separator)
    else:
        store = zarr.DirectoryStore(path, dimension_separator=dimension_separator)

    with zarr.open(store, mode="a") as f:
        g = f if key is None else f.require_group(key)
        expanded_data = expand_data(data, axes_names)
        g.create_dataset("s0", data=expanded_data, chunks=chunks, dimension_separator=dimension_separator)
        for ii in range(1, n_scales):
            data = _downscale(data, axes_names, downscaler, kwargs)
            expanded_data = expand_data(data, axes_names)
            g.create_dataset(f"s{ii}", data=expanded_data, chunks=chunks, dimension_separator=dimension_separator)
        function_name = f"{downscaler.__module__}.{downscaler.__name__}"
        create_ngff_metadata(g, name, type_=function_name, metadata=kwargs)


def create_ngff_metadata(g, name, type_=None, metadata=None):
    """Create ome-ngff metadata for a multiscale dataset stored in zarr format.
    """
    # validate the individual datasets
    ndim = g[list(g.keys())[0]].ndim
    assert all(dset.ndim == ndim for dset in g.values())

    ms_entry = {
        "datasets": [
            {"path": name} for name in g
        ],
        "name": name,
        "version": "0.2"
    }
    if type_ is not None:
        ms_entry["type"] = type_
    if metadata is not None:
        ms_entry["metadata"] = metadata

    metadata = g.attrs.get("multiscales", [])
    metadata.append(ms_entry)
    g.attrs["multiscales"] = metadata
