<!-- Header block for project -->
<hr>

<div align="center">

![logo](https://user-images.githubusercontent.com/3129134/163255685-857aa780-880f-4c09-b08c-4b53bf4af54d.png)

<h1 align="center">[unity-sds/ades_wpst]</h1>
<!-- ☝️ Replace with your repo name ☝️ -->

</div>

<pre align="center">The repo is an API Implementation which conforms to the OGC Standards, specifically WPS-T.</pre>
<!-- ☝️ Replace with a single sentence describing the purpose of your repo / proj ☝️ -->

<!-- Header block for project -->

[INSERT YOUR BADGES HERE (SEE: https://shields.io)] [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
<!-- ☝️ Add badges via: https://shields.io e.g. ![](https://img.shields.io/github/your_chosen_action/your_org/your_repo) ☝️ -->

![Screenshot](screenshot.png)
<!-- ☝️ Screenshot of your software (if applicable) via ![](https://uri-to-your-screenshot) ☝️ -->

This API is compliant with OGC's WPS-T specifications and implements a subset of the enpoints. We support the processes and jobs endpoints.
<!-- ☝️ Replace with a more detailed description of your repository, including why it was made and whom its intended for.  ☝️ -->

Link to OGC Specifications: http://docs.opengeospatial.org/per/18-050r1.html#_wps_t_restjson
<!-- example links>
[Website](INSERT WEBSITE LINK HERE) | [Docs/Wiki](INSERT DOCS/WIKI SITE LINK HERE) | [Discussion Board](INSERT DISCUSSION BOARD LINK HERE) | [Issue Tracker](INSERT ISSUE TRACKER LINK HERE)
-->

## Features

The API supports the following OGC operations:
* Get Processes
* Deploy a Process
* Undeploy a Process
* Describe Process
* Execute Process
* Get Job Status
* Get Job Result
* Dismiss Job
* List Jobs by Process
  
<!-- ☝️ Replace with a bullet-point list of your features ☝️ -->

## Contents

* [Quick Start](#quick-start)
* [Changelog](#changelog)
* [FAQ](#frequently-asked-questions-faq)
* [Contributing Guide](#contributing)
* [License](#license)
* [Support](#support)

## Quick Start

This guide provides a quick way to install and get started with API.

### Requirements

* The `Flask` python module is required for installation.
* If you want to run the API with a connection to HySDS, then make sure to have the kubernetes cluster running before hand. Refer to https://github.com/unity-sds/unity-sps-prototype/tree/main/hysds

  
<!-- ☝️ Replace with a numbered list of your requirements, including hardware if applicable ☝️ -->

### Setup Instructions

Clone the repo and create a subdirectory for the SQLite database file.

    git clone https://github.com/unity-sds/ades_wpst.git
    cd ades_wpst
    mkdir sqlite #to setup the local db

Be sure to satisfy the requirements list in "Requirements" section above first.  Install
natively as a python module with:

    python setup.py install


### Build Instructions
    
Build the docker container:

    docker build -t unity/ades-wpst-api:<tag> -f docker/Dockerfile .

For active development purposes (not releases), if you want to build container as frequent as multiple times a day, you can use the following to version containers by datetime

Run the following commands in order, every time:

    export DOCKER_TAG=$(date +"%d-%m-%yT%H.%M.%S")
    docker build -t unity/ades-wpst-api:$DOCKER_TAG -f docker/Dockerfile .
    docker tag unity/ades-wpst-api:$DOCKER_TAG unity/ades-wpst-api:latest ;

   
<!-- ☝️ Replace with a numbered list of how to set up your software prior to running ☝️ -->

### Run Instructions

#### Run it natively (not in a container)
Be sure to follow the steps in the "Get started" section above first.
Run the Flask app server with:

    python -m flask_ades_wpst.flask_wpst

      
#### Run with Docker: 
To run the docker container without connecting to the the ADES platform:

    docker run -it -p 5000:5000 -v ${PWD}/sqlite:/ades_wpst/sqlite unity/ades-wpst-api:latest


To run the docker container with the ADES platform, set the `ADES_PLATFORM` environment variable to the
appropriate setting for your platform (examples: K8s, PBS, HySDS).

    docker run -it -p 5000:5000 -v ${PWD}/sqlite:/ades_wpst/sqlite -e "ADES_PLATFORM=<platform>" unity/ades-wpst-api:<tag>
    
For the Unity prototype set it to HySDS:

    docker run -it -p 5000:5000 -v ${PWD}/sqlite:/ades_wpst/sqlite -e "ADES_PLATFORM=HySDS" unity/ades-wpst-api:<tag>

   
<!-- ☝️ Replace with a numbered list of your run instructions, including expected results ☝️ -->

### Usage Examples

To run as a Docker container, but sure to do the following in the `docker run`
command as shown in the examples above:

1. Map the Flask application server port to the host port (`-p` option)
1. Mount your `sqlite` subdirectory on the host machine in to the container
(`-v` option)
1. Set the `ADES_PLATFORM` environment variable to a supported environment
(e.g., `K8s`, `PBS`, `Generic`, `HySDS`) (`-e` option).  If no environment variable
is set, the default is `Generic`, which results in no additional actions
being done on the host.

<!-- ☝️ Replace with a list of your usage examples, including screenshots if possible, and link to external documentation for details ☝️ -->


### Test Instructions

To test the API endpoints you can use the following test plan:

1. **Get Processes**: `GET /processses`, after a new API deployment this should be empty i.e. in the response, `processes` list should be empty.
2. **Deploy a process** : `POST /processses`, if response is 200 then proceed to following steps
3. **Get Processes**: `GET /processses`, expect to see the process deployed above. In the response validate that the name in `processes[0].id`  matches the proc ID from step 2.
4. **Describe Process**: `GET /processes/[procID]`
5. **Execute Process**: `POST /processes/[procID]/jobs`, submit a job with the expected input params for the process deployed in Step 2. Expect and empty response but check for the field `location` for the URL to get job status in the response header.
6. **Get Job Status**: `GET /processes/[procID]/jobs/[jobID]`, use the URL found in the response header from step 5 (may need to update base URL to not point to localhost if API deployed on MCP) and perform a GET Request. Once the job status changes to `succeeded` then do Step 7.
7. **Get Job Result**: `GET /processes/[procID]/jobs/[jobID]/result`, If job had succeeded, look for `outputs` list in response.
8. **Get Jobs by Process**: `GET /processes/[procID]/jobs`,  returns a `jobs` list which contains the jobID, status and input parameters.
9. **Dismiss a job**: `DELETE /processes/[procID]/jobs/[jobID]` , stops a job if it's in running state, if job is still queued then it'll be deleted. Expect the same response format as Get Job Status (Step 6). The status should say `dismissed` . If job state is anything other than running or accepted at the time dismiss is requested, then the API will return an error in the response saying `Can not dismiss a job in {job status} state`.
10. **Undeploy Process**: `DELETE /processes/[procID]` , perform this after you are done testing everything for the process. On successful undeployment, you'll see  `undeploymentResult` in the response. To verify it's removed, you can do Get Processes (Step 3) and verify that the procID is not in the processes list.

<!-- ☝️ Replace with a numbered list of your test instructions, including expected results / outputs with optional screenshots ☝️ -->

## Changelog

See our [CHANGELOG.md](CHANGELOG.md) for a history of our changes.

See our [releases page]([INSERT LINK TO YOUR RELEASES PAGE]) for our key versioned releases.

<!-- ☝️ Replace with links to your changelog and releases page ☝️ -->

## Frequently Asked Questions (FAQ)

[INSERT LINK TO FAQ PAGE OR PROVIDE FAQ INLINE HERE]
<!-- example link to FAQ PAGE>
Questions about our project? Please see our: [FAQ]([INSERT LINK TO FAQ / DISCUSSION BOARD])
-->

<!-- example FAQ inline format>
1. Question 1
   - Answer to question 1
2. Question 2
   - Answer to question 2
-->

<!-- example FAQ inline with no questions yet>
No questions yet. Propose a question to be added here by reaching out to our contributors! See support section below.
-->

<!-- ☝️ Replace with a list of frequently asked questions from your project, or post a link to your FAQ on a discussion board ☝️ -->

## Contributing

Interested in contributing to our project? Please see our: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

See our: [LICENSE](LICENSE)

## Support

[INSERT CONTACT INFORMATION OR PROFILE LINKS TO MAINTAINERS AMONG COMMITTER LIST]

<!-- example list of contacts>
Key points of contact are: [@github-user-1](link to github profile) [@github-user-2](link to github profile)
-->

<!-- ☝️ Replace with the key individuals who should be contacted for questions ☝️ -->

