# Link Failure Detection and Recovery

A software-defined networking project that detects link failures in real time and automatically reroutes traffic — no human intervention required.

---

## The Problem

Networks fail. Cables get cut, ports go down, hardware breaks. In traditional networks, recovery is slow and manual. In an SDN-controlled network, the controller sees everything — and can react instantly.

This project demonstrates exactly that. When a link goes down, the Ryu controller detects the failure, tears out the old flow rules, and pushes new ones through a backup path — all before a single ping is dropped.

---

## How It Works

The network topology consists of three switches and two hosts:

```
h1 --- s1 --- s2 --- h2
        \     /
          s3
```

**Primary path:** h1 → s1 → s2 → h2  
**Backup path:** h1 → s1 → s3 → s2 → h2

The Ryu controller pre-installs explicit flow rules on all switches at startup. When the s1-s2 link fails, the controller detects the port status change, deletes the existing flow rules, and installs higher-priority backup rules through s3 — restoring connectivity immediately.

When the link comes back up, the controller detects the recovery and switches back to the primary path.

---

## Stack

- **Mininet** — network emulation
- **Ryu** — SDN controller (OpenFlow 1.3)
- **Open vSwitch** — virtual switching
- **Wireshark / iperf3** — traffic analysis and validation

---

## Setup

### Prerequisites

- Ubuntu 24.04 (native, not VM)
- Python 3.11
- Mininet 2.3.0
- Ryu 4.34

### Installation

```bash
# Install Mininet
sudo apt install mininet -y

# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv -y

# Set up Ryu in a virtual environment
python3.11 -m venv ~/ryu-env
source ~/ryu-env/bin/activate
pip install setuptools==58.0.0
pip install dnspython==2.3.0 eventlet==0.33.3
pip install ryu

# Install tools
sudo apt install wireshark iperf3 -y
```

---

## Running the Project

You need two terminals.

**Terminal 1 — Start the Ryu controller:**
```bash
source ~/ryu-env/bin/activate
ryu-manager controller.py
```

**Terminal 2 — Start the Mininet topology:**
```bash
sudo python3 topology.py
```

---

## Demo

### Scenario 1 — Normal operation
```
mininet> pingall
```
Expected: 0% packet loss. Traffic flows through primary path h1 → s1 → s2 → h2.

### Scenario 2 — Link failure and recovery
```
mininet> link s1 s2 down
mininet> pingall
```
Expected: 0% packet loss. Controller detects failure and reroutes through h1 → s1 → s3 → s2 → h2.

```
mininet> link s1 s2 up
mininet> pingall
```
Expected: 0% packet loss. Controller detects recovery and restores primary path.

---

## Expected Output

**Controller terminal during failure:**
```
==================================================
LINK FAILURE DETECTED on s1-s2! Switching to backup path.
==================================================
ACTIVE PATH: h1 -> s1 -> s3 -> s2 -> h2 (Backup)
==================================================
```

**Controller terminal during recovery:**
```
==================================================
LINK RESTORED on s1-s2! Switching back to primary path.
==================================================
ACTIVE PATH: h1 -> s1 -> s2 -> h2 (Primary)
==================================================
```

---

## Validation

- `pingall` confirms 0% packet loss before, during, and after link failure
- `ovs-ofctl dump-flows` confirms flow rule changes on each switch
- Wireshark captures confirm traffic path switching in real time
- iperf3 confirms throughput is maintained during rerouting

---

## Author

Vivian Sobers E
