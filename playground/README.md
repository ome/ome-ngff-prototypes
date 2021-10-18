# Playground

Prototypes for ome.ngff example data with the goal to collect diverse applications.

## Example Applications

### Single Image

The examples in `single_image` contain data that is described with a single `multiscales` metadata for all relevant `tczyx` axes combinations:
- yx: 2d image, nucleus channel of an image from [1]
- zyx: 3d volume, EM volume from [2]
- cyx: 2d image with channels, image with nucleus, virus marker and serum channels from [1]
- tyx: timeseries of 2d images, timeseries of central slice of membrane channel from [3]
- tzyx: timeseries of 3d images, timeseries of membrane channel volume from [3]
- tcyx: timeseries of images with channel, timeseries of central slice of membrane + nucleus channel from [3]
- czyx: 3d volume with channel, single timepoint of membrane and nucleus channel from [3]
- tczyx: timeseries of 3d volumes with channel, full data from [3]

Publications:
- [1] https://onlinelibrary.wiley.com/doi/full/10.1002/bies.202000257
- [2] https://www.sciencedirect.com/science/article/pii/S193131282030620X
- [3] https://elifesciences.org/articles/57613

The initial data in h5 format is available at https://oc.embl.de/index.php/s/4bDrWVnuDHIKmRF. 
The data in ome.zarr format version 0.3 is available at TODO
The data in ome.zarr format version 0.4 is available at TODO
