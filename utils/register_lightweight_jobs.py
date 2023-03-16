import argparse
import traceback

from image_container_builder import ContainerImageBuilder


parser = argparse.ArgumentParser()
parser.add_argument("--image-name", type=str, help="Name of the Docker image to build")
parser.add_argument("--image-tag", type=str, help="Tag of the Docker image to build")
parser.add_argument(
    "--register-job-location",
    type=str,
    default="/unity-sps-register_job",
    help="Location of the job repository",
)
args = parser.parse_args()

if __name__ == "__main__":
    try:
        image_name = args.image_name
        image_tag = args.image_tag
        register_job_location = args.register_job_location

        cb = ContainerImageBuilder(
            image_name=image_name,
            image_tag=image_tag,
            job_repo_path=register_job_location,
        )
        cb.validate_hysds_ios()
        cb.validate_job_specs()

        cb.build_image()
        image_url = cb.push_image()

        cb.publish_job_spec()
        cb.publish_hysds_io()
        cb.publish_container(image_url)

    except Exception as ex:
        tb = traceback.format_exc()
        error = "Failed to register {}\n Exception: {}\n Error: {}".format(
            f"{image_name}:{image_tag}", ex, tb
        )
