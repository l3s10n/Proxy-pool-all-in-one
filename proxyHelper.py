from pwn import *
import re, requests

s = server(8080)

def getRandomProxy():
    proxyRepositoryUrl = "http://127.0.0.1:5010/get/"
    try:
        proxy = requests.get(proxyRepositoryUrl).json()["proxy"]
    except:
        print("No http proxiy can be used")
        exit()
    return proxy

while True:
    cc = s.next_connection()
    msg = cc.recv().decode()

    headersPart, bodyPart = msg.split('\r\n\r\n')

    headerSlices = headersPart.split('\r\n')
    r = re.search("(.*) (.*) HTTP", msg)
    method = r.group(1)
    url = r.group(2)
    headers = {}
    for slice in headerSlices:
        if ': ' in slice:
            key, value = slice.split(': ')
            headers[key.strip()] = value.strip()

    if ('Content-Type' in headers.keys() or 'Transfer-Encoding' in headers.keys()) and bodyPart=='':
        bodyPart = cc.recv()

    proxy = getRandomProxy()
    proxies = {"http": "http://{proxy}".format(proxy=proxy)}
    response = False
    maxTry = 3
    countTry = 0

    if method == 'GET':
        while not response:
            if countTry > maxTry:
                print("out of max try")
                break
            countTry = countTry + 1
            try:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=5)
            except:
                proxy = getRandomProxy()
                proxies = {"http": "http://{proxy}".format(proxy=proxy)}
        if response:
            cc.send(response.content)
    elif method == 'POST':
        while not response:
            if countTry > maxTry:
                print("out of max try")
                break
            countTry = countTry + 1
            try:
                response = requests.post(url, headers=headers, data=bodyPart, proxies=proxies, timeout=5)
            except:
                proxy = getRandomProxy()
                proxies = {"http": "http://{proxy}".format(proxy=proxy)}
        if response:
            cc.send(response.content)
    else:
        print('unsupported method')

    cc.close()