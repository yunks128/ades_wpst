import os
import re
import json
import requests
import jsonschema
import docker


class StreamLineBuildGenerator(object):
    def __init__(self, json_data):
        self.__dict__ = json_data


# https://stackoverflow.com/questions/33570014/how-can-i-detect-when-docker-py-client-build-fails
def _process_output(output):
    if type(output) == str:
        output = output.split("\n")

    for line in output:
        if line:
            errors = set()
            try:
                stream_line = StreamLineBuildGenerator(line)

                if hasattr(stream_line, "status"):
                    print(stream_line.status)

                elif hasattr(stream_line, "stream"):
                    stream = re.sub("^\n", "", stream_line.stream)
                    stream = re.sub("\n$", "", stream)
                    # found after newline to close (red) "error" blocks: 27 91 48 109
                    stream = re.sub("\n(\x1B\[0m)$", "\\1", stream)
                    if stream:
                        print(stream)

                elif hasattr(stream_line, "aux"):
                    if hasattr(stream_line.aux, "Digest"):
                        print("digest: {}".format(stream_line.aux["Digest"]))

                    if hasattr(stream_line.aux, "ID"):
                        print("ID: {}".format(stream_line.aux["ID"]))
                else:
                    print("not recognized (1): {}".format(line))

                if hasattr(stream_line, "error"):
                    errors.add(stream_line.error)

                if hasattr(stream_line, "errorDetail"):
                    errors.add(stream_line.errorDetail["message"])

                    if hasattr(stream_line.errorDetail, "code"):
                        error_code = stream_line.errorDetail["code"]
                        errors.add("Error code: {}".format(error_code))

            except ValueError as e:
                print("not recognized (2): {}".format(line))

            if errors:
                message = "problem executing Docker: {}".format(". ".join(errors))
                raise SystemError(message)


class ContainerImageBuilder:
    def __init__(self, image_name, image_tag, job_repo_path):
        self.image_name = image_name
        self.image_tag = image_tag
        self.job_repo_path = job_repo_path
        self.image_name_tag = "{}:{}".format(self.image_name, self.image_tag)
        self._CR_SERVER = os.environ.get("CR_SERVER")
        self._CR_USERNAME = os.environ.get("CR_USERNAME")
        self._CR_PAT = os.environ.get("CR_PAT")
        self._CR_OWNER = os.environ.get("CR_OWNER")
        self._MOZART_REST_API = f"http://mozart:8888/api/v0.1/"
        self._GRQ_REST_API = f"http://grq2:8878/api/v0.1/"
        self.client = docker.from_env()
        self.api_client = docker.APIClient(base_url="unix://var/run/docker.sock")
        self.client.login(self._CR_USERNAME, self._CR_PAT, None, self._CR_SERVER)

    def push_image(self):
        image_url = f"{self._CR_SERVER}/{self._CR_OWNER}/{self.image_name_tag}"
        image = self.client.images.get(self.image_name_tag)
        image.tag(image_url, self.image_tag)

        output = self.client.images.push(image_url, self.image_tag)
        output = list(filter(None, output.split("\r\n")))
        output = [json.loads(i) for i in output]
        _process_output(output)

        return image_url

    def build_image(self):
        """
        Builds the Docker image
        :param tag: str; example, hello_world:develop
        :return: int; return status of docker build command
        """

        dockerfile_path = os.path.join(self.job_repo_path, "docker", "Dockerfile")
        output = [
            line
            for line in self.api_client.build(
                path=self.job_repo_path,
                dockerfile=dockerfile_path,
                rm=True,
                tag=self.image_name_tag,
                decode=True,
            )
        ]
        _process_output(output)

    def _build_container_name(self):
        container = "container-%s" % (self.image_name_tag)
        return container

    def _build_job_spec_name(self, filename):
        """
        :param file_name:
        :param version:
        :return: str, ex. job-hello_world:develop
        """
        name = filename.split(".")[-1]
        job_name = "job-%s:%s" % (name, self.image_tag)
        return job_name

    def _build_hysds_io_name(self, filename):
        """
        :param file_name:
        :param version:
        :return: str, ex. hysds-io-hello_world:develop
        """
        name = filename.split(".")[-1]
        hysds_io_name = "hysds-io-%s:%s" % (name, self.image_tag)
        return hysds_io_name

    def validate_hysds_ios(self):
        """
        Validates every hysds-io file in docker/ against the schema
        :param path:
        :return:
        """
        hysds_ios_schema = "https://raw.githubusercontent.com/hysds/hysds_commons/develop/schemas/hysds-io-schema.json"
        resp = requests.get(hysds_ios_schema)
        schema = resp.json()

        hysds_ios_dir = os.path.join(self.job_repo_path, "docker")
        hysds_ios_files = filter(
            lambda x: x.startswith("hysds-io"), os.listdir(hysds_ios_dir)
        )
        for i in hysds_ios_files:
            with open(os.path.join(hysds_ios_dir, i), "r") as f:
                d = json.load(f)
                validator = jsonschema.Draft7Validator(schema)
                errors = sorted(validator.iter_errors(d), key=lambda e: e.path)
                if len(errors) > 0:
                    raise RuntimeError(
                        "JSON schema failed to validate; errors: {}".format(errors)
                    )

    def validate_job_specs(self):
        """
        Validates every job-spec file in docker/ against the schema
        :param path:
        :return:
        """
        job_spec_schema = "https://raw.githubusercontent.com/hysds/hysds_commons/develop/schemas/job-spec-schema.json"
        resp = requests.get(job_spec_schema)
        schema = resp.json()

        jobspec_dir = os.path.join(self.job_repo_path, "docker")
        jobspec_files = filter(
            lambda x: x.startswith("job-spec"), os.listdir(jobspec_dir)
        )
        for i in jobspec_files:
            with open(os.path.join(jobspec_dir, i), "r") as f:
                d = json.load(f)
                validator = jsonschema.Draft7Validator(schema)
                errors = sorted(validator.iter_errors(d), key=lambda e: e.path)
                if len(errors) > 0:
                    raise RuntimeError(
                        "JSON schema failed to validate; errors: {}".format(errors)
                    )

    def publish_container(self, image_url, dry_run=False):
        """
        :param path:
        :param repository:
        :param version:
        :param dry_run:
        :return:
        """
        image = self.client.images.get(self.image_name_tag)
        digest = image.id
        metadata = {
            "name": self._build_container_name(),
            "version": self.image_tag,
            "url": image_url,
            "digest": digest,
            "resource": "container",
        }
        print("container: ", json.dumps(metadata, indent=2))
        if dry_run is False:
            add_container_endpoint = os.path.join(
                self._MOZART_REST_API, "container/add"
            )
            print(add_container_endpoint)
            r = requests.post(add_container_endpoint, data=metadata, verify=False)
            print(r.text)
            r.raise_for_status()

    def publish_job_spec(self, dry_run=False):
        """
        :param path:
        :param version:
        :param dry_run:
        :return:
        """
        fps = os.path.join(self.job_repo_path, "docker")
        for p in filter(lambda x: x.startswith("job-spec"), os.listdir(fps)):
            metadata = dict()
            metadata["container"] = self._build_container_name()
            metadata["job-version"] = self.image_tag
            metadata["resource"] = "jobspec"
            metadata["id"] = self._build_job_spec_name(p)
            with open(os.path.join(fps, p)) as f:
                job_spec = json.loads(f.read())
                metadata = {**metadata, **job_spec}
                print("job_specs: ", json.dumps(metadata, indent=2))
                if dry_run is False:
                    add_jobspec_endpoint = os.path.join(
                        self._MOZART_REST_API, "job_spec/add"
                    )
                    print(add_jobspec_endpoint)
                    r = requests.post(
                        add_jobspec_endpoint,
                        data={"spec": json.dumps(metadata)},
                        verify=False,
                    )
                    print(r.text)
                    r.raise_for_status()

    def publish_hysds_io(self, dry_run=False):
        """
        :param path:
        :param version:
        :param dry_run:
        :return:
        """
        fps = os.path.join(self.job_repo_path, "docker")
        for p in filter(lambda x: x.startswith("hysds-io"), os.listdir(fps)):
            name = p.split(".")[-1]
            metadata = dict()
            metadata["job-specification"] = self._build_job_spec_name(name)
            metadata["job-version"] = self.image_tag
            metadata["resource"] = "hysds-io-specification"
            metadata["id"] = self._build_hysds_io_name(name)
            with open(os.path.join(fps, p)) as f:
                hysds_io = json.loads(f.read())
                metadata = {**metadata, **hysds_io}
                print("hysds-ios: ", json.dumps(metadata, indent=2))
                if dry_run is False:
                    if metadata.get("component", "tosca") in ("mozart", "figaro"):
                        add_hysds_io_endpoint = os.path.join(
                            self._MOZART_REST_API, "hysds_io/add"
                        )
                    else:
                        add_hysds_io_endpoint = os.path.join(
                            self._GRQ_REST_API, "hysds_io/add"
                        )
                    print(add_hysds_io_endpoint)
                    r = requests.post(
                        add_hysds_io_endpoint,
                        data={"spec": json.dumps(metadata)},
                        verify=False,
                    )
                    print(r.text)
                    r.raise_for_status()
