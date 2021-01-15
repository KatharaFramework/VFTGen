FROM kathara/base

ARG DEBIAN_FRONTEND="noninteractive"
RUN apt update
RUN apt upgrade -y
RUN apt install -y python3-pip
RUN git clone https://github.com/brunorijsman/rift-python /rift
RUN python3 -m pip install -r /rift/requirements-3-567.txt

RUN apt clean && \
    rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/*