# multimon

Project to TCP Syn or Ping multiple IPs simultaneously



Requirements:

- Python 3.6
 
 

Usage:

python3 multimon.py [host/ip_list_file] [-tt title (optional)] [-rf refresh time (default 5s)] [-to timeout (default 1s)]

ex. python3 multitcpmon.py host_list.txt

ex. python3 multitcpmon.py host_list.txt -rf 10 -to 2




File Template:

host/ip,port,desc

e.g.

microsoft.com,443,Microsoft

192.168.0.1,80,Local_Router
