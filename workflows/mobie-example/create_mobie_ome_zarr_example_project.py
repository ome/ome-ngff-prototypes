import mobie


DS_NAME = "Covid19-S4-Area2"


def create_ngff_example(file_format):
    raw_path = "../data/Covid19-S4-Area2/images/local/sbem-6dpf-1-whole-raw.n5"
    raw_key = "setup0/timepoint0/s3"

    resolution = (0.008, 0.008, 0.008)
    resolution = [res * 2 ** 3 for res in resolution]
    scale_factors = [[2, 2, 2]] * 3
    chunks = (64,) * 3

    mobie.add_image(raw_path, raw_key, "./data", DS_NAME, image_name="raw",
                    resolution=resolution, scale_factors=scale_factors, chunks=chunks,
                    file_format=file_format, menu_name="em", target="local", max_jobs=8)

    seg_path = "../data/Covid19-S4-Area2/images/local/s4_area2_segmentation.n5"
    seg_key = "setup0/timepoint0/s3"
    mobie.add_segmentation(seg_path, seg_key, "./data", DS_NAME, segmentation_name="segmentation",
                           resolution=resolution, scale_factors=scale_factors, chunks=chunks, menu_name="em-seg",
                           file_format=file_format, max_jobs=8)


def upload_example(service_endpoint, bucket_name, upload):
    from subprocess import run
    mobie.metadata.add_remote_project_metadata("./data", bucket_name, service_endpoint)
    if upload:
        s3_path = f"embl/{bucket_name}/"
        cmd = ["mc", "cp", "-r", "data/", s3_path]
        print(cmd)
        run(cmd)


def create_example(file_format, service_endpoint, bucket_name, upload=False):
    create_ngff_example(file_format)
    upload_example(service_endpoint, bucket_name, upload)


def create_example_embl():
    file_format = "ome.zarr"
    service_endpoint = "https://s3.embl.de"
    bucket_name = "i2k-2020/project-ome-zarr"
    create_example(file_format, service_endpoint, bucket_name, upload=True)


def create_example_ebi():
    file_format = "ome.zarr"
    service_endpoint = "https://uk1s3.embassy.ebi.ac.uk"
    bucket_name = "bia-mobie-test"
    create_example(file_format, service_endpoint, bucket_name, upload=False)


if __name__ == "__main__":
    # create_example_embl()
    create_example_ebi()
