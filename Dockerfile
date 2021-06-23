FROM ubuntu:xenial-20170915 as statifier
RUN apt-get update && apt-get install -y\
 wget\
 build-essential

WORKDIR /
RUN wget https://sourceforge.net/projects/statifier/files/latest/download #latest 1.7.4 (at 2021/6/17)
RUN tar -zxf download
WORKDIR /statifier-1.7.4
RUN chmod 777 *
RUN ./configure && make
RUN ls

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
RUN git clone https://github.com/kevinhughes27/mupen64plus-input-bot
WORKDIR /mupen64plus-input-bot
RUN make all && make install

FROM nvidia/cuda:11.0.3-cudnn8-runtime-ubuntu20.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y\
 python-opengl\
 xvfb\
 ffmpeg\
 wget\
 unrar\
 git\
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
 mercurial\
 libpng-dev\
 freetype2-demos\
 libmupen64plus2\
 xvfb

RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv && cd ~/.pyenv/plugins/python-build && ./install.sh && /usr/local/bin/python-build -v 3.7.4 /usr/local/bin/python && rm -rf ~/.pyenv
ENV PATH $PATH:/usr/local/bin/python/bin

RUN wget https://github.com/mupen64plus/mupen64plus-core/releases/download/2.5.9/mupen64plus-bundle-linux64-2.5.9.tar.gz
RUN tar -xzf mupen64plus-bundle-linux64-2.5.9.tar.gz
WORKDIR /mupen64plus-bundle-linux64-2.5.9
RUN ./install.sh

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
 PyYAML\
 termcolor\
 mss

RUN mkdir -p /root/.jupyter && echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py
RUN echo c.NotebookApp.open_browser = False >> /root/.jupyter/jupyter_notebook_config.py

COPY --from=inputbot /mupen64plus-input-bot/mupen64plus-input-bot.so /usr/local/lib/mupen64plus/

WORKDIR /mnt
CMD jupyter notebook --allow-root --NotebookApp.token=''
