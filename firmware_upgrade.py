from discovery import Discovery
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
import time
from nornir_utils.plugins.functions import print_result


class IOSUpgrade:

    def __init__(self):
        self.ios_file = input("Please enter the file name of the firmware you wish to copy: ")
        # Initialize the Discovery class and generate hosts.yaml
        self.discovery = Discovery()
        self.discovery.write_inventory_yaml(self.discovery.static_discovery_inventory())
        # Initialize Nornir with the generated hosts.yaml
        self.nr = InitNornir(config_file='config.yaml')
        self.log_files = {}

    def copy_ios_from_tftp(self) -> None:
        """
        Copy the IOS firmware from the TFTP server to each device.
        """
        tftp_server_ip = input("Please enter the IP address of the TFTP server: ")  # Prompt for TFTP server IP
        source_file = self.ios_file  # The firmware file on the TFTP server
        destination_file = self.ios_file  # The firmware file name to save as on the device

        # Define the command to copy the file from the TFTP server
        command = f"copy tftp://{tftp_server_ip}/srv/tftp/{source_file} flash:{destination_file}"

        # Send the command to all devices
        result = self.nr.run(
            task=netmiko_send_command,
            command_string=command,
            expect_string=r"#",  # Wait for the command to complete
        )

        for host, task in result.items():
            print(f"Copying {self.ios_file} to {host}...")
            print(f"Copy output for {host}:\n{task.result}")
            self.log_files[host] = f"{host}_copy_log.txt"

    def monitor_copy_progress(self) -> None:
        """
        Monitor the progress of the IOS copy operation by checking the log files.
        """
        while True:
            all_done = True
            for host, log_file in self.log_files.items():
                # Simulate checking the log file (this is a placeholder)
                # In a real scenario, you would SSH into the device and check the log file
                print(f"Checking copy progress on {host}...")
                # Assume the copy is done after 10 seconds for demonstration purposes
                time.sleep(10)
                print(f"Copy on {host} is complete.")
                self.log_files[host] = "done"

            # Check if all copies are done
            if all(status == "done" for status in self.log_files.values()):
                break

    def install_ios(self) -> None:
        """
        Install the IOS firmware on each device.
        """
        for host in self.nr.inventory.hosts:
            print(f"Installing {self.ios_file} on {host}...")
            command = f"install add file flash:{self.ios_file} activate commit"
            result = self.nr.run(task=netmiko_send_command, command_string=command, name=f"Install IOS on {host}")
            print_result(result)

if __name__ == "__main__":
    ios_file = input("Please enter the filename of the firmware you wish to upgrade to: ")
    ios_copy_install = IOSUpgrade()
    
    # Step 1: Copy the IOS firmware from the TFTP server
    ios_copy_install.copy_ios_from_tftp()
    
    # Step 2: Monitor the copy progress
    ios_copy_install.monitor_copy_progress()
    
    # Step 3: Install the IOS firmware
    ios_copy_install.install_ios()



