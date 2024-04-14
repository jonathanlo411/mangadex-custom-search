# Imports
import requests as r
from json import load
from flask import Flask, request, render_template

# Setup
app = Flask(__name__)

# Globals
BASE_URL = "https://api.mangadex.org"
TAGS = r.get(
    f"{BASE_URL}/manga/tag"
).json()


# --- Page Render ---
@app.route('/', methods=['GET'])
def main():
    # Load tags
    config = load(open('config.json', 'r'))
    includes = obtain_tags(config['tags']['include'])
    excludes = obtain_tags(config['tags']['exclude'])

    # Make request to MangaDex
    res = r.get(
        f"{BASE_URL}/manga",
        params={
            "includedTags[]": includes,
            "excludedTags[]": excludes,
            "order[followedCount]": 'desc',
            "limit": 100
        }
    )
    clean = res.json()

    # Validate
    if (not clean) or (not 'data' in clean):
        print('Error in request.')
        return 0

    # Ensure that there is a mal link
    filtered = []
    for manga in clean['data']:
        links = manga['attributes']['links']
        if links and 'mal' in links:
            filtered.append(manga)

    return render_template('index.html', context={'filtered': filtered})
    


def obtain_tags(tags: list[str]) -> list[str]:
    return [
        tag["id"]
        for tag in TAGS["data"]
        if tag["attributes"]["name"]["en"]
        in tags
    ]

if __name__ == '__main__':
    main()