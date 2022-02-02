import argparse
import json
import os
from glob import glob

import requests
from jsonschema import validate


def validate_v04():
    # TODO there is probably a more elegant way to do this with json schema
    url = "https://raw.githubusercontent.com/ome/ngff/main/0.4/schemas/image.schema"
    with requests.get(url) as r:
        with open("./schema.json", "w") as f:
            f.write(r.text)
    with open("./schema.json") as f:
        schema = json.load(f)

    files = glob("./v0.4/*.ome.zarr")
    print(files)
    for path in files:
        print("Validate", path)
        with open(os.path.join(path, ".zattrs"), "r") as f:
            metadata = json.load(f)
        validate(instance=metadata, schema=schema)
    print("All passed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", type=str)
    args = parser.parse_args()
    version = args.version.lstrip("v")
    if version == "0.4":
        validate_v04()
    else:
        raise ValueError(f"Invalid version: {args.version}")


if __name__ == "__main__":
    main()
