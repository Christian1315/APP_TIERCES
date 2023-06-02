import requests

def getData(url):
    return requests.get(url)

def postData(url,data):
    return requests.post(url,json=data)

def patchData(url,data):
    return requests.patch(url,json=data)