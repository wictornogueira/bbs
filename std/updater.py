import os
import hashlib
from urllib import request
from json import JSONDecoder

URL = "https://api.github.com/repos/wictornogueira/bbs/contents/std"
CURR_PATH = os.path.dirname(os.path.abspath(__file__))

def update ():
  try:
    res = request.urlopen(URL)
    parsed = JSONDecoder().decode(res.read().decode("utf-8"))
    for rFile in parsed:
      if rFile["type"] != "file":
        continue

      fullPath = os.path.join(CURR_PATH, rFile["name"])
      if os.path.exists(fullPath):
        lFile = open(fullPath, "rb")

        lContent = lFile.read()
        lLength = len(lContent)

        lFile.close()

        if lLength == rFile["size"]:
          lStr = lContent.decode("utf-8")

          lRaw = f"blob {lLength}\0{lStr}".encode("utf-8")
          lHash = hashlib.sha1(lRaw).hexdigest()
          
          if lHash == rFile["sha"]:
            continue

      request.urlretrieve(rFile["download_url"], fullPath)
  except:
    pass

update()
