# multimon

Project to TCP Syn or Ping multiple IPs simultaneously

## Requirements:

- Python 3.6
- Asyncio

maybe need to install: pip install asyncio
 
## Usage:

python3 multimon.py [host/ip_list_file] [-tt title (optional)] [-rf refresh time (default 5s)] [-to timeout (default 1s)]

e.g. 

```text
python3 multitcpmon.py -h # for help
python3 multitcpmon.py host_list.txt
python3 multitcpmon.py host_list.txt -rf 10 -to 2
```

## File Template:

```text
host/ip,port,desc
```
use port value 0 for Ping

e.g.

```text
microsoft.com,443,Microsoft
192.168.0.1,0,Local_Router
```
