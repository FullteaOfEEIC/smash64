#libjson-c2
FROM ubuntu:xenial-20170915 AS libjsonc2
RUN apt-get update && apt-get -d -y install libjson-c2

#build inputbot
FROM ubuntu:xenial-20170915 AS inputbot
RUN apt-get update && apt-get install -y\
 build-essential\
 dpkg-dev\
 libwebkitgtk-dev\
 libjpeg-dev\
 libtiff-dev\
 libgtk2.0-dev\
 libsdl1.2-dev\
 libgstreamer-plugins-base0.10-dev\
 libnotify-dev\
 freeglut3\
 freeglut3-dev\
 libjson-c2\
 libjson-c-dev\
 git

RUN git clone https://github.com/mupen64plus/mupen64plus-core
RUN git clone https://github.com/FullteaOfEEIC/mupen64plus-input-bot
WORKDIR /mupen64plus-input-bot
RUN make all && make install

#main image
FROM nvidia/cuda:11.0.3-cudnn8-runtime-ubuntu20.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y\
 python-opengl\
 xvfb\
 ffmpeg\
 wget\
 unrar\
 git\
 cmake\
 curl\
 build-essential\
 libreadline-dev\
 libncursesw5-dev\
 libssl-dev\
 libsqlite3-dev\
 libgdbm-dev\
 libbz2-dev\
 liblzma-dev\
 zlib1g-dev\
 uuid-dev\
 libffi-dev\
 libdb-dev\
 tk-dev\
 mercurial\
 libpng-dev\
 freetype2-demos\
 libmupen64plus2\
 xvfb\
 scrot\
 libjson-c-dev

#install python
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv && cd ~/.pyenv/plugins/python-build && ./install.sh && /usr/local/bin/python-build -v 3.7.4 /usr/local/bin/python && rm -rf ~/.pyenv
ENV PATH $PATH:/usr/local/bin/python/bin

WORKDIR /
RUN pip install --upgrade pip setuptools
RUN pip install\
 keras-rl2\
 gym\
 h5py\
 Pillow\
 gym[atari]\
 gym-notebook-wrapper\
 jupyter\
 tensorflow-gpu==2.4.0\
 opencv-python\
 python-xlib\
 Flask

#install mupen64plus
RUN wget https://github.com/mupen64plus/mupen64plus-core/releases/download/2.5.9/mupen64plus-bundle-linux64-2.5.9.tar.gz
RUN tar -xzf mupen64plus-bundle-linux64-2.5.9.tar.gz
WORKDIR /mupen64plus-bundle-linux64-2.5.9
RUN ./install.sh
COPY rom/* /rom/
COPY [ "savedata/smash.sra", "/root/.local/share/mupen64plus/save/Super Smash Bros. (U) [!].sra" ]

#install libjson
WORKDIR /
RUN git clone https://github.com/json-c/json-c.git
WORKDIR /json-c-build
RUN cmake ../json-c
RUN make && make test && make install

COPY --from=libjsonc2 /var/cache/apt/archives/*.deb /tmp/
RUN apt install /tmp/*.deb

COPY --from=inputbot /mupen64plus-input-bot/mupen64plus-input-bot.so /usr/local/lib/mupen64plus/

#setup jupyter
RUN mkdir -p /root/.jupyter && echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py
RUN echo c.NotebookApp.open_browser = False >> /root/.jupyter/jupyter_notebook_config.py
WORKDIR /mnt
ENV DISPLAY :1
COPY startup.sh /startup.sh
RUN chmod 744 /startup.sh
CMD /startup.sh
