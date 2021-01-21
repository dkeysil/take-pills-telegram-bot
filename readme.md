# Take Pills telegram bot

[![Try it out!](https://i.imgur.com/nTXvBYA.jpg)](https://t.me/take_pills_bot)

This bot is made to remind you about the pills you prescript to take. You can add a new type of medicine with the `/new` command. The bot will ask you the name of the medicine and the time you'd like to receive the reminders.  

[![Reminds you when you want to!](https://i.imgur.com/rdhqYaX.png)](https://t.me/take_pills_bot)

It will remind you to take a pill until you press the "took it" button every five minutes.

[![Reminds you as many times as you need to!](https://i.imgur.com/Ktmb7Sp.png)](https://t.me/take_pills_bot)


When the treatment is about to end you can make the bot stop to remind you about the pills using the `/pills` command.

Try it and make your life easier right now - https://t.me/take_pills_bot


### How to run it by yourself:
To run it you just need Docker and docker-compose.
Set up your Telegram Bot Api token in `docker-compose.creds.yml`
```yml
    environment:
      BOT_API_KEY: "telegram-bot-api-token"
```
And then start it
```sh
docker-compose -f docker-compose1.creds.yml -f docker-compose.yml up --build -d
```
