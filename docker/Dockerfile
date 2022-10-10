FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev git

RUN git clone https://github.com/hysds/otello.git && \
    cd otello && \
    git checkout unity-dev && \
    pip install -e .

# TODO: clone the unity-sps-register_job repo

WORKDIR /flask_ades_wpst
COPY . /flask_ades_wpst
# write otello config to ~/.config/otello/config.yml'?
COPY config/otello_config.yml /root/.config/otello/config.yml

RUN python3 setup.py install

ENTRYPOINT [ "python3" ]

CMD [ "-m", "flask_ades_wpst.flask_wpst", "--host=0.0.0.0" ]
