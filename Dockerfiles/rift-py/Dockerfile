FROM kathara/base

RUN apt update
RUN apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y python3-pip
RUN git clone https://github.com/brunorijsman/rift-python /rift
RUN python3 -m pip install -r /rift/requirements-3-567.txt
