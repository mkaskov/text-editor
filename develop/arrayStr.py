from collections import Counter

str = [
    "string 1",
    "string 2",
    "string 3",
    "string 4",
    "string 2"
]

print str

c = Counter(str)

print c.items()

sss = list(c)

print len(sss)



