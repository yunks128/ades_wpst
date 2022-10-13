FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y ca-certificates \
    curl \
    gnupg \
    lsb-release && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get install docker-ce-cli


WORKDIR /flask_ades_wpst

COPY . /flask_ades_wpst

RUN python3 setup.py install

ENTRYPOINT [ "python3" ]

CMD [ "-m", "flask_ades_wpst.flask_wpst", "--host=0.0.0.0" ]
