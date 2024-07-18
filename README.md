# UV Warning Bot - Melbourne

## Summary
During the summer I spend a lot of time thinking about whether it's safe to be outside without a hat / sunscreen. I check ARPANSA all the time to see what the current UV is, and when it is projected to be > 3.0 - when sunsmartness is recommended.

This is a bot that checks ARPANSA for me, and lets me know via Telegram whether it is safe to be outside without sun protection or not.

## Messaging Logic
I didn't want the bot to be constantly spamming me with irrelevant information - so I decided to make it only run every hour between 8am and 5pm. 
Additionally - it will save the latest reading to DynamoDB, and will only message if:
  - The previous reading was below 3.0, and the latest is above 3.0 (Put on a hat!)
  - The previous reading was above 3.0, and the latest is below 3.0 (It's safe!)

## Screenshots
I set up a channel that the bot can post to to give me updates!

![Screenshot from 2024-07-18 21-20-32](https://github.com/user-attachments/assets/2bf6d625-8737-42c3-be34-c277d94c56c0)
