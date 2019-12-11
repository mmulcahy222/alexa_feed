# Alexa RSS News Reader

Do not use this, and I don't use this anymore.

This read the newspaper articles of various RSS feeds over the internet, chosen by a number.

If the Alexa "Speech Output" response exceeded the 8000 character limit, it offered a continue option.

One notable feature of this interesting Alexa Skill was deploying the Newspaper Python Module every time I pushed a code change

```
zip -r feed.zip . && aws lambda update-function-code --function-name media --region us-east-1 --zip-file file://C:\***\feed.zip
```

NOTE: None of my Alexa Skills used the state design pattern which I have used in subsequent projects like https://www.github.com/mmulcahy222/google_bookmarks. I was learning here.



