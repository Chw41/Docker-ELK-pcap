# Elastic Stack (ELK) on Docker with Fixed IP and WireGuard VPN for pcap Analysis

[![Elastic Stack version](https://img.shields.io/badge/Elastic%20Stack-8.17.0-00bfb3?style=flat&logo=elastic-stack)](https://www.elastic.co/blog/category/releases)
[![Build Status](https://github.com/deviantony/docker-elk/workflows/CI/badge.svg?branch=main)](https://github.com/deviantony/docker-elk/actions?query=workflow%3ACI+branch%3Amain)
[![Join the chat](https://badges.gitter.im/Join%20Chat.svg)](https://app.gitter.im/#/room/#deviantony_docker-elk:gitter.im)

Customized and enhanced the ELK stack based on [deviantony/docker-elk](https://github.com/deviantony/docker-elk), that enables seamless integration of PCAP files as logs for analysis. This setup is deployed on a fixed IP within a local network, utilizing a VPN for secure access. Additionally, I have included a `catch_pcap.py` script, which captures network traffic and generates PCAP files that can be directly ingested into ELK. This solution provides a centralized and scalable approach for network traffic monitoring, log analysis, and security investigations.

>[!note]
>The Chinese tutorial version is available at: [hackmd.io/@CHW/](https://hackmd.io/@CHW/S1vy8V8ca)

Run the latest version of the [Elastic stack][elk-stack] with Docker and Docker Compose.
Based on the [official Docker images][elastic-docker] from Elastic:

* [Elasticsearch](https://github.com/elastic/elasticsearch/tree/main/distribution/docker)
* [Logstash](https://github.com/elastic/logstash/tree/main/docker)
* [Kibana](https://github.com/elastic/kibana/tree/main/src/dev/build/tasks/os_packages/docker_generator)


---

## TL;DR

```sh
docker compose up setup
```

```sh
docker compose up
```

## Requirements

### Host setup

* [Docker Engine][docker-install] version **18.06.0** or newer
* [Docker Compose][compose-install] version **2.0.0** or newer
* 1.5 GB of RAM

By default, the stack exposes the following ports:

* 5044: Logstash Beats input
* 50000: Logstash TCP input
* 9600: Logstash monitoring API
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana

> [!WARNING]
> Elasticsearch's [bootstrap checks][bootstrap-checks] were purposely disabled to facilitate the setup of the Elastic
> stack in development environments. For production setups, we recommend users to set up their host according to the
> instructions from the Elasticsearch documentation: [Important System Configuration][es-sys-config].

## Setting a Fixed IP in the Local Network
>[!Note]
>Environment: Using WireGuard on Mac\
>Example: Deploying ELK on 172.27.71.7
### Editing `docker-compose.yml`
```
services:

  elasticsearch:
    ...
    ports:
      - "172.27.71.7:9200:9200"
      - "172.27.71.7:9300:9300"
    ...
    networks:
      elk:
        ipv4_address: 172.27.71.7
    ...

  logstash:
    ...
    ports:
      - "172.27.71.7:5044:5044"
      - "172.27.71.7:50000:50000/tcp"
      - "172.27.71.7:50000:50000/udp"
      - "172.27.71.7:9600:9600"
    ...
    networks:
      elk:
        ipv4_address: 172.27.71.8
    ...

  kibana:
    ...
    ports:
      - "172.27.71.7:5601:5601"
    ...
    networks:
      elk:
        ipv4_address: 172.27.71.9
    ...

networks:
  elk:
    driver: bridge
    ipam:
      config:
        - subnet: "172.27.71.0/24"
          gateway: "172.27.71.1"
```
Key Points:
1. Assign ELK services to 172.27.71.7
2. Create a custom Docker network:
  - Name: elk
  - Subnet: Defined manually
3. Assign static IPs to ELK (172.27.71.7, 172.27.71.8, 172.27.71.9) to prevent dynamic IP allocation issues that may cause VPN access failures.

### Restart Containers:

```sh
docker-compose down && docker-compose up -d
```


## Configuring VPN
### 1. Install WireGuard Tools

```sh
$ brew install wireguard-tools
```

>[!Note]
>Even if you have installed the WireGuard app, you still need wireguard-tools.\
>The GUI and CLI configurations are not synced.\
>**The WireGuard App from the App Store is different from wireguard-tools installed via Terminal.**

### 2. Create a WireGuard Configuration File
```
[Interface]
Address = 172.27.71.7/24
PrivateKey = <your_private_key>
DNS = 8.8.8.8, 1.1.1.1
ListenPort = 51820

[Peer]
PublicKey = <peer_public_key>
AllowedIPs = 172.27.71.4/32
Endpoint = <peer_public_ip>:51820
```

### 3. Move Configuration File & Start VPN

```sh
$ sudo mv {wireguard conf} /opt/homebrew/etc/wireguard/wg0.conf
$ sudo wg-quick up wg0
Password:
Warning: `/opt/homebrew/etc/wireguard/wg0.conf' is world accessible
[+] Interface for wg0 is utun10
wg-quick: `wg0' already exists as `{interface}'
```

### 4. Check VPN Status

```sh
$ sudo wg show
interface: {interface}
  public key: {public key}
  private key: (hidden)
  listening port: 51421

peer: y4IWe9FjQ1iJg5Ep6YekzmAqUCDXiSRW62X92qzK7HY=
  endpoint: {對方的公網IP}:48763
  allowed ips: 172.27.71.0/24
  latest handshake: 7 seconds ago
  transfer: 2.28 MiB received, 2.44 MiB sent
  persistent keepalive: every 25 seconds
```

### 5. Test Connectivity via ping

```sh
$ ping 172.27.71.7
PING 172.27.71.7 (172.27.71.7): 56 data bytes
64 bytes from 172.27.71.7: icmp_seq=0 ttl=63 time=344.646 ms
64 bytes from 172.27.71.7: icmp_seq=1 ttl=63 time=327.920 ms
64 bytes from 172.27.71.7: icmp_seq=2 ttl=63 time=331.835 ms
64 bytes from 172.27.71.7: icmp_seq=3 ttl=63 time=331.821 ms
```

>[!important]
> If ping fails, check your firewall settings:\
> `sudo pfctl -sr`

### 6. Restart VPN to Apply Changes

```sh
sudo wg-quick down wg0
sudo wg-quick up wg0
```

### 7. Access Kibana
Open a browser and navigate to: http://172.27.71.7:5601/\
![image](https://hackmd.io/_uploads/H1rwqPvOJl.png)


## Automates the downloading of .pcap files: `catch_pcap.py`
Define the target URL (pcap_target): Replace `'{your_pcap_target_url}'` with the actual base URL for fetching `.pcap` files.\
Set up headers: If an authentication token is required, ensure it is valid.

```python
url_template = '{your_pcap_target_url}/pcap/{TeamID}/{}'  # Replace with the actual target URL
headers = {
    'accept': 'application/json',
    # Replace with a valid authorization token if needed
}
```

Iterate over a range of round numbers (1-180): It constructs the download URL for each `.pcap` file.\
Check already downloaded files: The script skips files that are already present.

```python
for round_number in range(1, 180):
    file_name = f'{round_number}.pcap'
    
    if file_name in already_downloaded:
        continue
    
    url = url_template.format(round_number)
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        with open(os.path.join(save_path, file_name), 'wb') as f:
            f.write(response.content)
        print(f'Catch Round: {round_number} Success')
    else:
        print(f'Round: {round_number} Fail，Status Code：{response.status_code}')
    
    time.sleep(3)
```


