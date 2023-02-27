import requests
import time
from datetime import datetime

Cookie = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_..." # roblo security cookie, needed to get the item details in a batch request.
CatalogAPI = "https://catalog.roblox.com/v1/search/items?category=Accessories&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3&subcategory=Accessories" # catalog link for items created by users.
Webhook = "https://discord.com/api/webhooks/..." # Webook url for the Roblox items.
AuthURL = "https://auth.roblox.com/v2/logout" # for getting x-csrf-token.
def fetchItems(api):
    response = requests.get(api)
    try: return response.json()["data"]
    except:
        print("Failed to fetch item list.")
        return []

Items = fetchItems(CatalogAPI)
ItemBatch = []
DetailsBatch = []


def printWithTS(text): # i like timestamps.
    stamp = datetime.now().strftime("%H:%M:%S")
    return print(f"[{stamp}] - {text}")


def itemDetails(Batch):
    url = "https://catalog.roblox.com/v1/catalog/items/details"
    xcsrfReq = requests.post(AuthURL, cookies={'.ROBLOSECURITY': Cookie})
    xcsrf = xcsrfReq.headers["x-csrf-token"]
    try:
        response = requests.post(url, headers={"cookie": ".ROBLOSECURITY=" + Cookie + ";", "x-csrf-token": xcsrf, "referer": "https://www.roblox.com/"}, json={"items": Batch})
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
                    {"name": "Description", "value": item['description'].splitlines()[0]}
                ],
                "color": 0x84FF9B,
                "image": {"url": thumbnail(item['id'])},
                }]})
    except:
        printWithTS("Failed to post item to discord webhook.")


def scan():
    global Items, ItemBatch, DetailsBatch
    scanCount = 0
    while True:
        # scan for new items.
        printWithTS("Scanning for new items...")
        Items = compareItems(fetchItems(CatalogAPI), Items, ItemBatch)
        scanCount += 1
        if scanCount >= 4:# every 4 scans request the item details.
            if not ItemBatch: # check if there are any items in the batch.
                printWithTS("No items in the batch, skipping details request.")
            else:
                printWithTS("Scanning for item details...")
                # request the item details.
                ItemDetailsBatch = itemDetails(ItemBatch)
                for item in ItemDetailsBatch: # post the items.
                    postItem(item, Webhook, DetailsBatch)
                # clear the batches.
                ItemBatch = []
                DetailsBatch = []
            scanCount = 0
        time.sleep(15)
scan()
