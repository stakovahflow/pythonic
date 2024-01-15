#!/usr/bin/env python3
# Last modified: 2024-01-15 @ 09:36
version = 20240115001
import subprocess
import ipaddress
import os
import yaml
import argparse
import sys
import logging
import psutil
from datetime import datetime

# Set global variables:
config_dir = "/etc/netplan/"

# Application name"
application_name = sys.argv[0]

# Configure logging
def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    user_message_format = '%(message)s'

    # File Handler - for log file
    file_handler = logging.FileHandler('/var/log/netplanner.log')
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging.DEBUG)

    # Stream Handler - for console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(user_message_format))
    stream_handler.setLevel(logging.INFO)

    # Get the root logger and add both handlers
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

# Call the function to set up logging at the start of your script
setup_logging()


def timestamp():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return timestamp

def backup_interface_configurations(config_dir):
    filename = f'/var/log/netplan-backup-{timestamp()}.tgz'
    logging.info(f'Backing up {config_dir} to {filename}')
    try:
        status = subprocess.run(['tar', '-cvzf', filename, config_dir], capture_output=True, text=True, check=True)
        logging.info(f'Backup created: {filename}')
        logging.info(f'To restore this configuration, run: sudo {application_name} --restore {filename}')
    except Exception as e:
        logging.error(f'An error occurred when extracting {filename}: ', e)
    logging.debug(f'Output of {filename} extraction:')
    status_lines = status.stdout.splitlines()
    for line in status_lines:
        logging.debug(line)

def restore_interface_configuration(filename, config_dir):
    logging.info(f'Attempting to restore files from backup {filename}:')
    logging.debug(f'Removing current configuration files from {config_dir}')
    for file in os.listdir(config_dir):
        filepath = os.path.join(config_dir, file)
        try:
            os.remove(filepath)
        except Exception as e:
            logging.error(f"An error occurred when removing files in {config_dir}:", e)
    try:
        logging.debug(f'Attempting to extract tarball {filename}')
        status = subprocess.run(['tar', '-C', '/', '-xvzf', filename], capture_output=True, text=True, check=True)
        logging.info(f'Backup restored: {filename}')
    except Exception as e:
        logging.error(f'An error occurred when extracting {filename}: ', e)
    logging.debug(f'Output of {filename} extraction:')
    status_lines = status.stdout.splitlines()
    for line in status_lines:
        logging.debug(line)


def get_interfaces():
    try:
        result = subprocess.run(['ip', '-br', 'addr'], capture_output=True, text=True, check=True)
        interfaces = result.stdout.splitlines()
        return [line.split()[0] for line in interfaces if not line.startswith("lo") and not line.startswith("docker")]
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting interfaces: {e}")
        return []
    except Exception as e:
        logging.error(f"Error getting interfaces: {e}")
        return []

def show_current_config(iface):
    try:
        result = subprocess.run(['ip', 'addr', 'show', iface], capture_output=True, text=True, check=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error showing current configuration for {iface}: {e}")

def validate_ip_cidr(ip_cidr):
    try:
        ipaddress.IPv4Interface(ip_cidr)
        logging.debug(f'Interface CIDR: Valid')
        return True
    except ipaddress.AddressValueError:
        logging.error(f'Interface CIDR: Invalid')
        return False

def validate_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        logging.debug(f'Interface Address: Valid')
        return True
    except ipaddress.AddressValueError:
        logging.error(f'Interface Address: Invalid')
        return False


def get_network_details(interfaces,interface=None):
    while True:
        try:
            iface = ''
            if interface:
                if interface in interfaces:
                    logging.info(f"Configuring network interface: {interface}")
                    iface = interface
                else:
                    logging.error(f"Unable to find specified interface: {interface}")
            if not iface:
                print("Available interfaces:", ', '.join(interfaces))
                try:
                    iface = input("Enter the network interface (e.g., eth0): ").lower()
                except KeyboardInterrupt:
                    logging.error('\nOperation cancelled by user. Exiting... (get_network_details)')
                    exit(1)
                except Exception as e:
                    logging.error('Unknown error occurred', e)
                    exit(1)
            if iface not in interfaces:
                logging.error("Invalid interface. Please try again.")
                continue

            show_current_config(iface)

            config_type = input("Choose configuration type (dhcp/static/none): ").lower()
            if config_type not in ["dhcp", "static", "none"]:
                logging.error("Invalid configuration type. Please try again.")
                continue

            mtu = input("Enter MTU (hit enter for default): ")
            if mtu and (not mtu.isdigit() or int(mtu) < 0):
                logging.error("Invalid MTU. Please enter a positive numeric value.")
                continue

            if config_type == "static":
                cidr_examples ="""Common masks & CIDR notation:
    CIDR: Mask:
    16    255.255.0.0 *
    17    255.255.128.0
    18    255.255.192.0
    19    255.255.224.0
    20    255.255.240.0
    21    255.255.248.0
    22    255.255.252.0
    23    255.255.254.0
    24    255.255.255.0 ***
    25    255.255.255.128
    26    255.255.255.192
    27    255.255.255.224
    28    255.255.255.240
    29    255.255.255.248
    30    255.255.255.252
    """
                while True:
                    logging.debug(f"Getting IP address for interface {iface} from stdin")
                    ip = input("Enter the IP address (e.g., 192.168.1.10): ")
                    print(cidr_examples)
                    prefix_length = input("Enter the network prefix length (/24, 24): ").strip()
                    if prefix_length.startswith("/"):
                        prefix_length = prefix_length[1:]
                    if not prefix_length.isdigit() or int(prefix_length) < 0 or int(prefix_length) > 32:
                        logging.error("Invalid network CIDR prefix length. Please enter a numeric value between 0 and 32.")
                        continue

                    ip_cidr = f"{ip}/{prefix_length}"
                    if not validate_ip_cidr(ip_cidr):
                        logging.error("Invalid IP address or network prefix. Please try again.")
                        continue
                    else:
                        break

                while True:
                    gateway = input("Enter the gateway address: ")
                    if not validate_ip(gateway):
                        logging.error("Invalid gateway address. Please try again.")
                        continue
                    else:
                        break

                dns_input = input("Enter DNS addresses (comma-separated, hit enter if none): ")
                dns = [dns.strip() for dns in dns_input.split(',') if validate_ip(dns.strip())]
                
                return iface, config_type, ip_cidr, gateway, dns, mtu
            else:
                return iface, config_type, None, None, None, mtu
        except KeyboardInterrupt:
            logging.error('\nOperation cancelled by user. Exiting... (get_network_details)')
            exit(1)
        except Exception as e:
            logging.error(f'An error occurred when running (get_network_details):', e)
            exit(1)

def generate_netplan_config(iface, config_type, ip_cidr, gateway, dns, mtu):
    mtu_config = f"mtu: {mtu}" if mtu else ""
    if config_type == "static":
        dns_entries = ", ".join(dns)
        config = f"""network:
  version: 2
  ethernets:
    {iface}:
      dhcp4: no
      addresses: [{ip_cidr}]
      gateway4: {gateway}
      nameservers:
        addresses: [{dns_entries}]
      {mtu_config}
"""
    elif config_type == "dhcp":
        config = f"""network:
  version: 2
  ethernets:
    {iface}:
      dhcp4: yes
      {mtu_config}
"""
    else:  # config_type == "none"
        config = f"""network:
  version: 2
  ethernets:
    {iface}:
      dhcp4: no
      {mtu_config}
"""
    return config


def view_netplan_configs(config_dir):
    for filename in os.listdir(config_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(config_dir, filename)
            try:
                logging.info(f"Netplan Configuration: {filepath}")
                with open(filepath,'r') as file:
                    for line in file:
                        logging.info(line.strip('\n'))
                file.close()
            except Exception as e:
                print(f"Error reading file {filepath}: {e}")

# Clean-up function for all configuration files:
def clean_up_netplan_configs(config_dir):
    for filename in os.listdir(config_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(config_dir, filename)
            try:
                with open(filepath, 'r') as file:
                    data = yaml.safe_load(file)
                    if is_file_almost_blank(data):
                        os.remove(filepath)
                        print(f"Removed almost blank configuration file: {filename}")
            except yaml.YAMLError as exc:
                print(f"Error processing {filename}: {exc}")
            except Exception as e:
                print(f"Error removing file {filename}: {e}")

# Find files that are missing any network interface configuration details
def is_file_almost_blank(data):
    # Define what constitutes an 'almost blank' file.
    # This includes files that only have the 'version', and optionally 'renderer', but no 'ethernets' or empty 'ethernets'.
    if 'network' not in data:
        return True  # No 'network' section makes the file almost blank.

    network_section = data['network']
    # Check if 'ethernets' section is missing or empty
    if 'ethernets' not in network_section or not network_section['ethernets']:
        # Also check that no other keys (like 'wifis', 'bridges', etc.) are present
        allowed_keys = {'version', 'renderer', 'ethernets'}
        return all(key in allowed_keys for key in network_section)
    return False

# Remove network interface configuration from a single configuration file:
def remove_interface_single_config(interface, filepath):
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
            if 'network' in data and 'ethernets' in data['network'] and interface in data['network']['ethernets']:
                del data['network']['ethernets'][interface]
                if not data['network']['ethernets']:
                    del data['network']['ethernets']
                if not data['network']:
                    os.remove(filepath)
                else:
                    with open(filepath, 'w') as file:
                        yaml.dump(data, file, default_flow_style=False)
                logging.info(f"Removed configuration for {interface} from {filepath}")
    except yaml.YAMLError as exc:
        print(f"Error processing {filepath}: {exc}")
    except IOError as e:
        print(f"Could not open or write to file {filepath}: {e}")

# Remove network interface configuration from all configuration files in (config_dir) - /etc/netplan:
def remove_interface_all_configs(interface, config_dir):
    for filename in os.listdir(config_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = f'{config_dir}/{filename}'
            try:
                remove_interface_single_config(interface, filepath)
            except yaml.YAMLError as exc:
                print(f"Error processing {filename}: {exc}")
            except IOError as e:
                print(f"Could not open or write to file {filename}: {e}")

# Provide a list of all files containing a specific interface name:
def list_files_with_interface(interface_name, config_dir):
    """
    List files in the given directory that contain the specified interface name.
    Args:
        interface_name (str): The interface name to search for.
        config_dir (str): The directory containing configuration files.

    Returns:
        list: A list of file paths that contain the interface name.
    """
    matching_files = []
    
    for filename in os.listdir(config_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(config_dir, filename)
            try:
                with open(filepath, 'r') as file:
                    data = yaml.safe_load(file)
                    if 'network' in data and 'ethernets' in data['network']:
                        ethernets = data['network']['ethernets']
                        if interface_name in ethernets:
                            matching_files.append(filepath)
            except yaml.YAMLError as exc:
                print(f"Error processing {filename}: {exc}")
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
    
    return matching_files

# Display all configuration data within a specific file:
def display_config(config, filename):
    # Display the interface configuration
    print(f"Configuration in {filename}:")
    print(yaml.dump(config, default_flow_style=False))

# Provide a sanity check for potential network interface configuration conflicts:
def sanity_check(config_dir):
    interface_files = {}  # Dictionary to store the files where each interface is defined
    # Iterate through the configuration files
    for filename in os.listdir(config_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(config_dir, filename)
            try:
                with open(filepath, 'r') as file:
                    data = yaml.safe_load(file)
                    if 'network' in data and 'ethernets' in data['network']:
                        # Iterate through ethernets in the configuration
                        for iface in data['network']['ethernets']:
                            if iface in interface_files.keys():
                                # Add the file where the conflict occurs to the list for each interface
                                interface_files[iface].append(filename)
                            else:
                                # Initialize the list of files for each interface
                                interface_files[iface] = [filename]
            except yaml.YAMLError as exc:
                print(f"Error processing {filename}: {exc}")
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
    for interface_file in interface_files:
        print(f'{interface_file}')
    return interface_files

# Provide the user with options to clean up conflicts among files
def clean_up_conflicts(conflicts):
    interfaces = get_interfaces()
    for interface, conflict_info in conflicts.items():
        files_with_conflict = conflict_info
        unique_files = list(set(files_with_conflict))
        if len(unique_files) > 1:
            clean_up_method = ''
            clean_up_methods = ['m','c','d','i']
            while clean_up_method not in clean_up_methods: # Loop until a valid selection is made
                print("(m) Manually address configuration file conflicts (exits)")
                print("(c) Create new network interface configuration file")
                print("(d) Delete network interface configuration from all existing files (and clear empty files)")
                print("(i) Interactively select which configuration to keep")
                print("How would you like to proceed in cleaning up the network configuration conflicts? ")
                clean_up_method = input("Please select 1 option: (m/c/d/i)   ").lower()
                if clean_up_method == 'm':        # Manual
                    print(f"Exiting now without making changes")
                    exit(0)
                elif clean_up_method == 'c':      # Create new configuration
                    print(f"You will be prompted for configuration details for {interface}")
                    new_interface(interface, interfaces)
                elif clean_up_method == 'd':      # Delete all network configurations for affected interface definitions
                    remove_interface_all_configs(interface, config_dir)
                elif clean_up_method == 'i':      # Interactively select the configuration file to keep
                    print(f"Conflicting netplan configurations found for interface '{interface}':")
                    # get the index (number) and filename of the unique files containing specific network interface configuration details
                    for idx, conflict_file in enumerate(unique_files): 
                        print(f"{idx + 1}. {conflict_file}")
                    while True:
                        try:
                            choice = int(input(f"Which configuration do you want to keep for interface {interface}? (Enter the number): "))
                            if choice < 1 or choice > len(unique_files):
                                print("Invalid choice. Please enter a valid number.")
                            else:
                                # Keep the selected configuration and remove the others
                                selected_file = unique_files[choice - 1]
                                for file_to_remove in files_with_conflict:
                                    file_to_remove_path = f'{config_dir}/{file_to_remove}'
                                    # Check if the interface name matches the current interface
                                    if file_to_remove != selected_file:
                                        remove_interface_single_config(interface, file_to_remove_path)
                                break
                        except ValueError:
                            print("Invalid input. Please enter a number.")
        else:
            print(f"No conflicting configurations found for {interface}")

# Apply the configuration 
def apply_configuration(interface, config_dir, config):
    config_path = f"{config_dir}/{interface}.yaml"

    if not remove_interface_all_configs(interface, config_dir):
        print(f"No existing configuration found for {interface}. Proceeding with new configuration.")

    try:
        with open(config_path, "w") as file:
            file.write(config)
        subprocess.run(["netplan", "try"], check=True)
        subprocess.run(["netplan", "apply"], check=True)
    except Exception as e:
        logging.error(f"An error occurred while applying the configuration: {e}")

def new_interface(interface, interfaces):
    interfaces = get_interfaces()
    iface, config_type, ip_cidr, gateway, dns, mtu = get_network_details(interfaces, interface)
    logging.debug([f'Received settings for netplan configuration: {iface}, {config_type}, {ip_cidr}, {gateway}, {dns}, {mtu}'])
    config = generate_netplan_config(iface, config_type, ip_cidr, gateway, dns, mtu)
    logging.info("Generated configuration:\n")
    logging.info(config)

    apply = input("Apply this configuration? (yes/no): ").lower()
    if apply == "yes" or apply == 'y':
        try:
            logging.info("Attempting to remove any unnecessary netplan configuration files:")
            clean_up_netplan_configs(config_dir)
        except Exception as e:
            logging.info("An error occurred when attempting to clean netplan configuration files", e)
        apply_configuration(iface, config_dir, config)
        if config_type == "none":
            logging.debug(f"Prompting user for promiscous configuration for interface {iface}")
            promiscuous = input(f'Enable promiscuous mode for interface {iface}? (yes/no) ').lower()
            if promiscuous == 'y' or promiscuous == 'yes':
                logging.debug(f'Promiscuous mode selected for interface: {iface}')
                subprocess.run(["ip", "link", "set", iface, "promisc", "on"], check=True)
                logging.info(f'Promiscuous mode enabled for interface: {iface}')
                logging.info(f'(Please note that promiscuous mode is not persistent across many netplan-enabled systems.)')
            else:
                logging.debug(f'Promiscuous mode not selected for interface: {iface}')
                subprocess.run(["ip", "link", "set", iface, "promisc", "off"], check=True)
                logging.info(f'Promiscuous mode disabled for interface: {iface}')
        print(f"Configuration applied for {iface}.")

    else:
        logging.info("Configuration not applied.")

def main():
    # Ensure we're running as root user:
    if os.geteuid() != 0:
        print(f"{sys.argv[0]} must be run with root (sudo) permissions")
        exit(1)

    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Create or append to a CSV file with base64-encoded credentials.")
        parser.add_argument("-V", "--version", action="store_true", help="Show version information and exit")
        parser.add_argument("-v", "--view", action="store_true", help="View network configuration(s)")
        parser.add_argument("-l", "--list", action="store_true", help="List available network interfaces")
        parser.add_argument("-i", "--interface", default=None, help="Specific Interface")
        parser.add_argument("-g", "--generate", action="store_true", help="Generate new netplan configuration")
        parser.add_argument("-r", "--remove", action="store_true", help="Remove netplan configuration for a specific interface")
        parser.add_argument("-c", "--clean", action="store_true", help="Clean netplan configurations")
        parser.add_argument("--backup", action="store_true", help="Backup netplan configurations")
        parser.add_argument("--restore", help="Restore netplan configurations from tgz backup")
        parser.add_argument("-s", "--sanity", action="store_true", help="Perform sanity-check on netplan configurations")
    except Exception as e:
        logging.error(f"Error getting arguments: {e}")
    
    # Let's put it all together:
    try:
        # Get the filename and command line arguments
        args = parser.parse_args()
        # Done collecting command line arguments
        interface = args.interface
        interfaces = get_interfaces()

        # Let's collect our command line arguments

        if args.interface:
            logging.debug(f"Interface selected via CLI argument: {args.interface}")

        if not interfaces:
            logging.info("No network interfaces found.")
            return
        
        if args.version:
            logging.info(f'{application_name} version number: {version}')
            exit(0)
        elif args.list:
            logging.debug("Listing interface configurations: ")
            i = 0
            for interface in get_interfaces():
                print(f"{i}: {interface}")
                i+=1
            exit(0)
        elif args.view:
            logging.debug("View interface configuration: ")
            view_netplan_configs(config_dir)
            exit(0)
        elif args.backup:
            logging.info(f"Backing up netplan configuration files")
            backup_interface_configurations(config_dir)
            exit(0)
        elif args.sanity:
            logging.debug("Looking for conflicting interface configuration entries")
            conflicts = sanity_check(config_dir)
            for iface, files in conflicts.items():
                if len(files) > 1:
                    logging.info(f"Conflicting netplan configurations found for interface '{iface}':")
                    for conflict_file in files:
                        logging.info(f"  - {conflict_file}")
        elif args.restore:
            try:
                filename = args.restore
                logging.info(f"Restoring netplan configuration files")
                restore_interface_configuration(filename, config_dir)
            except FileNotFoundError as fnf:
                logging.error(f"Unable to find file {filename}: {fnf}")
            except Exception as e:
                logging.error(f"Unable to restore backup from file: {filename}")
                logging.error(e)
        
        elif args.remove:
            backup_interface_configurations(config_dir)
            logging.debug(f"Removing interface {interface} configuration: ")
            remove_interface_all_configs(interface, config_dir)
            clean_up_netplan_configs(config_dir)
            exit(0)

        elif args.clean:
            backup_interface_configurations(config_dir)
            logging.debug("Cleaning interface configuration: ")
            clean_up_netplan_configs(config_dir)
            conflicts = sanity_check(config_dir)
            clean_up_conflicts(conflicts)
            clean_up_netplan_configs(config_dir)
            exit(0)

        else:
            print('Top level function not selected.')
            new_interface(interface, interfaces)
            
    except KeyboardInterrupt:
        logging.info("\nOperation cancelled by user. Exiting... (main)")
        exit(1)

if __name__ == "__main__":
    main()
