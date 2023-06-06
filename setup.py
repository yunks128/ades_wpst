from setuptools import setup, find_packages

setup(
    name="flask_ades_wpst",
    version="0.1",
    packages=find_packages(),
    author="",
    author_email="",
    description="Base Flask app implementing OGC/ADES WPS-T specification",
    long_description=open("README.md").read(),
    keywords="ADES WPS-T Flask SOAMC HySDS JPL",
    url="https://github.jpl.nasa.gov/SOAMC/flask_ades_wpst.git",
    project_urls={
        "Source Code": "https://github.jpl.nasa.gov/SOAMC/flask_ades_wpst.git",
        "Container": "https://hub.docker.com/r/jjacob7734/flask-ades-wpst",
    },
    install_requires=[
        "Flask==2.0.2",
        "requests==2.29.0",
        "urllib3==1.26.15",
        "pyyaml==5.4.1",
        "kubernetes==19.15.0",
        "cwltool==3.1.20211107152837",
        "cwl-runner==1.0",
        "docker==6.0.0",
        "jsonschema==4.5.1",
        "GitPython==3.1.29",
        "pydantic==1.10.7",
        "boto3==1.26.118",
    ],
)
