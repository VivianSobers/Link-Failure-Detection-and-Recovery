# Link Failure Detection and Recovery

![Networking](https://img.shields.io/badge/Domain-Computer%20Networks-1E90FF?style=for-the-badge)
![SDN](https://img.shields.io/badge/SDN-Software%20Defined%20Networking-4169E1?style=for-the-badge)
![Controller](https://img.shields.io/badge/Controller-Ryu-6A5ACD?style=for-the-badge)
![Emulation](https://img.shields.io/badge/Emulator-Mininet-20B2AA?style=for-the-badge)
![Protocol](https://img.shields.io/badge/OpenFlow-1.3-4682B4?style=for-the-badge)
![Switching](https://img.shields.io/badge/Open%20vSwitch-OVS-2E8B57?style=for-the-badge)
![Validation](https://img.shields.io/badge/Validation-Wireshark%20%7C%20iperf3-FF8C00?style=for-the-badge)
![Recovery](https://img.shields.io/badge/Recovery-Automatic%20Failover-success?style=for-the-badge)
![Packet Loss](https://img.shields.io/badge/Packet%20Loss-0%25-brightgreen?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

A software-defined networking project that detects link failures in real time and automatically reroutes traffic, no human intervention required.

---

## The Problem

Networks fail. Cables get cut, ports go down, hardware breaks. In traditional networks, recovery is slow and manual. In an SDN-controlled network, the controller sees everything and can react instantly.

This project demonstrates exactly that. When a link goes down, the Ryu controller detects the failure, tears out the old flow rules, and pushes new ones through a backup path all before a single ping is dropped.

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

The Ryu controller pre-installs explicit flow rules on all switches at startup. When the s1-s2 link fails, the controller detects the port status change, deletes the existing flow rules, and installs higher-priority backup rules through s3 restoring connectivity immediately.

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

- Ubuntu 24.04 (native or VM)
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

## Proof of Execution

### Network Startup — Primary Path Active
![Network Startup](screenshots/1.png)

### Scenario 1 — Normal pingall (0% dropped)
![Normal pingall](screenshots/2.png)

### Link Failure Detected — Switching to Backup Path
![Link Failure](screenshots/3.png)

### Scenario 2 — pingall During Link Failure (0% dropped)
![pingall during failure](screenshots/4.png)

### Link Restored — Back to Primary Path
![Link Restored](screenshots/5.png)

### iperf3 — Normal Operation (15.2 Gbits/sec)
![iperf3 normal](screenshots/6.png)

### iperf3 — During Link Failure (16.8 Gbits/sec)
![iperf3 failure](screenshots/7.png)

### Wireshark — ICMP Capture
![Wireshark all](screenshots/8.png)

### Wireshark — ICMP Filtered (Normal)
![Wireshark filtered](screenshots/9.png)

### Wireshark — ICMP Filtered (During Failure)
![Wireshark during failure](screenshots/10.png)

---
## Author

Vivian Sobers E
