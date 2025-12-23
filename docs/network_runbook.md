# Network Runbook

## OSPF Troubleshooting

### Neighbor Stuck in INIT State
If an OSPF neighbor is stuck in INIT state, check the following:
1. Verify both sides have matching OSPF network statements
2. Check that hello and dead timers match on both interfaces
3. Ensure the interface is not set to passive
4. Verify there are no ACLs blocking OSPF (protocol 89)

Commands to run:
- show ip ospf interface
- show ip ospf neighbor
- debug ip ospf adj

### Neighbor Stuck in EXSTART/EXCHANGE
This usually indicates an MTU mismatch between neighbors.
1. Check MTU on both interfaces with "show interface"
2. Either match the MTU or configure "ip ospf mtu-ignore"

## BGP Troubleshooting

### BGP Neighbor Not Established
Common causes for BGP neighbors not coming up:
1. TCP port 179 blocked by firewall or ACL
2. Incorrect neighbor IP address configured
3. AS number mismatch
4. Missing or incorrect update-source configuration
5. eBGP multihop not configured for non-directly-connected peers

Commands to run:
- show ip bgp summary
- show ip bgp neighbors
- debug ip bgp

### BGP Route Not Being Advertised
If a route exists in the routing table but isn't being advertised via BGP:
1. Check the network statement matches exactly (including mask)
2. Verify the route exists in the RIB
3. Check for route-maps on the neighbor that might filter the prefix
4. Look for prefix-lists that might block the advertisement

## VLAN Troubleshooting

### Users Cannot Reach Other VLANs
Inter-VLAN routing issues checklist:
1. Verify the SVI (interface vlan X) is up/up
2. Check that ip routing is enabled on the switch
3. Verify the default gateway is correctly configured on end hosts
4. Check for any ACLs applied to the SVI

### Trunk Not Passing VLANs
If a trunk is up but not passing certain VLANs:
1. Check allowed VLANs on trunk: "show interface trunk"
2. Verify VLAN exists in the VLAN database on both switches
3. Check for VLAN pruning
4. Ensure native VLAN matches on both sides

## Interface Troubleshooting

### Interface Flapping
Rapid up/down cycles on an interface can be caused by:
1. Bad cable or SFP module
2. Duplex mismatch
3. Speed mismatch
4. Electrical interference
5. Spanning tree issues (portfast missing on access ports)

### High CRC Errors
CRC errors indicate layer 1 problems:
1. Replace the cable
2. Replace the SFP module
3. Check for EMI sources near the cable run
4. Clean fiber connectors if using fiber

### Input/Output Errors
High error counters suggest:
- Input errors: Usually physical layer (cables, optics)
- Output errors: Usually congestion or buffer issues
- Collisions: Duplex mismatch (should be 0 on full duplex)