import shlex
import paramiko
from pathlib import Path


class PBSTestsUtils:
    """
    This class provides utilities and helpers to be used inside PBS e2e test.
    """

    def __init__(
        self,
        pbs_head_node: str,
        pbs_sim_node: str,
        pbs_username: str = "mpiuser",
        pbs_password: str = "mpiuser",
    ) -> None:
        self.pbs_head_node = pbs_head_node
        self.pbs_sim_node = pbs_sim_node
        self.pbs_username = pbs_username
        self.pbs_password = pbs_password
        # This is used, so we do not have to reconfigure the PBS in each test if it is already configured by any test.
        self.is_configured = False

    def remote_job_runner(
        self, hostname: str, command: str, username: str = "mpiuser"
    ) -> str:
        """
        This is used to submit commands to the PBS cluster
        """
        with paramiko.SSHClient() as client:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=hostname,
                username=username,
                password=username,
                allow_agent=False,
                look_for_keys=False,
            )
            stdin, stdout, stderr = client.exec_command(command)
            output = "".join(stdout)
            client.close()
            return output.strip()

    def pbs_script(self, runner_serializer) -> str:
        script = """
        #!/bin/bash
        curl -X POST -u admin:admin pbs-sim-node:8000/api/runners/start/ -H 'Content-Type: application/json' -d '{"description": "description_placeholder","crawler": crawler_placeholder}'
        """
        # TODO: use shlex to make me safe
        script = script.replace(
            "description_placeholder", str(runner_serializer["description"])
        )
        # script = script.replace('name_placeholder', runner_serializer["name"])
        # TODO: use shlex to make me safe
        script = script.replace(
            "crawler_placeholder", str(runner_serializer["crawler"])
        )
        return script

    def remove_jobs(self) -> None:
        """
        This method is used as cleaning up the simulations/jobs in the head node.
        """
        create_tmp_directory = (
            f"qselect -u {shlex.quote(self.pbs_username)} | xargs qdel"
        )
        self.remote_job_runner(self.pbs_head_node, create_tmp_directory)

    def register_sim_node(self) -> None:
        """
        Register the simulation node to the head node
        """
        register_command = (
            f"sudo /opt/pbs/bin/qmgr -c 'create node {shlex.quote(self.pbs_sim_node)}'"
        )
        self.remote_job_runner(self.pbs_head_node, register_command)

    def add_pub_key_to_nodes(self) -> None:
        """
        This will add the ssh public key into the head and sim nodes,
         without this step the e2e test machine can not communicate with the nodes
        """
        public_key_path = ".ssh/id_ssh.pub"
        with open(public_key_path, "r") as f:
            public_key = f.read()
        add_pub_key_cmd = f"echo {shlex.quote(public_key)} >> ~/.ssh/authorized_keys"
        self.remote_job_runner(self.pbs_head_node, add_pub_key_cmd)
        self.remote_job_runner(self.pbs_sim_node, add_pub_key_cmd)

    def add_both_nodes_ip_address(self) -> None:
        """
        This method will publish the IP address of bother head and sim nodes to each other,
         without it the nodes can not communicate.
        """
        ip_command = 'hostname -I | awk "{print \\$1}"'
        head_node_ip = self.remote_job_runner(self.pbs_head_node, ip_command)
        sim_node_ip = self.remote_job_runner(self.pbs_sim_node, ip_command)
        sim_command = f"echo '{shlex.quote(head_node_ip)} {shlex.quote(self.pbs_head_node)}' >> /etc/hosts"
        self.remote_job_runner(self.pbs_sim_node, sim_command)
        head_command = f"echo '{shlex.quote(sim_node_ip)} {shlex.quote(self.pbs_sim_node)}' >> /etc/hosts"
        self.remote_job_runner(self.pbs_head_node, head_command)

    def create_ssh_key(self) -> None:
        """
        To communicate with the PBS cluster we need to generate ssh key if it does not exist.
        :return:
        """
        # If there is no ssh key we create one
        Path(".ssh").mkdir(parents=True, exist_ok=True)
        key = paramiko.RSAKey.generate(4096)
        key.write_private_key_file(".ssh/id_ssh")
        key_filename = ".ssh/id_ssh.pub"
        with open(key_filename, "w") as f:
            f.write(f"{key.get_name()} {key.get_base64()}")

    def run_job(self, runner_serializer) -> None:
        job_script = self.pbs_script(runner_serializer)
        qsub_command = f"qsub {job_script} &"
        self.remote_job_runner(self.pbs_head_node, qsub_command)

    def set_up_pbs(self) -> None:
        """
        This is used to set up the PBS cluster correctly.
        This will connect the sim node with the head node.
        """

        # If the pbs is already configured we do not have to rerun the same commands again.
        if self.is_configured:
            pass
        self.create_ssh_key()
        self.add_pub_key_to_nodes()
        self.add_both_nodes_ip_address()
        self.register_sim_node()
        self.is_configured = True
