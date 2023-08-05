FROM pbs-base-image


RUN sed -i '/PBS_START_MOM=*/c\PBS_START_MOM=1' /etc/pbs.conf
RUN sed -i '/PBS_START_SERVER=*/c\PBS_START_SERVER=0' /etc/pbs.conf
RUN sed -i '/PBS_START_COMM=*/c\PBS_START_COMM=0' /etc/pbs.conf
RUN sed -i '/PBS_START_SCHED=*/c\PBS_START_SCHED=0' /etc/pbs.conf
RUN sed -i '/\$clienthost */c\$clienthost pbs-sim-node' /var/spool/pbs/mom_priv/config


# Generate key non-interactively with no passphrase
RUN ssh-keygen -q -t rsa -N '' <<< ""$'\n'"y" 2>&1 >/dev/null
# So all nodes have SSH access to each other
RUN cat /home/${user}/.ssh/id_rsa.pub >> /home/${user}/.ssh/authorized_keys


# Step 3: Download and install Python 3.10
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz && \
    tar -xzf Python-3.10.0.tgz && \
    cd Python-3.10.0 && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf Python-3.10.0*

# Step 4: Create a virtual environment and set its location
ENV VIRTUAL_ENV=/opt/venv
RUN python3.10 -m venv $VIRTUAL_ENV

# Step 5: Add the virtual environment's binary directory to PATH
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install crawlNode
WORKDIR /home/${user}
RUN sudo apt-get install unzip
RUN wget https://github.com/Alhajras/webscraper/archive/refs/heads/main.zip
RUN unzip main.zip
RUN rm main.zip
WORKDIR webscraper-main
RUN rm -r frontend/ pbs/ Report/
WORKDIR backend/webscraper/
RUN python3 -m venv venv
RUN /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Install chromedriver
RUN sudo apt update
RUN sudo apt install -y chromium-chromedriver xvfb

WORKDIR /home/${user}
ADD entrypoint.sh /home/${user}/entrypoint.sh
RUN chmod 777 /home/${user}/entrypoint.sh
RUN chmod 777 /etc/ssh/sshd_config
RUN chmod 777 /etc/pbs.conf

EXPOSE 22
ENTRYPOINT ["./entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]
