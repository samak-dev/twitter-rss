from flask import Flask, Response
import subprocess
import json
import datetime

app = Flask(__name__)

@app.route('/twitter/<username>')
def twitter_feed(username):
    try:
        # Run snscrape command
        result = subprocess.run(
            ['snscrape', '--jsonl', '--max-results', '10', f'twitter-user:{username}'],
            capture_output=True, text=True, check=True
        )
        tweets = [json.loads(line) for line in result.stdout.strip().split('\n') if line]

        rss_items = ""
        for tweet in tweets:
            pub_date = datetime.datetime.strptime(tweet['date'], "%Y-%m-%dT%H:%M:%S%z").strftime("%a, %d %b %Y %H:%M:%S GMT")
            rss_items += f"""
            <item>
                <title><![CDATA[{tweet['content'][:100]}]]></title>
                <link>https://twitter.com/{username}/status/{tweet['id']}</link>
                <pubDate>{pub_date}</pubDate>
                <description><![CDATA[{tweet['content']}]]></description>
            </item>
            """

        rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
        <channel>
            <title>Twitter Feed for @{username}</title>
            <link>https://twitter.com/{username}</link>
            <description>Latest tweets from @{username}</description>
            {rss_items}
        </channel>
        </rss>
        """

        return Response(rss_feed, content_type="application/rss+xml; charset=utf-8")

    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
