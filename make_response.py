import hashlib
import time

key = "ayylmao123"
nick = "fwilson"

def commandtoken(nick, command):
    timestr = str(time.time() // 300)
    return hashlib.sha1("{}{}{}{}".format(timestr, nick, command, key).encode()).hexdigest()

split = input("command: ").split()
command, args = split[0], split[1:]

print(command, commandtoken(nick, ":".join([command, ",".join(args)])), " ".join(args))
