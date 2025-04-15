import os
import logging
from discovery import Discovery
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command, netmiko_file_transfer
import time
from nornir_utils.plugins.functions import print_result


# Enable logging for Netmiko
logging.basicConfig(level=logging.DEBUG)



class IOSUpgrade:

    def __init__(self):
        self.ios_file = "cat9k_iosxe.17.12.04.SPA.bin"
        # Initialize the Discovery class and generate hosts.yaml
        self.discovery = Discovery()
        self.discovery.write_inventory_yaml(self.discovery.static_discovery_inventory())
        # Initialize Nornir with the generated hosts.yaml
        self.nr = InitNornir(config_file='config.yaml')
        self.log_files = {}
    

    def install_ios(self) -> None:
        """
        Install the IOS firmware on each device.
        """
        
        print(f"Installing {self.ios_file}...")
        command = f"install add file flash:{self.ios_file} activate commit prompt-level none"
        result = self.nr.run(task=netmiko_send_command, command_string=command, name=f"Install IOS", read_timeout=600)
        print_result(result)




if __name__ == "__main__":
    ios = IOSUpgrade()
    ios.install_ios()

    
