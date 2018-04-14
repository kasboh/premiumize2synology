__author__ = 'Bogdan'

import requests
import os, psutil
import shutil

''' change values '''
CUSTOMER_ID = 'put your customer id here'
PIN = 'put your pin here'
FEED_DOWNLOADS_FOLDER_ID = 'your root folder id where files are downloaded'
SYNOLOGY_FOLDER = 'your synology target folder e.g. /volume2/downloads'
''' change values above '''
ROOT = 'https://www.premiumize.me/api'
GET_FOLDER_URL = "/folder/list?id="
FOLDER_DELETE = "/folder/delete"
url = GET_FOLDER_URL + FEED_DOWNLOADS_FOLDER_ID + "&customer_id=" + CUSTOMER_ID + "&pin=" + PIN + "&includebreadcrumbs=true"
FOLDER_LIST = '%(root)s%(folder_url)s%(folder)s&customer_id=%(customer)s&pin=%(pin)s&includebreadcrumbs=true'
url = FOLDER_LIST % dict(root=ROOT, folder_url=GET_FOLDER_URL, folder=FEED_DOWNLOADS_FOLDER_ID, customer=CUSTOMER_ID, pin=PIN)
DELETE = '%(root)s%(delete)s?customer_id=%(customer)s&pin=%(pin)s'
deleteUrl = DELETE % dict(root=ROOT, delete=FOLDER_DELETE, customer=CUSTOMER_ID, pin=PIN)

def main():

    if running():
        return

    transfersList = []
    print("Transfers:")
    listTransfers = '%(root)s/transfer/list?customer_id=%(customer)s&pin=%(pin)s'
    url2 = listTransfers % dict(root=ROOT,customer=CUSTOMER_ID, pin=PIN)
    rTransfers = requests.get(url2)
    if rTransfers.status_code == 200:
        for transfer in rTransfers.json()['transfers']:
            if transfer["status"] == "finished":
                transfersList.append({"id": transfer["id"], "folder": transfer["folder_id"], "file": transfer["file_id"]})

    if not transfersList:
        return
    print(transfersList)
    removeNotRelevantTransfers(transfersList)
    downloadFolders(transfersList)
    deleteTransfers(transfersList)


def removeNotRelevantTransfers(transfers):
    transfers[:] = [tf for tf in transfers if checkFolderIsPartOfFeed(tf["folder"])]
    return


def checkFolderIsPartOfFeed(folder_id):
    url = FOLDER_LIST % dict(root=ROOT,folder_url=GET_FOLDER_URL, folder=folder_id, customer=CUSTOMER_ID, pin=PIN)
    requestFolder = requests.get(url)
    if requestFolder.status_code == 200:
        breadcrums = requestFolder.json()["breadcrumbs"]
        if any(bc["id"] == FEED_DOWNLOADS_FOLDER_ID for bc in breadcrums):
            return True
    return False


def downloadFolders(list):
    for item in list:
        url = FOLDER_LIST % dict(root=ROOT,folder_url=GET_FOLDER_URL, folder=item["folder"], customer=CUSTOMER_ID, pin=PIN)
        r = requests.get(url)
        if r.status_code == 200:
            jsonResponse = r.json()
            downloadFolder = SYNOLOGY_FOLDER + "/" + jsonResponse["name"]
            if not os.path.exists(downloadFolder):
                os.makedirs(downloadFolder)
            for content in jsonResponse["content"]:
                if content["type"] == "file":
                    file = requests.get(content["link"], stream=True)
                    with open(downloadFolder + "/" + content["name"], 'wb') as f:
                        shutil.copyfileobj(file.raw, f)

    return

def running():

    for q in psutil.process_iter():
        if q.name() == 'python':
            print(q.cmdline())
            if len(q.cmdline())>1 and 'premiumize.py' in q.cmdline()[1]:
                return True

    return False

def deleteTransfers(transfers):
    for folder in transfers:
        r = requests.post(deleteUrl, data = {"id":folder["folder"]})
    return


if __name__=="__main__":
   main()
