# Create a MoBIE project with ome.zarr data

Example script to create a MoBIE project with ome.zarr data using the [mobie-python library](https://github.com/mobie/mobie-utils-python).
The resulting project is available both via EMBL-Heidelberg s3 and EMBL-EBI s3:
- https://s3.embl.de/i2k-2020/project-ome-zarr
- https://uk1s3.embassy.ebi.ac.uk/bia-mobie-test

It can be opened in [the MoBIE Fiji plugin](https://github.com/mobie/mobie-viewer-fiji#install) by selecting `Plugins->MoBIE->Open->Open MoBIE Project` and then entering one of the addresses.

The data used for this example is part of [Integrative imaging reveals SARS-CoV-2-induced reshaping of subcellular morphologies](https://www.sciencedirect.com/science/article/pii/S193131282030620X).
The full MoBIE project for this publication is available at https://github.com/mobie/covid-em-project.

## Running the example

This example contains two scripts:
- `download_example_data.py` to load the data for this example from s3. You can pass the argument `--scale` to this function to choose the scale level at which the data will be downloaded and control the size of the data. For example `python download_exampl_data.py --scale 0` will download it at the full resolution, corresponding to the maximal size. The default is scale 3.
- `create_mobie_ome_zarr_example.py` to create the MoBIE project, using ome.zarr as data format.

You will need to set up a python environment with the mobie python library to run these scripts, see https://github.com/mobie/mobie-utils-python#installation for details.
