import hashlib
key = "ayylmao123"
nick = "fwilson"

def commandtoken(nick, command):
    return hashlib.sha1("{}{}{}".format(nick, command, key).encode()).hexdigest()

split = input("command: ").split()
command, args = split[0], split[1:]

print(command, commandtoken(nick, ":".join([command, ",".join(args)])), " ".join(args))
