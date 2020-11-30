#-*- coding:utf-8 -*-

import os
from bs4 import BeatifulSoup
from pymongo import MongoClient

mongo = MongoClient("localhost",27017).asset.nmap_result

def parse_xml(xml_filename):
    soup = BeatifulSoup(open(xml_filename,'r').read(),'lxml')
    for host in soup.find_all('host'):
        if host.status['state'] == 'up':
            ip = host.address['addr']
            ports = []
            for port in  host.ports.find_all('port'):
                ports.append({
                    'protocol':port['protocol'],
                    'portid':port['portid'],
                    'state':port.state['state'],
                    'service':port.service['service']
                })

            mongo.update_one(
                {'ip':ip},
                {
                    '$set':{
                        'port':ports
                    }
                },
                upsert = True
            )
            print(ip)

def main():
    for root,dir,names in os.walk('.'):
        for name in names:
            if name.endswith('.xml'):
                filename = root + os.sep +name
                parse_xml(filename)