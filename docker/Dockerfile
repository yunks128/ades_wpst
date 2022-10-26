FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev git && \
    apt-get install -y curl && \
    curl https://get.docker.com/builds/Linux/x86_64/docker-latest.tgz | tar xvz -C /tmp/ && mv /tmp/docker/docker /usr/bin/docker
    # apt-get install -y ca-certificates curl gnupg lsb-release && \
    # curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    # echo \
    # "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    # $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    # apt-get install docker-ce-cli

RUN git clone https://github.com/hysds/otello.git && \
    cd otello && \
    git checkout unity-dev && \
    pip install -e .

RUN git clone https://github.com/unity-sds/unity-sps-register_job.git
# RUN git clone -b deploy-process https://github.com/drewm-jpl/unity-sps-register_job.git

WORKDIR /flask_ades_wpst
COPY . /flask_ades_wpst
# write otello config to ~/.config/otello/config.yml'?
COPY config/otello_config.yml /root/.config/otello/config.yml

RUN python3 setup.py install

ENTRYPOINT [ "python3" ]

CMD [ "-m", "flask_ades_wpst.flask_wpst", "--host=0.0.0.0" ]
