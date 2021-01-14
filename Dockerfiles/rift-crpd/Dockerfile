FROM crpd-rift

ARG DEBIAN_FRONTEND="noninteractive"
RUN apt update
RUN apt install -y \
    wget \
    xz-utils \
    make \
    gcc \
    bison \
    flex

RUN FILE_NAME=`wget -q -O - https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/ | \
        tac | \
        grep -m 1 -o "iproute2-5[\.0-9]*[0-9]" | \
        head -n 1` && \
    wget -q https://mirrors.edge.kernel.org/pub/linux/utils/net/iproute2/$FILE_NAME.tar.xz && \
    tar xf $FILE_NAME.tar.xz && \
    cd $FILE_NAME && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -r $FILE_NAME && \
    rm $FILE_NAME.tar.xz

RUN apt remove -y \
    wget \
    xz-utils \
    make \
    gcc \
    bison \
    flex

RUN apt clean && \
    rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/*