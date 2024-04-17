# Imports
import requests as r
from flask import Flask, request, render_template, Response

# Setup
app = Flask(__name__)

# Globals
BASE_URL = "https://api.mangadex.org"
TAGS: dict = r.get(
    f"{BASE_URL}/manga/tag"
).json()


# --- Page Render ---
@app.route('/', methods=['GET'])
def landing() -> None:
    # Process pagination
    offest = int(request.args['p']) * 100 if 'p' in request.args else 0

    # Handle tag logic
    includes: list[str] = []
    excludes: list[str] = []
    if 'includes[]' in request.args or 'excludes[]' in request.args:    # Hard Search
        include_raw = request.args.getlist('includes[]')
        exclude_raw = request.args.getlist('excludes[]')
        includes = obtain_tags(include_raw)
        excludes = obtain_tags(exclude_raw)

    # Process original language
    original_language = None
    if 'ln' in request.args:
        original_language = request.args['ln']

    # Get Manga items
    starter = make_request(includes, excludes, offest, original_language)
    filtered = filter_mangadex(starter)

    # Get Manga covers
    cover_filenames = obtain_cover_filenames(filtered)

    return render_template('index.html', context={
        'filtered': filtered,
        'covers': cover_filenames
    })


# --- APIs ---
@app.route('/mdimg', methods=['GET'])
def get_image() -> Response:
    manga_id = request.args['md']
    filename = request.args['fn']
    res = r.get(
        f'https://uploads.mangadex.org/covers/{manga_id}/{filename}'
    )
    return Response(res.content, headers=dict(res.headers))

@app.route('/tags', methods=['GET'])
def get_tags() -> Response:
    tag_names = list(map(lambda x: x['attributes']['name']['en'], TAGS['data']))
    return tag_names, 200

# === Helpers ===

def make_request(
        includes: list[str],
        excludes: list[str],
        offest=0,
        original_language=None
    ) -> dict:
    """
    Makes a request to the MangaDex Search API
    """
    # Handle parameter logic
    params = {
        "includedTags[]": includes,
        "excludedTags[]": excludes,
        "order[followedCount]": 'desc',
        "limit": 100,
        "offset": offest,
        "includes[]": 'cover_art',
    }
    if original_language:
        params['originalLanguage[]'] = original_language

    # Make request
    res = r.get(
        f"{BASE_URL}/manga",
        params=params
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


def obtain_cover_filenames(mangadex_res: dict) -> dict:
    """
    Iterates through manga results returned from filter_mangadex() and
    finds their cover art filenames.

    Returns a dictionary with the MangaDex ID
    and its corresponding cover art filename.
    """
    filenames = {}
    for manga in mangadex_res:
        for relation in manga["relationships"]:
            if relation["type"] == "cover_art":
                cover_art_filename = relation["attributes"]["fileName"]
                manga_id = manga["id"]
                filenames[manga_id] = cover_art_filename
                continue

    return filenames