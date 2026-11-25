# Network Tools Guide — Wireshark + Nmap

## Wireshark 4.6.10 — see every packet on your network

**What it does:** captures and displays network traffic in real time — every packet your computer sends/receives, decoded into readable protocols (HTTP, DNS, TLS...)

### Quick start
1. Open **Wireshark** (Start Menu)
2. Pick your active network interface (usually "Wireshark Loopback" or your Wi-Fi/Ethernet adapter — the one with traffic moving)
3. Click the **blue shark fin** to start capturing
4. Browse a website → packets flood in
5. Click any packet → 3 panes: packet list / protocol details / raw bytes

### Useful filters (type in the filter bar)
- `http` — only web traffic
- `dns` — only domain lookups
- `tls` — encrypted connections (you'll see SNI = which sites)
- `ip.addr == 192.168.1.5` — traffic to/from one device
- `tcp.port == 443` — HTTPS only

### CLI version (no GUI needed)
```powershell
& "C:\Program Files\Wireshark\tshark.exe" -i 1 -c 20
```

## Nmap 7.80 — scan your own network

**What it does:** discovers devices and open ports on a network.

### Safe beginner scans (YOUR network only!)
```powershell
nmap localhost                    # scan your own PC
nmap -sn 192.168.1.0/24           # find all devices on your Wi-Fi (no port scan)
nmap 192.168.1.1                  # scan your router
```

### Reading output
- `Nmap scan report` = device found
- `PORT STATE SERVICE` = open doors — e.g. `22/tcp open ssh`

### Legal note
Only scan networks/devices **you own or have permission to test**. Scanning networks you don't own is illegal in most countries.

## Wireshark vs Nmap
| Tool | Sees | Question it answers |
|---|---|---|
| Wireshark | packet contents | "What is being said?" |
| Nmap | open ports/services | "What doors exist?" |
