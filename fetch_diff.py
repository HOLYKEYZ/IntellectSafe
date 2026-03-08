import urllib.request
url = "https://github.com/HOLYKEYZ/IntellectSafe/pull/8.diff"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    diff = response.read().decode('utf-8')
    print("=== DIFF ===")
    print(diff)
