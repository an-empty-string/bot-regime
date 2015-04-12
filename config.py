host = "raphus.pdgn.co"
prefix = "czar_"
with open("key") as keyfile:
    key = keyfile.read().strip()

channels = [i.strip() for i in open("channels").readlines()]
