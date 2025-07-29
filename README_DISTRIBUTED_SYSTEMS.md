# Distributed Systems Simulator

A comprehensive simulator for distributed systems that implements consensus algorithms, fault tolerance mechanisms, and distributed data structures.

## Features

- **Consensus Algorithms**: Raft, PBFT, and Paxos implementations
- **Distributed Hash Table**: Consistent hashing with replication
- **Load Balancing**: Multiple algorithms (Round Robin, Least Connections, etc.)
- **Fault Tolerance**: Node failures and network partitions simulation
- **Network Simulation**: Configurable latency and packet loss
- **Byzantine Fault Tolerance**: Handles malicious nodes
- **Real-time Visualization**: Cluster topology and status monitoring

## Requirements

- Python 3.7+
- asyncio
- NetworkX
- Matplotlib
- NumPy

## Installation

1. Install the required packages:

```bash
pip install -r requirements_distributed_systems.txt
```

## Usage

### Command Line Interface

**Basic Raft cluster simulation:**
```bash
python 28_distributed_systems_simulator.py --nodes 5 --algorithm raft --duration 60
```

**Simulate network issues:**
```bash
python 28_distributed_systems_simulator.py --nodes 7 --packet-loss 0.1 --latency 50 200
```

**Generate visualization:**
```bash
python 28_distributed_systems_simulator.py --nodes 5 --visualize --output results.json
```

### Parameters

- `--nodes`: Number of nodes in the cluster (default: 5)
- `--algorithm`: Consensus algorithm (raft, pbft, paxos)
- `--duration`: Simulation duration in seconds (default: 60)
- `--packet-loss`: Packet loss rate 0.0-1.0 (default: 0.0)
- `--latency`: Network latency range in ms (default: 10 100)
- `--visualize`: Generate cluster topology visualization
- `--output`: Save results to JSON file

## Consensus Algorithms

### Raft Algorithm
- **Leader Election**: Automatic leader selection with term-based voting
- **Log Replication**: Consistent log replication across followers
- **Safety Properties**: Strong consistency guarantees
- **Fault Tolerance**: Handles minority node failures

### PBFT (Practical Byzantine Fault Tolerance)
- **Byzantine Fault Tolerance**: Handles up to f malicious nodes in 3f+1 system
- **Three-Phase Protocol**: Pre-prepare, prepare, commit phases
- **View Changes**: Leader replacement mechanism
- **Message Authentication**: Cryptographic message verification

### Paxos Algorithm
- **Multi-Paxos**: Efficient consensus for multiple values
- **Prepare Phase**: Proposal number selection
- **Accept Phase**: Value acceptance and learning
- **Fault Tolerance**: Progress with majority availability

## Distributed Hash Table (DHT)

### Consistent Hashing
- **Virtual Nodes**: Better load distribution
- **Fault Tolerance**: Automatic failover and recovery
- **Scalability**: Dynamic node addition/removal
- **Replication**: Configurable replication factor

### Operations
```python
# Store key-value pair
dht_node.put("key1", "value1")

# Retrieve value
value = dht_node.get("key1")

# Delete key
dht_node.delete("key1")
```

## Load Balancing Algorithms

### Round Robin
- **Simple**: Equal distribution across servers
- **Stateless**: No server state tracking
- **Fair**: Each server gets equal requests

### Least Connections
- **Dynamic**: Routes to server with fewest active connections
- **Load-Aware**: Considers current server load
- **Adaptive**: Adjusts to varying request durations

### Weighted Round Robin
- **Capacity-Based**: Considers server capabilities
- **Configurable**: Adjustable weights per server
- **Flexible**: Handles heterogeneous server clusters

### Consistent Hashing
- **Sticky Sessions**: Same client always routes to same server
- **Fault Tolerant**: Minimal disruption when servers fail
- **Scalable**: Easy to add/remove servers

## Network Simulation

### Failure Models
- **Node Failures**: Crash-stop and crash-recovery
- **Network Partitions**: Split-brain scenarios
- **Message Loss**: Configurable packet loss rates
- **Latency Variations**: Realistic network delays

### Fault Injection
```python
# Fail a specific node
simulator.network.fail_node("node_1")

# Create network partition
simulator.network.create_partition({"node_1", "node_2"}, {"node_3", "node_4"})

# Recover failed node
simulator.network.recover_node("node_1")
```

## Project Structure

- `RaftNode`: Raft consensus algorithm implementation
- `DistributedHashTable`: DHT with consistent hashing
- `LoadBalancer`: Multiple load balancing strategies
- `NetworkSimulator`: Network conditions and fault injection
- `DistributedSystemsSimulator`: Main simulation orchestrator

## Advanced Features

### Byzantine Fault Tolerance
- Handles malicious nodes that send conflicting messages
- Cryptographic message authentication
- View change protocols for leader replacement
- Safety guarantees with up to f Byzantine failures in 3f+1 nodes

### Performance Monitoring
- Message throughput tracking
- Latency measurements
- Consensus completion times
- Load distribution metrics

### Visualization
- Real-time cluster topology
- Node state visualization
- Network partition display
- Performance dashboards

## Examples

### Basic Raft Cluster
```python
from distributed_systems_simulator import DistributedSystemsSimulator

simulator = DistributedSystemsSimulator()
simulator.create_raft_cluster(["node_1", "node_2", "node_3"])

# Run simulation
await simulator.run_simulation(duration=60)

# Get cluster status
status = simulator.get_cluster_status()
```

### DHT Operations
```python
# Create DHT cluster
simulator.create_dht_cluster(["node_1", "node_2", "node_3"], replication_factor=2)

# Store and retrieve data
dht_node = simulator.dht_nodes["node_1"]
dht_node.put("user:123", {"name": "John", "age": 30})
user_data = dht_node.get("user:123")
```

### Load Balancer Setup
```python
# Create load balancer
simulator.create_load_balancer(["server_1", "server_2", "server_3"], "least_connections")

# Route requests
server = simulator.load_balancer.get_server("client_123")
```

## Performance Optimization

- **Batch Processing**: Group multiple operations for efficiency
- **Caching**: Reduce redundant consensus operations
- **Pipelining**: Overlap request processing
- **Compression**: Reduce message sizes

## Testing Scenarios

### Split-Brain Prevention
Test how the system handles network partitions and prevents split-brain scenarios.

### Leader Election
Verify correct leader election under various failure conditions.

### Data Consistency
Ensure strong consistency guarantees across all nodes.

### Performance Under Load
Measure system performance with high request rates and network stress.

## Troubleshooting

- **Consensus Failures**: Check network connectivity and node health
- **Split-Brain**: Verify quorum requirements are met
- **Performance Issues**: Monitor network latency and node resources
- **Data Inconsistency**: Check replication factor and failure scenarios

## License

This project is open source and available under the MIT License. 