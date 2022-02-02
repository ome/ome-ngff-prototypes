# OME-NGFF-Prototypes

Prototypes for [ome.zarr / ome.ngff](https://github.com/ome/ngff). Example data with the goal to collect diverse applications.

## Examples

### Single Image

The examples in `single_image` contain data that is described with a single `multiscales` metadata for all relevant `tczyx` axes combinations:
- yx.ome.zarr: 2d image, nucleus channel of an image from [1]
- zyx.ome.zarr: 3d volume, EM volume from [2]
- cyx.ome.zarr: 2d image with channels, image with nucleus, virus marker and serum channels from [1]
- tyx.ome.zarr: timeseries of 2d images, timeseries of central slice of membrane channel from [3]
- tzyx.ome.zarr: timeseries of 3d images, timeseries of membrane channel volume from [3]
- tcyx.ome.zarr: timeseries of images with channel, timeseries of central slice of membrane + nucleus channel from [3]
- czyx.ome.zarr: 3d volume with channel, single timepoint of membrane and nucleus channel from [3]
- tczyx.ome.zarr: timeseries of 3d volumes with channel, full data from [3]
- multi-image.ome.zarr: a simple example for multiple images in one ome.zarr, stores all four channels from `cyx.ome.zarr` as separate 2d images.

Publications:
- [1] https://onlinelibrary.wiley.com/doi/full/10.1002/bies.202000257
- [2] https://www.sciencedirect.com/science/article/pii/S193131282030620X
- [3] https://elifesciences.org/articles/57613

Data availability:
- The initial data in h5 format is available at https://oc.embl.de/index.php/s/4bDrWVnuDHIKmRF.
- The data in ome.zarr format version 0.3 is available at https://s3.embl.de/i2k-2020/ngff-example-data/v0.3. 
- The data in ome.zarr format version 0.4 is available at:
    - https://s3.embl.de/i2k-2020/ngff-example-data/v0.4 (via s3)
    - https://oc.embl.de/index.php/s/tTcRt4TUF9oqZPe (as single zip with all the example data)
