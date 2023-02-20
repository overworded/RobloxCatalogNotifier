import requests
import time
from datetime import datetime

cookie = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_BC415058B20577C03FD5C6EA04459562D206D4BD4CD0A680292E61613AEA3045A40B62ACB40A7E76A842C5B513DD6E7AF3B82692E80277B8E7FF4D632A92A5817C4E60035589E7B8044B6F68F63508A022D593A9B21BFA5E4C254CC621BC9537C29F1F56D052EBD8B832DC01484AFA745B4ED85FFDA3A3E5B62CFC30204AD4A092E80ED66EEA4EDBA46559AD43023AE06F7A613B1C821243752D1C3DDADB731B78AE546C021ACE4D56BCC6199395B69C216282141F86DABFB25ED31EDB59EEB1568F68C48619E200F5F785E7EA621F0F1029DA42C49DB6C43BDBCC3F9026D45B516F6CB6B7E588C4C57018FA0905898ED9B1A1AD4CFEB769C496D5EDD61FED97DC3C5AB60032B7E1F2E7BEC4BDA3B69E38AD1E6B1DF2601831E183FDCBDABCF1EF87A71A118FAD3C20C30FDDD214563F412D341B5F11698D15B8283DA3BD1DB9AA87E31A4D2605D385485534309B640EB1BCE16A1657A420FD670A3B64DFFCC9025E4295D6A2AD57F4EF094694B4D93ED3CA4DCD" # roblo security cookie, needed to get the item details in a batch request.
RobloxCatalog = "https://catalog.roblox.com/v1/search/items?category=All&creatorName=Roblox&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3" # catalog link for items created by the Roblox account.
UGCCatalog = "https://catalog.roblox.com/v1/search/items?category=Accessories&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3&subcategory=Accessories" # catalog link for items created by users.
RobloxWebhook = "https://discord.com/api/webhooks/1076814234538741800/0mEqqd4Lxv8W_q-JthU4Kgwwek8LdEI8BRtZPq3cNokZ45LC2JaKe4cihdpQXWoLvHaF" # Webook url for the Roblox items.
UGCWebhook = "https://discord.com/api/webhooks/1076814116666232902/qpSMZS9-4f5dnJpB863xpwywjkISgYF_C1vLKbugaTt-P-I7btjK8OvPyRCsLwbRMkyp" # Webook url for the user generated items.
authURL = "https://auth.roblox.com/v2/logout" # for getting x-csrf-token.
def fetchItems(api):
    try: response = requests.get(api)
    except: printWithTS("Failed to fetch item list."); time.sleep(5)
    if response.status_code == 200:
        return response.json()["data"]
    else:
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
            Batch.append({"itemType": item['itemType'], "id": item['id']})
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
                    {"name": "Price", "value": f"{item['price'] if 'price' in item else 'Off Sale'}", "inline": True},
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
