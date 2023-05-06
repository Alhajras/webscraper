#!/bin/bash
sed -i '/PBS_START_COMM=0/c\PBS_START_COMM=1' /etc/pbs.conf
sed -i '/PBS_START_SERVER=0/c\PBS_START_SERVER=1' /etc/pbs.conf
sed -i '/PBS_SERVER=*/c\PBS_SERVER=pbs-head-node' /etc/pbs.conf
sed -i '/\$clienthost */c\$clienthost pbs-head-node' /var/spool/pbs/mom_priv/config
sudo /etc/init.d/pbs start
echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
echo 'PermitEmptyPasswords no' >> /etc/ssh/sshd_config
echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config
exec "$@"
