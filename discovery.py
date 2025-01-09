from nornir.core.inventory import Host
from config_templates import inventory_data
from netmiko import ConnectHandler
from dotenv import load_dotenv
import pprint as p
import json
import yaml
import os

# Load environment variables from the .env file
load_dotenv()

class Discovery:

    def __init__(self):
        self.starting_ip = input('Please enter the IP of the device you are starting discovery on (this IP will be excluded from inventory): ')
        self.network_access_ip = input('Please enter the IP of the connection prividing network access (this IP will be excluded from inventory): ')
        self.excluded_ips = [self.starting_ip, self.network_access_ip]
        self.switch_user = os.environ.get('switch_user')
        self.switch_pass = os.environ.get('switch_pass')
        self.switch_enable = os.environ.get('switch_enable')
        self.inventory = inventory_data['inventory']['hosts']
        self.hosts = []

    
    def device(self) -> dict:
        device = {
            'device_type': 'cisco_ios',  # Specify device type
            'host': self.starting_ip,       # Device IP address
            'username': self.switch_user,          # SSH username
            'password': self.switch_pass,   # SSH password
            'secret': self.switch_enable,   # Enable password (if required)
            'port': 22,                   # Default SSH port (optional)
            }
        return device
    
    def static_discovery(self) -> dict:
        '''
        function for discovering devices and creating an inventory in hosts.yaml if its an initial device configuration
        of switches/routers that are only attached to one switch connected to the network that are giving the rest of
        the switches their base config for automation. 
        '''
        #make the initial connection to the switch & get the cdp neighbors
        net_connect = ConnectHandler(**self.device())
        net_connect.enable()
        neighbors = net_connect.send_command('show cdp neighbors detail', use_textfsm=True)

        #close the connection
        net_connect.disconnect()

        return neighbors

    def static_discovery_inventory(self) -> dict:
        '''
        This function is for creating an inventory files with yaml on a fresh project 
        '''
        
        devices = self.static_discovery()
        
        for device in devices:
            if device.get('mgmt_address') not in self.excluded_ips: 
                self.inventory[device['mgmt_address']] = {}
                self.inventory[device['mgmt_address']]['hostname'] = device['mgmt_address']
                self.inventory[device['mgmt_address']]['port'] = 22
                self.inventory[device['mgmt_address']]['username'] = self.switch_user
                self.inventory[device['mgmt_address']]['password'] = self.switch_pass
                self.inventory[device['mgmt_address']]['platform'] = "cisco_ios"


        return self.inventory

    def write_inventory_yaml(self, data: dict, inventory_type: str = 'hosts'):
        '''
        this function writes to the yaml file and defaults to writing to the hosts yaml file
        '''
        
        file = ''
        if inventory_type == 'hosts': file = 'hosts.yaml' 
        elif inventory_type == 'groups': file = 'groups.yaml'

        # Write to a YAML file
        with open(file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
if __name__ == "__main__":
    #print(json.dumps(Host.schema(), indent=4))
    discover = Discovery()
    data = discover.static_discovery_inventory()
    discover.write_inventory_yaml(data=data)