FROM ubuntu:22.04

RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker
RUN echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker


RUN apt-get update -q && \
	export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends tzdata

RUN dpkg-reconfigure -f noninteractive tzdata

# Install packages
RUN apt-get update -q && \
	export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends wget curl rsync netcat mg vim bzip2 zip unzip gnupg2 && \
    apt-get install -y --no-install-recommends libx11-6 libxcb1 libxau6 && \
    apt-get install -y --no-install-recommends lxde tightvncserver xvfb dbus-x11 x11-utils && \
    apt-get install -y --no-install-recommends xfonts-base xfonts-75dpi xfonts-100dpi && \
    apt-get install -y --no-install-recommends libssl-dev && \
    apt-get install -y python3 aptitude python3.10-venv  python3.10-distutils python3.10-dev && \
    apt-get install -y novnc firefox && \
    apt-get install -y websockify && \
    apt-get install -y net-tools openssh-client git

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -  
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get -y install google-chrome-stable


RUN useradd -ms /bin/bash rpa
USER rpa
WORKDIR /home/rpa
COPY --chown=rpa ./config /home/rpa/.config
COPY --chown=rpa ./extension /home/rpa/extension
COPY --chown=rpa ./app /home/rpa/app

RUN python3 -m venv /home/rpa/.env
ENV PATH=/home/rpa/.env/bin:$PATH
RUN pip install -r /home/rpa/app/requirements.txt


RUN export XKL_XMODMAP_DISABLE=1
RUN export USER=root
RUN export DISPLAY=:1
RUN mkdir -p /home/rpa/.vnc
RUN echo  "/usr/bin/startlxde" > /home/rpa/.vnc/xstartup
RUN chmod a+x /home/rpa/.vnc/xstartup
RUN touch /home/rpa/.vnc/passwd
RUN /bin/bash -c "echo -e 'contem1g\ncontem1g\nn' | vncpasswd" > /home/rpa/.vnc/passwd
RUN chmod 400 /home/rpa/.vnc/passwd
RUN chmod go-rwx /home/rpa/.vnc
RUN /bin/bash -c "echo -e '#!/bin/bash\necho \"starting VNC server ...\"\n'" > /home/rpa/start-vnc-server.sh
RUN /bin/bash -c "echo -e 'export USER=root\n'"  >> /home/rpa/start-vnc-server.sh
RUN /bin/bash -c "echo -e 'websockify -D --web=/usr/share/novnc/  6901 localhost:5901\n'" >> /home/rpa/start-vnc-server.sh
#RUN /bin/bash -c "echo -e 'vncserver :1 -geometry 1280x800 -depth 24 && tail -F /home/rpa/.vnc/*.log\n'" >> /home/rpa/start-vnc-server.sh
RUN /bin/bash -c "echo -e 'vncserver :1 -geometry 1280x800 -depth 24\n'" >> /home/rpa/start-vnc-server.sh
RUN /bin/bash -c "echo -e 'python /home/rpa/app/main.py\n'"  >> /home/rpa/start-vnc-server.sh
RUN touch /home/rpa/.Xauthority
RUN chmod a+x /home/rpa/start-vnc-server.sh

ENV DISPLAY=:1

EXPOSE 5901
EXPOSE 6901

CMD [ "/home/rpa/start-vnc-server.sh" ]

