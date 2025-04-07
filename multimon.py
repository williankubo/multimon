import argparse
import socket
import errno
import threading
import queue
import time
import sys
import os
import asyncio


output_stream = sys.stdout

#https://github.com/williankubo/multimon/blob/main/multimon.py
#https://raw.githubusercontent.com/williankubo/multimon/main/multimon.py


#Initialize the parser
parser = argparse.ArgumentParser(
    description='Multi Monitor - by Kubo (This is a Multi Monitor connect status.)')
parser.add_argument('File', help='file format - e.g. host/ip,port,description - for ping use port value 0')
parser.add_argument('-tt', help='title')
parser.add_argument('-rf', help='refresh time (default 5s)')
parser.add_argument('-to', help='timeout time (default 1s)')
args = parser.parse_args()

#Retrieve parameter values from the parser arguments

#madatory values

ipfile=args.File
#print(ipfile)

#optional values

title = ""
if args.tt != None:
    title = args.tt
#print(title)

delay_refresh = 5
if args.rf != None:
    delay_refresh = float(args.rf)
#print(delay_refresh)

wait_return = 1
if args.to != None:
    wait_return = args.to
#print(wait_return)

"""
ports = range(1,1024)
if "-" in args.p:
    [minPort,maxPort] = [int(i) for i in args.p.split("-")]
    ports = range(minPort,maxPort+1)
elif args.p != None:
    ports = [int(i) for i in args.p.split(",")]
"""

# Define global variables

version = "v0.1"
lock = threading.Lock()
q = queue.Queue()
wait_ping_return = 1


# open source_file
with open( ipfile, 'r') as source_file:
    # read lines from source_file
    lines = source_file.readlines()
    
    # remove empty lines
    no_empty_lines = [line.strip() for line in lines if line.strip()]
    
#print(no_empty_lines)

# init list
lines = []

# each line from source_file to line in list
for line in no_empty_lines:
    lines.append(line.strip().split(',')) # separate by ','

# do matriz from lines
new_data = [list(line) for line in lines]
#print(new_data)


# number of lines (hosts)
number_of_lines = len(new_data)


# add colum:  list[[ip,port,desc]] -> list[[ip,port,desc,status]
for i in range(number_of_lines):
    new_data[i].append("Wait")
#print(new_data)

# number of threads = number of lines 
threads = number_of_lines
#print(threads)


# class colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[40;92m'
    OKWARNING = '\033[40;93m'
    WARNING = '\033[93m'
    FAIL = '\033[40;91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_RED = '\033[1;41m'
    BG_GREEN = '\033[1;42m'
    BG_BLK2 = '\033[40;1m'
    BG_BLK = '\033[40;0m'


# function to clear screen
clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')


## start functions TCP_CONNECT

#connect(ip, port) - Connects to an ip address on a specified port to check if it is open
#Params:
#   ip - The ip to connect to
#   port - The port to connect to on the specified ip
#
#Returns: 'Open', 'Closed' or 'Timeout' depending on the result of connecting to the specified ip and port
def connect(ip, port):
    status = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        connection = s.connect((ip, port))
        status = "Open"
        s.close()

    except socket.timeout:
        status = "Timeout"
    
    except socket.gaierror as e:
            status = "errorDNSresol"
  
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
            status = "Closed"
        else:
            raise e

    return status


#worker() - A function for worker threads to scan IPs and ports
def worker():
    while not q.empty():
        (ip,port,index) = q.get()
        status = connect(ip,port)
        lock.acquire()
        new_data[index][3] = status
        lock.release()
        q.task_done()

## END

#init_polling() - A function to prepare and start polling to list host/ip:ports
def init_polling():

    ## TCP_CONNECT    
    #Prepare queue
    tcp_threads = 0
    for index in range(number_of_lines):
        if  (int(new_data[index][1])) != 0:      #if port is different of 0 (because 0 is PING)
            tcp_threads = tcp_threads + 1             
            q.put((new_data[index][0],int(new_data[index][1]),index))
            #print(new_data[index][0]+":"+new_data[index][1]+" index "+str(index))

    #Start threads
    #print(tcp_threads)
    for index in range(tcp_threads):
        t = threading.Thread(target=worker)
        t.start()

    q.join()


## start functions PING 

# async function, receive index of list
async def ping(index):                              #add the "async" keyword to make a function asynchronous
    global new_data
    global wait_ping_return
    #host = str(host)                               #turn ip address object to string
    host = new_data[index][0]                               #turn ip address object to string
    proc = await asyncio.create_subprocess_shell(  #asyncio can smoothly call subprocess for you
            f'ping {host} -c 1 -W {wait_ping_return}',                   #ping command
            stderr=asyncio.subprocess.DEVNULL,     #silence ping errors
            stdout=asyncio.subprocess.DEVNULL      #silence ping output
            )
    stdout,stderr = await proc.communicate()       #get info from ping process
    if  proc.returncode == 0:                      #if process code was 0                      
        #print(f'{host} is alive!')                 #say it's alive!
        new_data[index][3] = "Up"                      #set status 1 (UP)
        #print(new_data[index])

    else:
        #print(f'{bcolors.FAIL}{host} is dead!{bcolors.ENDC}')
        new_data[index][3] = "Timeout"             #set status 0 (Timeout)
        #print(new_data[index])


loop = asyncio.get_event_loop()                    #create an async loop

tasks = []                                         #list to hold ping tasks

## END



# update/print data on screen
def update_screen():

    global polling

    clearConsole() #clear screen
    print(f'[ {bcolors.OKCYAN}{title}{bcolors.ENDC} - Multi Monitor {version} ]')
    print()
    for index2 in range(len(new_data)):
        host = new_data[index2][0]
        try:
            ip = socket.gethostbyname(new_data[index2][0])
        except socket.gaierror:
            ip=""
        port = new_data[index2][1]
        description = new_data[index2][2]
        status = new_data[index2][3]
        if ((status == "Open") or (status == "Closed") or (status == "Up")):
            #print connection status
            print(f'{host}:{port} {ip} {bcolors.UNDERLINE}{description}{bcolors.ENDC} is {bcolors.OKGREEN}{status}{bcolors.ENDC}')
        elif (status == "Timeout"):
            #print connection status
            print(f'{host}:{port} {ip} {bcolors.UNDERLINE}{description}{bcolors.ENDC} is {bcolors.FAIL}{status}{bcolors.ENDC}')
        else:
            #print connection status
            print(f'{host}:{port} {ip} {bcolors.UNDERLINE}{description}{bcolors.ENDC} is {bcolors.OKWARNING}{status}{bcolors.ENDC}')
    print()


# init variable polling
polling = 0

# init variable time_start
time_start = time.time()

# clone new_data to current_data (reference to detect changes)
current_data = list(map(list, new_data))
#print(current_data)



# main loop
while True:

    # Print first screen

    if(polling==0):

        # save start time
        time_start = time.time()

        # print first screen
        update_screen()

        #Update screen line polling
        output_stream.write('Polling %s\r' % polling)
        output_stream.flush()

        polling = polling + 1
        
        # to avoid syn storm e high cpu (always wait refresh time)
        time_execution = time.time()-time_start
        if time_execution < delay_refresh:
            time_rest = delay_refresh - time_execution
            time.sleep(time_rest)


    else:

        # save start time
        time_start = time.time()

        # Init polling TCP
        init_polling()
        
        # Prepare queue PING
        for index in range(number_of_lines):
            if  (int(new_data[index][1])) == 0:      #if port is equal of 0 (because 0 is PING)
                task = ping(index)                      #create async task from function we defined above
                tasks.append(task)                      #add task to list of tasks

        # Start queu PING
        tasks = asyncio.gather(*tasks)                     #some magic to assemble the tasks
        loop.run_until_complete(tasks)                     #run all tasks (basically) at once
        tasks = [] 
        
        # verify if new_data updated, and print new screen
        if(new_data!=current_data):
            update_screen()                    
            current_data = list(map(list, new_data)) #update current_data with new_data

        #Update screen line polling
        output_stream.write('Polling %s\r' % polling)
        output_stream.flush()

        polling = polling + 1

        # to avoid syn storm e high cpu (always wait refresh time)
        time_execution = time.time()-time_start
        if time_execution < delay_refresh:
            time_rest = delay_refresh - time_execution
            time.sleep(time_rest)
