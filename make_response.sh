#!/bin/bash
NICK="fwilson"
KEY="ayylmao123"

read -p "Challenge: " challenge
echo "PRIVMSG this string to the bot: "
echo -n $challenge$KEY$NICK | sha1sum
