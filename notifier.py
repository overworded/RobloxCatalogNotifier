import requests
import time
from datetime import datetime

RobloxCatalog = "https://catalog.roblox.com/v1/search/items?category=All&creatorName=Roblox&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3"
UGCCatalog = "https://catalog.roblox.com/v1/search/items?category=Accessories&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3&subcategory=Accessories"
RobloxWebhook = "https://discord.com/api/webhooks/......"
UGCWebhook = "https://discord.com/api/webhooks/......"

def fetchItems(api):
    response = requests.get(api)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print("Failed to fetch item list:", response.text)
        return []

previousRobloxItems = fetchItems(RobloxCatalog)
previousUGCItems = fetchItems(UGCCatalog)

def printWithTS(text):
    stamp = datetime.now().strftime("%H:%M:%S")
    return print(f"[{stamp}] - {text}")

def thumbnail(itemid):
    url = f"https://thumbnails.roblox.com/v1/assets?assetIds={itemid}&size=250x250&format=Png"
    response = requests.get(url)
    imageUrl = response.json()["data"][0]["imageUrl"]
    return imageUrl

def itemDetails(itemid):
    url = f"https://api.roblox.com/marketplace/productinfo?assetId={itemid}"
    response = requests.get(url)
    return response.json()

def compareItems(currentItems, previousItems, webhook):
    addedItems = [item for item in currentItems if item not in previousItems]
    if addedItems:
        printWithTS(f"{len(addedItems)} new item(s) added!")
        for item in addedItems:
            itemDetails = itemDetails(item['id'])
            printWithTS(f"ID: {item['id']}, Type: {item['itemType']}")
            requests.post(webhook, json={"embeds": [{
                        "title": itemDetails['Name'],
                        "url": f"https://www.roblox.com/catalog/{item['id']}",
                        "fields": [
                            {"name": "Price", "value": itemDetails['PriceInRobux'], "inline": True},
                            {"name": "Creator", "value": itemDetails["Creator"]["Name"], "inline": True},
                            {"name": "Description", "value": itemDetails['Description']},
                        ],
                        "color": 0x84FF9B,
                        "thumbnail": {"url": thumbnail(item['id'])},
                        "footer": {"text": itemDetails['Creator']['Name']},
                        "timestamp": itemDetails['Created']
                }]})
    return currentItems

def scan():
    while True:
        printWithTS("Checking for new items in 15 seconds!")
        time.sleep(15)  # wait for 5 seconds before checking again
        global previousRobloxItems
        global previousUGCItems
        previousRobloxItems = compareItems(fetchItems(RobloxCatalog), previousRobloxItems, RobloxWebhook)
        previousUGCItems = compareItems(fetchItems(UGCCatalog), previousUGCItems, UGCWebhook)
        printWithTS("Done checking!")

scan()
