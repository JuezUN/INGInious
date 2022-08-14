# DOCKER-VERSION 1.1.0
FROM rockylinux:8

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8

RUN     dnf clean metadata && \
        dnf -y install langpacks-en && \
        dnf -y install epel-release && \
        dnf -y upgrade && \
        dnf -y install python39 python39-pip python39-devel zip unzip tar sed openssh-server openssl bind-utils iproute file jq procps-ng nano && \
        pip3.9 install msgpack pyzmq jinja2 PyYAML timeout-decorator ipython mypy && \
        dnf clean all

# Allow to run commands
ADD     . /INGInious
RUN     chmod -R 755 /INGInious/bin && \
        chmod 700 /INGInious/bin/INGInious && \
        mv /INGInious/bin/* /bin

# Install everything needed to allow INGInious' python libs to be loaded
RUN     chmod -R 644 /INGInious/inginious && \
        mkdir -p /usr/lib/python3.9/site-packages/inginious && \
        cp -R /INGInious/inginious/*.py  /usr/lib/python3.9/site-packages/inginious && \
        echo "inginious" > /usr/lib/python3.9/site-packages/inginious.pth

# Delete unneeded folders
RUN     rm -R /INGInious

# Create worker user
RUN     groupadd --gid 4242 worker && \
        useradd --uid 4242 --gid 4242 worker --home-dir /task

# Set locale params for SSH debug
RUN     echo -e "LANG=en_US.UTF-8\nLANGUAGE=en_US:en\nLC_ALL=en_US.UTF-8" >> /etc/environment
RUN     sed -i.bak '/^AcceptEnv/ d' /etc/ssh/sshd_config

# Set proxy vars in case the agent is behind a proxy
RUN     echo -e "export http_proxy=\"$http_proxy\"\nexport https_proxy=\"$http_proxy\"\nexport HTTP_PROXY=\"$http_proxy\"\nexport HTTPS_PROXY=\"$http_proxy\"\n" >> /etc/profile

CMD ["INGInious"]
