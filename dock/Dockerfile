#from ubuntu:yakkety
from ubuntu:xenial

RUN apt-get update && \
    apt-get upgrade -y 

RUN  apt-get install -y \
      curl build-essential git environment-modules \
      python-pip libperl-dev \
      libx11-dev libxpm-dev libxext-dev libxft-dev libglu1-mesa-dev libncurses-dev \
      cmake swig libfreetype6-dev zlibc openssl libcurl4-openssl-dev

RUN apt-get install -y libbz2-dev libtool-bin texinfo automake autopoint libxml2-dev flex bison libssl-dev

#RUN apt-get install -y gcc-4.9 g++-4.9 gfortran-4.9
#RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 50 \
#                          --slave /usr/bin/g++ g++ /usr/bin/g++-4.9 \
#                          --slave /usr/bin/gfortran gfortran /usr/bin/gfortran-4.9

#RUN pip install alibuild
RUN pip install git+https://github.com/alisw/alibuild.git@v1.4.0

RUN useradd -d/home/akubera -u10000 -ms /bin/bash akubera

RUN apt-get remove -y cmake

USER akubera
WORKDIR /home/akubera


#RUN git clone https://github.com/alisw/alidist.git

#RUN aliBuild build boost
#RUN aliBuild build gsl
#RUN aliBuild build fastjet
#RUN aliBuild build root
#RUN aliBuild build aliroot
#RUN aliBuild build aliphysics

