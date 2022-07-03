import numpy as np
import requests
import re
import socket
from collections import Counter

# get local IP via API64
def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

# get local IP with internal interfaces
def get_local_ip_address():
    return str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] 
    if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), 
    s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, 
    socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

# get location by passing IP address
# using external API (ipapi or geolocation-db)
def get_location(ip_address = ''):
    if ip_address == '': ip_address = get_ip()
    
    # response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    response = requests.get(f'https://geolocation-db.com/json/{ip_address}').json()
    
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    
    return location_data

# read file and return a list of all the lines present in the file
def read_file(file_path):
    file = open(file_path, 'r')
    lines = file.read()
    
    return lines.split('\n')

# generic apache log
def apache_log(log_line):
    temp = log_line.split()
    
    return {'remote_host': temp[0],
            'datetime': (temp[3] + ' ' + temp[4]).replace('[', '').replace(']', ''),
            'apache_status': temp[8],
            'data_transfer': temp[9],
            'host_info': get_location(ip_address=temp[0])
    }

# to create a list o dictionary with the informations 
# of every line in the log file
def get_apache_infos(logs_list):
    # list of dictionary 
    list_dict = []
    
    for line in logs_list: list_dict.append(apache_log(log_line=line))
        
    return list_dict
  
def main(file_path):
    # debug 
    for dict in get_apache_infos(logs_list=read_file(file_path)):
        print(str(dict['remote_host']) + ': ' + str(dict['host_info']['country']))
        
    # test with regex (list of all the ips present in the log file)
    ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', open(file_path, 'r').read())
    ip_counter = Counter(ips)
    
    # debug
    print(ip_counter)
    
    # print(type(Counter(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', open(file_path, 'r').read()))))
    # print(Counter(re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', open(file_path, 'r').read())).elements())

    for ip in ip_counter.elements(): print(str(ip) + str(ip_counter[ip]))
    
if __name__ == '__main__':
    main(file_path='log.txt')
