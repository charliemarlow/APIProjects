import json

with open('test.json') as f:
    test = json.load(f)

for t in test:
    print(t['Name'])
