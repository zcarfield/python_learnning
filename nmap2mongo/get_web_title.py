# -*- utf-8 -*-
import requests,re,chardet
from requests.packages import urllib3
from pymongo import MongoClient
import threading
from queue import Queue
urllib3.disable_warnings()

header = {
    'User-Agent'：'Mozilla/5.0 (Windows NT 10.0; Win64; X64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}

task_queue = Queue()
threadlock = threading.Lock()
mongo_website = MongoClient("localhost",27017).asset.website

def get_web_title(url):
    try:
        if url.startswith('https'):
            r = requests.get(url,headers=headers,verify=False,timeout=5)
        else:
            r = requests.get(url,headers=headers,timeout=5)
    except:
        return

    if r.status_code == 200:
        title = re.findall(r'<title>(.*?)</title>')
        home_title = ''
        if title:
            dect_encoding = chardet.detect(r.text.encode(r.encoding))['encoding']

            try:
                home_title = title[0].encode(r.encoding).decode(dect_encoding)
            except:
                home_title = title[0]
            else:
                pass

        mongo_website.update_one(
            {'url':url},
            {'$set':{
                'title':home_title,
                'reponse_header':r.headers
            }},
            upsert = True
        )
        print(url,home_title)

class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            threadlock.acquire()
            if task_queue.empty():
                threadlock.release()
                break

            else:
                url = task_queue.get()
                print('queue size',task_queue.qsize())
                threadlock.release()
                get_web_title(url)

def main():
    mongo = MongoClient("localhost",27017).asset.nmap_result
    for url in ['http://'+x['ip'] for x in mongo.find({'ports.portid':'80'},{'ip':1})]:
        task_queue.put(url)

    threads = []
    for i in range(20):
        t = myThread()
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    print('completed!')

main()