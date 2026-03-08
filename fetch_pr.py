import json
import urllib.request
import re

url = "https://api.github.com/repos/HOLYKEYZ/IntellectSafe/pulls/8"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf-8'))
    
body = data.get('body', '')
print("PR Body Extract:")
print(body[:2000]) # Print first part to see if edits are in there
