#IGNORE, Does nothing.

import json
with open(r"E:\SteamLibrary\steamapps\common\GarrysMod\garrysmod\settings\addonpresets.txt", "r") as f:
    data = json.load(f)
with open("addonpresets.json", "w") as f:
    json.dump(data, f, indent=4)