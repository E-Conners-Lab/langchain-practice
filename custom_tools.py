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


@tool
def ping_check(target: str) -> str:
    """Simulate a ping check to a target IP or hostname."""
    # Simulated ping results
    ping_db = {
        "192.168.10.1": {"status": "success", "latency": "1ms", "packet_loss": "0%"},
        "192.168.20.1": {"status": "success", "latency": "2ms", "packet_loss": "0%"},
        "192.168.30.1": {"status": "timeout", "latency": "N/A", "packet_loss": "100%"},
        "8.8.8.8": {"status": "success", "latency": "15ms", "packet_loss": "0%"},
        "10.0.0.1": {"status": "success", "latency": "1ms", "packet_loss": "0%"},
    }

    if target in ping_db:
        result = ping_db[target]
        return f"Ping {target}: {result['status']}, Latency: {result['latency']}, Packet Loss: {result['packet_loss']}"
    else:
        return f"Ping {target}: host unreachable"


@tool
def get_routing_table(device: str) -> str:
    """Get the routing table for a device."""
    routing_tables = {
        "R1": """
Destination      Gateway         Interface        Protocol
0.0.0.0/0        10.0.0.1        Gi0/0           static
192.168.10.0/24  connected       Gi0/1           connected
192.168.20.0/24  192.168.1.2     Gi0/0           OSPF
192.168.30.0/24  192.168.1.3     Gi0/0           OSPF
10.0.0.0/8       connected       Gi0/0           connected""",
        "R2": """
Destination      Gateway         Interface        Protocol
0.0.0.0/0        10.0.0.1        Gi0/0           OSPF
192.168.10.0/24  192.168.1.1     Gi0/0           OSPF
192.168.20.0/24  connected       Gi0/1           connected
192.168.30.0/24  192.168.1.3     Gi0/0           OSPF""",
        "SW1": """
Destination      Gateway         Interface        Protocol
0.0.0.0/0        192.168.10.1    VLAN10          static
192.168.10.0/24  connected       VLAN10          connected""",
    }

    if device in routing_tables:
        return f"Routing table for {device}:\n{routing_tables[device]}"
    return f"Device {device} not found"


@tool
def get_ospf_neighbors(device: str) -> str:
    """Get OSPF neighbor information for a device."""
    ospf_data = {
        "R1": """
Neighbor ID     State       Address         Interface
192.168.1.2     FULL/DR     192.168.1.2     Gi0/0
192.168.1.3     FULL/BDR    192.168.1.3     Gi0/0""",
        "R2": """
Neighbor ID     State       Address         Interface
192.168.1.1     FULL/BDR    192.168.1.1     Gi0/0
192.168.1.3     FULL/DR     192.168.1.3     Gi0/0""",
        "R3": """
Neighbor ID     State       Address         Interface
192.168.1.1     FULL/DR     192.168.1.1     Gi0/0
192.168.1.2     FULL/BDR    192.168.1.2     Gi0/0""",
    }

    if device in ospf_data:
        return f"OSPF neighbors for {device}:\n{ospf_data[device]}"
    return f"No OSPF data for {device}"


@tool
def get_bgp_summary(device: str) -> str:
    """Get BGP summary information for a device."""
    bgp_data = {
        "R1": """
Neighbor        AS      State       PfxRcd  PfxSnt
10.0.0.2        65002   Established 150     120
10.0.0.3        65003   Established 200     120
10.0.0.4        65004   Idle        0       0""",
        "R2": """
Neighbor        AS      State       PfxRcd  PfxSnt
10.0.0.1        65001   Established 120     150
10.0.0.5        65005   Established 300     150""",
    }

    if device in bgp_data:
        return f"BGP summary for {device}:\n{bgp_data[device]}"
    return f"No BGP data for {device}"


@tool
def get_interface_errors(interface: str) -> str:
    """Get error counters for a specific interface."""
    error_data = {
        "GigabitEthernet0/1": {
            "input_errors": 0,
            "output_errors": 0,
            "crc_errors": 0,
            "collisions": 0,
            "status": "healthy"
        },
        "GigabitEthernet0/2": {
            "input_errors": 1542,
            "output_errors": 23,
            "crc_errors": 847,
            "collisions": 156,
            "status": "errors detected"
        },
        "GigabitEthernet0/3": {
            "input_errors": 5,
            "output_errors": 0,
            "crc_errors": 5,
            "collisions": 0,
            "status": "minor issues"
        },
    }

    if interface in error_data:
        e = error_data[interface]
        return f"{interface} errors: Input={e['input_errors']}, Output={e['output_errors']}, CRC={e['crc_errors']}, Collisions={e['collisions']}, Status={e['status']}"
    return f"Interface {interface} not found"


@tool
def generate_acl(params: str) -> str:
    """Generate an ACL based on parameters. Format: 'permit|deny,source_ip,dest_ip,protocol,port'"""
    try:
        parts = params.split(",")
        if len(parts) != 5:
            return "Error: Format should be 'permit|deny,source_ip,dest_ip,protocol,port'"

        action, source, dest, protocol, port = [p.strip() for p in parts]

        acl = f"""
ip access-list extended GENERATED_ACL
 {action} {protocol} {source} any {dest} any eq {port}
 deny ip any any log
!
interface GigabitEthernet0/1
 ip access-group GENERATED_ACL in
"""
        return f"Generated ACL:\n{acl}"
    except Exception as e:
        return f"Error generating ACL: {str(e)}"


if __name__ == "__main__":
    print("Testing Custom Tools")
    print("=" * 50)

    print("\n1. Subnet Calculator:")
    print(calculate_subnet.invoke({"cidr": "10.0.0.0/22"}))

    print("\n2. VLAN Lookup:")
    print(lookup_vlan.invoke({"vlan_id": 10}))

    print("\n3. Port Status:")
    print(check_port_status.invoke({"interface": "GigabitEthernet0/1"}))

    print("\n4. Ping Check:")
    print(ping_check.invoke({"target": "192.168.10.1"}))
    print(ping_check.invoke({"target": "192.168.30.1"}))

    print("\n5. Routing Table:")
    print(get_routing_table.invoke({"device": "R1"}))

    print("\n6. OSPF Neighbors:")
    print(get_ospf_neighbors.invoke({"device": "R1"}))

    print("\n7. BGP Summary:")
    print(get_bgp_summary.invoke({"device": "R1"}))

    print("\n8. Interface Errors:")
    print(get_interface_errors.invoke({"interface": "GigabitEthernet0/2"}))

    print("\n9. Generate ACL:")
    print(generate_acl.invoke({"params": "permit,192.168.10.0/24,192.168.20.0/24,tcp,443"}))