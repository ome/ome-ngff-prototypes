# Convert data from a spatial transcriptomics experiment to ome.zarr

Example script to convert data from a spatial transcriptomics experiment (stored as ome.tiff and csv files) into ome.zarr
It uses the [ome-zarr-py python library](https://github.com/ome/ome-zarr-py). The resulting data is hosted on [IDR](todo).

The data used for this example is part of [Integration of spatial and single-cell transcriptomic data elucidates mouse organogenesis](https://www.nature.com/articles/s41587-021-01006-2).
Note that the script currently only converts the image data to ome.zarr and does not operate on the actual transcriptomics data.
This will be updated once tabular data is fully supported in ome.zarr, see https://github.com/ome/ngff/pull/64.
The current script also does not join the separate positions per mouse embryo into their common coordinate space; this will also be updated.

## Running the example

First, download the example data from https://oc.embl.de/index.php/s/Is8P2s4Vvm2jpt9. Note that this only contains one of the positions from the publication data.
Then run `convert_transcriptomics_data.py`. You will need to set up a python library with `ome-zarr-py` to run this script, see https://github.com/ome/ome-zarr-py#installation for details.
