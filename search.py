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
def landing() -> None:
    # Load tags
    config = load(open('config.json', 'r'))
    includes = obtain_tags(config['tags']['include'])
    excludes = obtain_tags(config['tags']['exclude'])

    # Get Manga items
    starter = make_request(includes, excludes)
    filtered = filter_mangadex(starter)

    # Get Manga covers
    cover_ids = get_cover_ids(filtered)
    cover_filenames = obtain_cover_filenames(cover_ids)

    return render_template('index.html', context={
        'filtered': filtered,
        'covers': cover_filenames
    })
    
# === Helpers ===

def make_request(includes: list[str], excludes: list[str], offest=0) -> dict:
    """
    Makes a request to the MangaDex Search API
    """
    res = r.get(
        f"{BASE_URL}/manga",
        params={
            "includedTags[]": includes,
            "excludedTags[]": excludes,
            "order[followedCount]": 'desc',
            "limit": 100,
            "offset": offest
        }
    )
    clean = res.json()
    
    # Validate
    if (not clean) or (not 'data' in clean):
        print('Error in request.', flush=True)
        return 0
    return clean


def obtain_tags(tags: list[str]) -> list[str]:
    """
    Obtains the IDs of the tags given the plaintext inputs.
    """
    return [
        tag["id"]
        for tag in TAGS["data"]
        if tag["attributes"]["name"]["en"]
        in tags
    ]


def filter_mangadex(mangadex_res: dict) -> list:
    """
    Filters the MangaDex response using custom filters. Current conditions:
    - Has a MyAnimeList link
    """
    # Ensure that there is a mal link
    filtered = []
    for manga in mangadex_res['data']:
        links = manga['attributes']['links']
        if links and 'mal' in links:
            filtered.append(manga)
    return filtered


def get_cover_ids(mangadex_res: dict) -> list:
    """
    Parses the cover art ID from the MangaDex response object.
    """
    relationships = list(map(lambda x: x['relationships'], mangadex_res))
    cover_ids_pre = [
        relationship for sublist in relationships
        for relationship in sublist
            if relationship['type'] == 'cover_art'
    ]
    cover_ids = list(map(lambda x: x['id'], cover_ids_pre))
    return cover_ids


def obtain_cover_filenames(manga_cover_ids: list[str]) -> list[str]:
    """
    Given a Manga Cover ID, will obtain the filename. Necessary for displaying the image.
    """
    # Make MangaDex Query
    query_string = '&ids[]='.join(manga_cover_ids)
    res = r.get(
        f'{BASE_URL}/cover?ids[]={query_string}',
        params={
            'limit': 100
        }
    )
    clean = res.json()

    # Process Query to obtain valid pairs
    filenames = {}
    for manga_entry in clean['data']:
        filename = manga_entry['attributes']['fileName']
        manga_relation = list(filter(lambda x: x['type'] == 'manga', manga_entry['relationships']))
        manga_id = manga_relation[0]['id']
        filenames[manga_id] = filename

    return filenames
