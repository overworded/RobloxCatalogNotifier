import requests
import time
from datetime import datetime

cookie = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_..." # roblo security cookie, needed to get the item details in a batch request.
RobloxCatalog = "https://catalog.roblox.com/v1/search/items?category=All&creatorName=Roblox&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3" # catalog link for items created by the Roblox account.
UGCCatalog = "https://catalog.roblox.com/v1/search/items?category=Accessories&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3&subcategory=Accessories" # catalog link for items created by users.
RobloxWebhook = "https://discord.com/api/webhooks/1076814234538741800/..." # Webook url for the Roblox items.
UGCWebhook = "https://discord.com/api/webhooks/1076814116666232902/..." # Webook url for the user generated items.
authURL = "https://auth.roblox.com/v2/logout" # for getting x-csrf-token.
def fetchItems(api):
    try: response = requests.get(api)
    except: printWithTS("Failed to fetch item list."); time.sleep(5)
    try:
        re= response.json()["data"]
        return re
    except:
        print("Failed to fetch item list:", response.text)
        return []

RobloxItems = fetchItems(RobloxCatalog)
UGCItems = fetchItems(UGCCatalog)
RobloxItemBatch = []
UGCItemBatch = []
RobloxDetailsBatch = []
UGCDetailsBatch = []


def printWithTS(text): # i like timestamps.
    stamp = datetime.now().strftime("%H:%M:%S")
    return print(f"[{stamp}] - {text}")


def itemDetails(Batch):
    url = "https://catalog.roblox.com/v1/catalog/items/details"
    xcsrfReq = requests.post(authURL, cookies={'.ROBLOSECURITY': cookie})
    xcsrf = xcsrfReq.headers["x-csrf-token"]
    try:
        response = requests.post(url, headers={"cookie": ".ROBLOSECURITY=" + cookie + ";", "x-csrf-token": xcsrf, "referer": "https://www.roblox.com/"}, json={"items": Batch})
        return response.json()["data"]
    except:
        printWithTS("Failed to fetch item details.")
        return []



def compareItems(currentItems, previousItems, Batch):
    addedItems = [item for item in currentItems if item not in previousItems]
    if addedItems:
        printWithTS(f"{len(addedItems)} new item(s) added!")
        for item in addedItems:
            # add the item to the batch dictionary with the format
            Batch.append({"id": item['id'], "itemType": item['itemType']})
            printWithTS(f"Added {item['id']} to batch!")
        return currentItems
    else:
        printWithTS("No new items added!")
        return previousItems


def thumbnail(itemid): # getting the thumbnail of the item from roblox because they suck!
    url = f"https://thumbnails.roblox.com/v1/assets?assetIds={itemid}&size=250x250&format=Png"
    try: 
        response = requests.get(url)
        imageUrl = response.json()["data"][0]["imageUrl"]
    except: 
        printWithTS("Failed to get thumbnail!")
        imageUrl = "https://images.rbxcdn.com/9281912c23312bc0d08ab750afa588cc.png"
    return imageUrl


def postItem(item, webhook, batch):
    print(item)
    printWithTS(f"ID: {item['id']}, Type: {item['itemType']}")
    try:
        requests.post(webhook, json={"embeds": [{ # discord webhook info.
                "title": item['name'],
                "url": f"https://www.roblox.com/catalog/{item['id']}",
                # if the price is not there then its off sale
                "fields": [
            # if the price is not there then its off sale
                    {"name": "Price", "value": item['price'] if 'price' in item else item['price'], "inline": True},
                    {"name": "Creator", "value": item["creatorName"], "inline": True},
                    {"name": "Description", "value": item['description']},
                ],
                "color": 0x84FF9B,
                "thumbnail": {"url": thumbnail(item['id'])},}]})
    except:
        printWithTS("Failed to post item to discord webhook.")


def scan():
    global RobloxItems, UGCItems, RobloxItemBatch, UGCItemBatch, RobloxDetailsBatch, UGCDetailsBatch
    scanCount = 0
    while True:
        # scan for new items.
        printWithTS("Scanning for new items...")
        RobloxItems = compareItems(fetchItems(RobloxCatalog), RobloxItems, RobloxItemBatch)
        UGCItems = compareItems(fetchItems(UGCCatalog), UGCItems, UGCItemBatch)
        scanCount += 1
        if scanCount >= 4:# every 4 scans request the item details.
            if not RobloxItemBatch and not UGCItemBatch: # check if there are any items in the batch.
                printWithTS("No items in the batch, skipping details request.")
            else:
                printWithTS("Scanning for item details...")
                # request the item details.
                RobloxDetailsBatch = itemDetails(RobloxItemBatch) 
                UGCDetailsBatch = itemDetails(UGCItemBatch)
                for item in RobloxDetailsBatch: # post the items.
                    postItem(item, RobloxWebhook, RobloxDetailsBatch)
                for item in UGCDetailsBatch: # post the items.
                    postItem(item, UGCWebhook, UGCDetailsBatch)
                print(RobloxDetailsBatch)
                # clear the batches.
                RobloxItemBatch = []
                UGCItemBatch = []
                RobloxDetailsBatch = []
                UGCDetailsBatch = []
            scanCount = 0
        time.sleep(15)
scan()
