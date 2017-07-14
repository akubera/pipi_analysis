#from ubuntu:yakkety
from ubuntu:xenial

RUN apt-get update && \
    apt-get upgrade -y 

RUN apt-get install -y \
      curl	\
      git	\
      cmake	\
      openssl	\
      automake	\
      autopoint	\
      flex	\
      bison	\
      texinfo	\
      python-pip	\
      build-essential	\
      gfortran-5	\
      libperl-dev	\
      environment-modules	\
      libx11-dev libxpm-dev libxext-dev libxft-dev libglu1-mesa-dev libncurses-dev \
      libfreetype6-dev zlibc libcurl4-openssl-dev libssl-dev \
      libxml2-dev libtool-bin libbz2-dev


#RUN apt-get install -y gcc-4.9 g++-4.9 gfortran-4.9
#RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 50 \
#                          --slave /usr/bin/g++ g++ /usr/bin/g++-4.9 \
#                          --slave /usr/bin/gfortran gfortran /usr/bin/gfortran-4.9

#RUN pip install alibuild
RUN pip install git+https://github.com/alisw/alibuild.git@v1.4.0

RUN useradd -d/home/akubera -u10000 -ms /bin/bash akubera

RUN ln -s gfortran-5 /usr/bin/gfortran
#RUN apt-get remove -y cmake

USER akubera
WORKDIR /home/akubera

RUN mkdir -p .config/alibuild/disable-analytics
RUN git config --global credential.helper 'cache --timeout=3600'


#RUN aliBuild build boost
#RUN aliBuild build gsl
#RUN aliBuild build fastjet
#RUN aliBuild build root
#RUN aliBuild build aliroot
#RUN aliBuild build aliphysics

