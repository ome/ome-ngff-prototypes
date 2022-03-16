import json
import os

import s3fs
# import zarr


def download_n5_volume(endpoint_url, bucket_name, container, dataset, output_file, output_key):
    os.makedirs(output_file, exist_ok=True)

    # open the container on s3
    fs = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": endpoint_url})
    store = s3fs.S3Map(root=f"{bucket_name}/{container}", s3=fs)

    # copy the root level attributes file
    attrs = store["attributes.json"].decode("utf-8")
    attrs = json.loads(attrs)
    attrs_file = os.path.join(output_file, "attributes.json")
    with open(attrs_file, "w") as f:
        json.dump(attrs, f)

    # open the dataset store
    store = s3fs.S3Map(root=f"{bucket_name}/{container}/{dataset}", s3=fs)

    # copy the dataset level attributes file
    ds_file = os.path.join(output_file, output_key)
    os.makedirs(ds_file, exist_ok=True)
    attrs = store["attributes.json"].decode("utf-8")
    attrs = json.loads(attrs)
    attrs_file = os.path.join(ds_file, "attributes.json")
    with open(attrs_file, "w") as f:
        json.dump(attrs, f)

    # open the empty local dataset and iterate over the chunks to download them
    # dataset = zarr.open(output_file)[output_key]
    for name, obj in store.items():
        if name == "attributes.json":
            continue
        chunk_path = os.path.join(ds_file, name)
        os.makedirs(os.path.split(chunk_path)[0], exist_ok=True)
        with open(chunk_path, "wb") as f:
            f.write(obj)


def download_example_data():
    os.makedirs("./example_data", exist_ok=True)
    # download the raw data (we use "s3", which is downsampled 3 times by a factor of 2)
    download_n5_volume("https://s3.embl.de", "covid-fib-sem",
                       container="Covid19-S4-Area2/images/local/fibsem-raw.n5",
                       dataset="setup0/timepoint0/s3",
                       output_file="./example_data/raw.n5", output_key="data")
    # download the segmentation data
    download_n5_volume("https://s3.embl.de", "covid-fib-sem",
                       container="Covid19-S4-Area2/images/local/s4_area2_segmentation.n5",
                       dataset="setup0/timepoint0/s3",
                       output_file="./example_data/segmentation.n5", output_key="data")


if __name__ == "__main__":
    download_example_data()
