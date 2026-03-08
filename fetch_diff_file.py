import urllib.request
url = "https://github.com/HOLYKEYZ/IntellectSafe/pull/8.diff"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    diff = response.read().decode('utf-8')
    with open("pr8_diff.txt", "w", encoding="utf-8") as f:
        f.write(diff)
print("Saved PR #8 diff to pr8_diff.txt")
