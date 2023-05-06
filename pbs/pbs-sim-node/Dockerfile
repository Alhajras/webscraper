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


# Upgrrade python to 3.10 to run crawlerNode
RUN sudo add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN sudo apt list | grep python3.10
RUN sudo apt-get install -y python3.10
RUN sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN sudo apt install -y python3.10-venv

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

WORKDIR /home/${user}
ADD entrypoint.sh /home/${user}/entrypoint.sh
RUN chmod 777 /home/${user}/entrypoint.sh
RUN chmod 777 /etc/ssh/sshd_config
RUN chmod 777 /etc/pbs.conf

EXPOSE 22
ENTRYPOINT ["./entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]
