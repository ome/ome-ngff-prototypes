# Create a MoBIE project with ome.zarr data

Example script to create a MoBIE project with ome.zarr data using the [mobie-python library](https://github.com/mobie/mobie-utils-python).
The resulting project is available both via EMBL-Heidelberg s3 and EMBL-EBI s3:
- https://s3.embl.de/i2k-2020/project-ome-zarr
- https://uk1s3.embassy.ebi.ac.uk/bia-mobie-test

It can be opened in [the MoBIE Fiji plugin](https://github.com/mobie/mobie-viewer-fiji#install) by selecting `Plugins->MoBIE->Open->Open MoBIE Project` and then entering one of the addresses.

The data used for this example is part of [Integrative imaging reveals SARS-CoV-2-induced reshaping of subcellular morphologies](https://www.sciencedirect.com/science/article/pii/S193131282030620X).
The full MoBIE project for this publication is available at https://github.com/mobie/covid-em-project.

## Running the example

First, run the `download_exmaple_data.py` script to download the example data from s3. Then run `create_mobie_ome_zarr_example.py` to create the example project.
You will need to set up a python environment with the mobie python library to run these scripts, see https://github.com/mobie/mobie-utils-python#installation for details.
