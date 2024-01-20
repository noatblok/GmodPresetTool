import json, time, requests
import concurrent.futures
import tkinter as tk
from bs4 import BeautifulSoup
from datetime import datetime
from tkinter import filedialog
def prettify_file_details(files):
    formatteddata = ""
    print(len(files))
    for file in files:
        if file["result"] == 1:
            createdstr = datetime.fromtimestamp(file["time_created"],tz=None).strftime("%A %B %d %Y, at %I:%M %p")
            updatedstr = datetime.fromtimestamp(file["time_updated"],tz=None).strftime("%A %B %d %Y, at %I:%M %p")
            filedata = f"================\nTitle: {file['title']}\nCreated: {createdstr}\nUpdated: {updatedstr}\nURL: https://steamcommunity.com/sharedfiles/filedetails/?id={file['publishedfileid']}\n================\n\n"
            formatteddata += filedata
    return formatteddata

def get_file_details(ids):
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    params = {
        "itemcount": len(ids)
    }
    i = 0
    for id in ids:
        params[f"publishedfileids[{i}]"] = id
        i += 1
    r = requests.post(url, data=params)
    data = r.json()["response"]
    with open("e.json", "w") as f:
        json.dump(data, f, indent=4)
    return data["publishedfiledetails"]
def get_collection_files(colid):
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
    params = {
        "collectioncount": 1,
        "publishedfileids[0]": colid
    }
    r = requests.post(url, data=params)
    data = r.json()
    newdata = []
    for file in data["response"]["collectiondetails"][0]["children"]:
        newdata.append(int(file["publishedfileid"]))
    return newdata
def process_file(file):
    out = []
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={file}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    reqitems = soup.find_all("a", {"data-subscribed": 0})
    if reqitems != []:
        for item in reqitems:
            itemid = int(item.attrs["href"].split("?id=")[1])
            out.append(itemid)
    return out

alldependencies = []
def get_file_dependencies(files):
    dependencies = []
    start = time.time()
    executor = concurrent.futures.ThreadPoolExecutor(len(files))
    futures = [executor.submit(process_file, file) for file in files]
    concurrent.futures.wait(futures)
    for future in futures:
        result = future.result()
        for dependent in result:
            if dependent not in dependencies and dependent not in alldependencies:
                dependencies.append(dependent)
    alldependencies.extend(dependencies)
    #print("DID DA TING BOSSMAN") To whom this may concern, I legit used this for debugging and I thought I'd leave this here, let me know if I got a laugh out of you.
    if len(dependencies) != 0:
        get_file_dependencies(dependencies)
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    addonpreset_path = filedialog.askopenfilename("Open the \"addonpresets.txt\" file within GarrysMod/garrysmod/settings") # No code to verify this is a valid addonpresets.txt, be careful
    presetname = f"Generated Preset {int(datetime.now().timestamp())}"
    colids = [2929171816, 590303919, 180077636] # Change collection ID's to what you want, user input coming soon.
    allfiles = []
    for col in colids:
        colfiles = get_collection_files(col)
        data = get_file_dependencies(colfiles)
        allfiles.extend(list(set(alldependencies + colfiles)))

    with open("out.txt", "w") as f:
        f.write(prettify_file_details(get_file_details(allfiles)))
    with open(addonpreset_path, "r") as f:
        presetdata = json.load(f)
    presetdata[presetname] = {
        "disabled": [],
        "enabled": [str(fileid) for fileid in allfiles],
        "name": presetname,
        "newAction": ""
    }
    with open(addonpreset_path, "w") as f:
        f.write(json.dumps(presetdata))