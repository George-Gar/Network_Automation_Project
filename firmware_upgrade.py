from discovery import Discovery
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command

class ios_upgrade(Discovery):

    def __init__(self):
        super().__init__()
        self.ios_file = input("Please enter filename of the firmware you wish to upgrade to: ")

    def get_devices(self) -> list:
        devices = self.static_discovery_inventory()
        return devices
    
    def upgrade_ios(self) -> None:
        self.get_devices()
        nr = InitNornir(config_file='config.yaml')

        #define command
        command = "sh ip int br"

        # Send the command to all devices
        result = nr.run(task=netmiko_send_command, command_string=command)

        for host, task in result.items():
            print(f"Output from {host}:")
            print(task.result)
    


if __name__ == "__main__":
    ios = ios_upgrade()
    ios.upgrade_ios()