"""Creating custom tools for agents."""

from langchain_core.tools import tool
import ipaddress


@tool
def calculate_subnet(cidr: str) -> str:
    """Calculate subnet details from CIDR notation. Input should be like '192.168.1.0/24'."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return f"""
Subnet Details for {cidr}:
  Network Address: {network.network_address}
  Broadcast Address: {network.broadcast_address}
  Subnet Mask: {network.netmask}
  Wildcard Mask: {network.hostmask}
  Total Hosts: {network.num_addresses}
  Usable Hosts: {network.num_addresses - 2 if network.num_addresses > 2 else 0}
  First Usable: {list(network.hosts())[0] if network.num_addresses > 2 else 'N/A'}
  Last Usable: {list(network.hosts())[-1] if network.num_addresses > 2 else 'N/A'}
"""
    except ValueError as e:
        return f"Error: {str(e)}"


@tool
def lookup_vlan(vlan_id: int) -> str:
    """Look up VLAN information by ID. Returns VLAN name and associated subnets."""
    vlan_db = {
        10: {"name": "USERS", "subnet": "192.168.10.0/24", "gateway": "192.168.10.1"},
        20: {"name": "SERVERS", "subnet": "192.168.20.0/24", "gateway": "192.168.20.1"},
        30: {"name": "MANAGEMENT", "subnet": "192.168.30.0/24", "gateway": "192.168.30.1"},
        99: {"name": "NATIVE", "subnet": "192.168.99.0/24", "gateway": "192.168.99.1"},
        100: {"name": "VOICE", "subnet": "10.10.100.0/24", "gateway": "10.10.100.1"},
    }

    if vlan_id in vlan_db:
        vlan = vlan_db[vlan_id]
        return f"VLAN {vlan_id}: Name={vlan['name']}, Subnet={vlan['subnet']}, Gateway={vlan['gateway']}"
    else:
        return f"VLAN {vlan_id} not found in database"


@tool
def check_port_status(interface: str) -> str:
    """Check the status of a network interface. Input should be like 'GigabitEthernet0/1'."""
    interfaces = {
        "GigabitEthernet0/1": {"status": "up", "vlan": 10, "speed": "1000Mbps", "duplex": "full"},
        "GigabitEthernet0/2": {"status": "down", "vlan": 20, "speed": "auto", "duplex": "auto"},
        "GigabitEthernet0/3": {"status": "up", "vlan": 30, "speed": "100Mbps", "duplex": "half"},
        "GigabitEthernet0/4": {"status": "admin down", "vlan": 1, "speed": "auto", "duplex": "auto"},
    }

    if interface in interfaces:
        port = interfaces[interface]
        return f"{interface}: Status={port['status']}, VLAN={port['vlan']}, Speed={port['speed']}, Duplex={port['duplex']}"
    else:
        return f"Interface {interface} not found"


if __name__ == "__main__":
    print("Testing Custom Tools")
    print("=" * 50)

    print("\n1. Subnet Calculator:")
    print(calculate_subnet.invoke({"cidr": "10.0.0.0/22"}))

    print("\n2. VLAN Lookup:")
    print(lookup_vlan.invoke({"vlan_id": 10}))
    print(lookup_vlan.invoke({"vlan_id": 20}))
    print(lookup_vlan.invoke({"vlan_id": 999}))

    print("\n3. Port Status:")
    print(check_port_status.invoke({"interface": "GigabitEthernet0/1"}))
    print(check_port_status.invoke({"interface": "GigabitEthernet0/2"}))