FROM ubuntu:18.04 as pbs-base-image

RUN apt-get update
RUN apt-get install -y openssh-server \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
    gcc \
    make \
    libtool \
    libhwloc-dev \
    libx11-dev \
    libxt-dev \
    libedit-dev
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y libical-dev
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y  postgresql-contrib
RUN apt-get install -y ncurses-dev perl \
    postgresql-server-dev-all \
    python3-dev \
    tcl-dev \
    tk-dev \
    swig \
    libexpat-dev \
    libssl-dev \
    libxext-dev \
    libxft-dev \
    autoconf \
    automake \
    expat \
    libedit2 \
    postgresql \
    python3 \
    sendmail-bin \
    tcl
RUN apt-get install -y tk \
    libical3 \
    sudo \
    build-essential \
    wget \
    bash \
    apt-transport-https \
    ca-certificates \
    gnupg-agent \
    software-properties-common \
    sshpass \
    sshfs

RUN mkdir /var/run/sshd
ENV user mpiuser

RUN useradd -m -d /home/${user} ${user} && \
                        chown -R ${user} /home/${user} && \
                        adduser ${user} sudo && \
                        echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ${user}
SHELL ["/bin/bash", "-c"]
WORKDIR /home/${user}

# Generate key non-interactively with no passphrase
RUN ssh-keygen -q -t rsa -N '' <<< ""$'\n'"y" 2>&1 >/dev/null
# So all nodes have SSH access to each other
RUN cat /home/${user}/.ssh/id_rsa.pub >> /home/${user}/.ssh/authorized_keys

USER root

#PBS installation steps
RUN wget https://github.com/openpbs/openpbs/archive/refs/tags/v20.0.1.tar.gz
RUN tar -xpvf v20.0.1.tar.gz
WORKDIR openpbs-20.0.1/
RUN ./autogen.sh
RUN ./configure --prefix=/opt/pbs
RUN make
RUN sudo make install
RUN sudo /opt/pbs/libexec/pbs_postinstall

# Installing MPI doesn't add it to the path
USER root
RUN echo -e "mpiuser\nmpiuser" | passwd ${user}

RUN chsh -s /bin/bash ${user}

USER ${user}
SHELL ["/bin/bash", "-c"]
USER root

RUN sed -i '/]] && sys_pgsql_ver=*/c\#Bug in PBS' /opt/pbs/libexec/pbs_habitat
RUN sed -i '/ulimit -l unlimited/c\' /opt/pbs/lib/init.d/limits.pbs_mom
RUN echo "" > /opt/pbs/lib/init.d/limits.post_services
RUN sudo chmod 4755 /opt/pbs/sbin/pbs_iff /opt/pbs/sbin/pbs_rcp
RUN sudo sysctl -w fs.inotify.max_user_watches=100000

RUN sed -i "/^PATH=/c\PATH=/home/mpiuser/mpich-3.2-install/bin/:/opt/pbs/sbin:/opt/pbs/bin/:$PATH" /etc/environment
