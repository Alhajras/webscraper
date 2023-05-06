FROM pbs-base-image


RUN sed -i '/PBS_START_COMM=0/c\PBS_START_COMM=1' /etc/pbs.conf
RUN sed -i '/PBS_START_SERVER=0/c\PBS_START_SERVER=1' /etc/pbs.conf
RUN sed -i '/PBS_SERVER=*/c\PBS_SERVER=pbs-head-node' /etc/pbs.conf
RUN sed -i '/\$clienthost */c\$clienthost pbs-head-node' /var/spool/pbs/mom_priv/config


# Generate key non-interactively with no passphrase
RUN ssh-keygen -q -t rsa -N '' <<< ""$'\n'"y" 2>&1 >/dev/null
# So all nodes have SSH access to each other
RUN cat /home/${user}/.ssh/id_rsa.pub >> /home/${user}/.ssh/authorized_keys

ADD entrypoint.sh /home/${user}/entrypoint.sh
RUN chmod 777 /home/${user}/entrypoint.sh
RUN chmod 777 /etc/ssh/sshd_config
RUN chmod 777 /etc/pbs.conf
WORKDIR /home/${user}

RUN mkdir /home/${user}/testingPBSDirectory
RUN chmod 777 /home/${user}/testingPBSDirectory

EXPOSE 22
ENTRYPOINT ["./entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]
