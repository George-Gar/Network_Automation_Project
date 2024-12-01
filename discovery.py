from netmiko import ConnectHandler
import nornir
import yaml
import os


class Discovery:

    def __init__(self):
        self.starting_ip = input('Please enter the IP of the device you are starting discovery on (this IP will be excluded from inventory): ')
        self.network_access_ip = input('Please enter the IP of the connection prividing network access (this IP will be excluded from inventory): ')
        self.excluded_ips = [self.starting_ip, self.network_access_ip]

    
    def device(self) -> dict:
        device = {
            'device_type': 'cisco_ios',  # Specify device type
            'host': self.starting_ip,       # Device IP address
            'username': os.environ.get('switch_user'),          # SSH username
            'password': os.environ.get('switch_pass'),   # SSH password
            'secret': os.environ.get('switch_enable'),   # Enable password (if required)
            'port': 22,                   # Default SSH port (optional)
            }
        return device
    
    def static_discovery(self):
        '''
        function for discovering devices and creating an inventory in hosts.yaml if its an initial device configuration
        of switches/routers that are only attached to one switch connected to the network that are giving the rest of
        the switches their base config for automation. 
        '''
        #make the initial connection to the switch & get the cdp neighbors
        net_connect = ConnectHandler(**self.device())
        net_connect.enable()
        neighbors = net_connect.send_command('show cdp neighbors')

        #close the connection
        net_connect.disconnect()

        return neighbors


    
if __name__ == "__main__":
    discover = Discovery()
    print(discover.static_discovery())