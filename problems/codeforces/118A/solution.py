vowels = ["a", "e", "i", "o", "u", "y"]
s = input().lower()

res = ""
for ch in s:
    if ch in vowels:
        continue
    else:
        res += "." + ch

print(res)
