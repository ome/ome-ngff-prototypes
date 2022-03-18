import argparse
import mobie


def create_ngff_example(file_format, max_jobs):
    ds_name = "Covid19-S4-Area2"
    raw_path = "./example_data/raw.n5"
    raw_key = "data"

    resolution = (0.008, 0.008, 0.008)
    resolution = [res * 2 ** 3 for res in resolution]
    scale_factors = [[2, 2, 2]] * 3
    chunks = (64,) * 3

    mobie.add_image(raw_path, raw_key, "./data", ds_name, image_name="raw",
                    resolution=resolution, scale_factors=scale_factors, chunks=chunks,
                    file_format=file_format, menu_name="em", target="local", max_jobs=16)

    seg_path = "./example_data/segmentation.n5"
    seg_key = "data"
    mobie.add_segmentation(seg_path, seg_key, "./data", ds_name, segmentation_name="segmentation",
                           resolution=resolution, scale_factors=scale_factors, chunks=chunks, menu_name="em-seg",
                           file_format=file_format, max_jobs=max_jobs)


def upload_example(service_endpoint, bucket_name, upload):
    from subprocess import run
    mobie.metadata.add_remote_project_metadata("./data", bucket_name, service_endpoint)
    if upload:
        s3_path = f"embl/{bucket_name}/"
        cmd = ["mc", "cp", "-r", "data/", s3_path]
        print(cmd)
        run(cmd)


def create_example(file_format, service_endpoint, bucket_name, upload=False, max_jobs=16):
    create_ngff_example(file_format, max_jobs)
    upload_example(service_endpoint, bucket_name, upload)


def create_example_embl(max_jobs):
    file_format = "ome.zarr"
    service_endpoint = "https://s3.embl.de"
    bucket_name = "i2k-2020/project-ome-zarr"
    create_example(file_format, service_endpoint, bucket_name, upload=True, max_jobs=max_jobs)


def create_example_ebi(max_jobs):
    file_format = "ome.zarr"
    service_endpoint = "https://uk1s3.embassy.ebi.ac.uk"
    bucket_name = "bia-mobie-test"
    create_example(file_format, service_endpoint, bucket_name, upload=False, max_jobs=max_jobs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max_jobs", type=int, default=16)
    # for_ebi: whether to create s3 metadata for deposition on the EBI/BIA s3 or the on-premise EMBL-HD s3
    parser.add_argument("-e", "--for_ebi", type=int, default=0)
    args = parser.parse_args()
    if bool(args.for_ebi):
        create_example_ebi(args.max_jobs)
    else:
        create_example_embl(args.max_jobs)


if __name__ == "__main__":
    main()
