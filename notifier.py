import requests
import time
from datetime import datetime

RobloxCatalog = "https://catalog.roblox.com/v1/search/items?category=All&creatorName=Roblox&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3" # catalog link for items created by the Roblox account.
UGCCatalog = "https://catalog.roblox.com/v1/search/items?category=Accessories&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3&subcategory=Accessories" # catalog link for items created by users.
RobloxWebhook = "https://discord.com/api/webhooks/..." # Webook url for the Roblox items.
UGCWebhook = "https://discord.com/api/webhooks/..." # Webook url for the user generated items.

def fetchItems(api):
    response = requests.get(api)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print("Failed to fetch item list:", response.text)
        return []

previousRobloxItems = fetchItems(RobloxCatalog)
previousUGCItems = fetchItems(UGCCatalog)

def printWithTS(text): # i like timestamps.
    stamp = datetime.now().strftime("%H:%M:%S")
    return print(f"[{stamp}] - {text}")

def thumbnail(itemid): # getting the thumbnail of the item from roblox because they suck!
    url = f"https://thumbnails.roblox.com/v1/assets?assetIds={itemid}&size=250x250&format=Png"
    response = requests.get(url)
    imageUrl = response.json()["data"][0]["imageUrl"]
    return imageUrl

def itemDetails(itemid):
    url = f"https://api.roblox.com/marketplace/productinfo?assetId={itemid}"
    response = requests.get(url)
    return response.json()

def postItem(item, webhook):
    try: # try to get the item details, but if it fails, just wait 30 seconds and try again.
        details = itemDetails(item['id'])
    except: # ratelimited part
        printWithTS("Waiting 30 seconds to fetch item details because of ratelimit!")
        time.sleep(30)
        details = itemDetails(item['id'])

    printWithTS(f"ID: {item['id']}, Type: {item['itemType']}")
    requests.post(webhook, json={"embeds": [{ # discord webhook info.
                "title": details['Name'],
                "url": f"https://www.roblox.com/catalog/{item['id']}",
                "fields": [
                    {"name": "Price", "value": details['PriceInRobux'], "inline": True},
                    {"name": "Creator", "value": details["Creator"]["Name"], "inline": True},
                    {"name": "Description", "value": details['Description']},
                ],
                "color": 0x84FF9B,
                "thumbnail": {"url": thumbnail(item['id'])},
        }]})


def compareItems(currentItems, previousItems, webhook):
    addedItems = [item for item in currentItems if item not in previousItems]
    if addedItems:
        printWithTS(f"{len(addedItems)} new item(s) added!")
        for item in addedItems:
            postItem(item, webhook)
    return currentItems

def scan():
    while True:
        printWithTS("Checking for new items in 15 seconds!")
        time.sleep(15)  # wait so you dont get ratelimited.
        global previousRobloxItems
        global previousUGCItems
        previousRobloxItems = compareItems(fetchItems(RobloxCatalog), previousRobloxItems, RobloxWebhook)
        previousUGCItems = compareItems(fetchItems(UGCCatalog), previousUGCItems, UGCWebhook)
        printWithTS("Done checking!")

scan()
