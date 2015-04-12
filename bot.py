from asyncirc import irc
import asyncirc.plugins.addressed

import config
import hashlib
import logging
import string
import random
logger = logging.getLogger("czarbot")
logging.basicConfig(level=logging.INFO)

bot = irc.connect(config.host)
bot.register(config.prefix + str(random.randint(10**6, 10**7 - 1)), "regime", "bot regime")

@bot.on("irc-001")
def join_stuff(message):
    logger.info("autojoining channels")
    bot.join(config.channels)

def generate_challenge(nick):
    challenge = "".join([random.choice(string.ascii_lowercase) for i in range(40)])
    response = hashlib.sha1("{}{}{}".format(challenge, config.key, nick).encode()).hexdigest()
    return challenge, response

def completestr(nick, channel):
    return hashlib.sha1("{}{}{}".format(nick, channel, config.key).encode()).hexdigest()

def commandtoken(nick, command):
    return hashlib.sha1("{}{}{}".format(nick, command, config.key).encode()).hexdigest()

challenges = {}
done = []

@bot.on("addressed")
def on_addressed(message, user, target, text):
    if text == "opme":
        challenge, response = generate_challenge(user.nick)
        if user.nick not in challenges:
            challenges[user.nick] = {}
        challenges[user.nick][response] = target
        bot.say(user.nick, "Your challenge for {} is {}".format(target, challenge))

@bot.on("public-message")
def on_pubmsg(message, user, target, text):
    split = text.split()
    command, token, args = split[0], split[1], split[2:]
    valid_token = commandtoken(user.nick, ":".join([command, ",".join(args)]))
    if valid_token != token:
        return
    if command == "addchan":
        channel = args[0]
        if channel in config.channels:
            bot.say(target, "channel already known!")
            return
        config.channels.append(channel)
        with open("channels", "w") as f:
            f.write("\n".join(config.channels))
        bot.join(channel)
        bot.say(target, "ok")
    if command == "rmchan":
        channel = args[0]
        if channel not in config.channels:
            bot.say(target, "channel already unknown!")
            return
        config.channels.remove(channel)
        with open("channels", "w") as f:
            f.write("\n".join(config.channels))
        bot.part(channel)
        bot.say(target, "ok")

@bot.on("join")
def on_join(message, user, channel):
    if user.nick == bot.nickname:
        return
    if user.nick not in challenges:
        challenges[user.nick] = {}
    if user.nick.startswith(config.prefix):
        logger.info("{} joins, sending challenge".format(user.nick))
        challenge, response = generate_challenge(user.nick)
        bot.say(user.nick, "CHALLENGE {} {}".format(channel, challenge))
        challenges[user.nick][response] = channel

@bot.on("private-message")
def on_message(message, user, target, text):
    logger.info("got a message")
    response = text
    if user.nick in challenges and response in challenges[user.nick]:
        chan = challenges[user.nick][response]
        del challenges[user.nick][response]
        logger.info("challenge success for {}".format(user.nick))
        bot.writeln("MODE {} +o {}".format(chan, user.nick))
        bot.say(user.nick, "COMPLETE {} {}".format(chan, completestr(user.nick, chan)))
    elif text.startswith("CHALLENGE "):
        chan, text = text.replace("CHALLENGE ", "").split()
        logger.info("got challenge from {}, responding".format(user.nick))
        bot.say(user.nick, hashlib.sha1("{}{}{}".format(text, config.key, target).encode()).hexdigest())
    elif text.startswith("COMPLETE "):
        chan, text = text.replace("COMPLETE ", "").split()
        if text == completestr(target, chan):
            done.append(chan)
    elif user.nick in challenges:
        del challenges[user.nick]

import asyncio
asyncio.get_event_loop().run_forever()
