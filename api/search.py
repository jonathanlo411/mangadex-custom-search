# Imports
import requests as r
from flask import Flask, request, render_template, Response
from dotenv import load_dotenv
import os

# Setup
load_dotenv()
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
    offest = 0
    if 'p' in request.args and len(request.args['p']) > 0:
        offest = int(request.args['p']) * 100

    # Handle tag logic
    includes: list[str] = []
    excludes: list[str] = []
    if 'includes[]' in request.args or 'excludes[]' in request.args:    # Hard Search
        include_raw = request.args.getlist('includes[]')
        exclude_raw = request.args.getlist('excludes[]')
        includes = obtain_tags(include_raw)
        excludes = obtain_tags(exclude_raw)

    # Process original language
    original_language = request.args['ln'] if 'ln' in request.args else None

    # Process MyAnimeList
    has_mal = not (request.args['noMal'] if 'noMal' in request.args else False)
    mal_user = request.args['malUser'] if 'malUser' in request.args else None
    mal_min_score = request.args['malMinScore'] if 'malMinScore' in request.args else None

    # Get Manga items
    starter = make_request(includes, excludes, offest, original_language)
    if starter == 0: return render_template('index.html', context={'filtered':{}})
    filtered = filter_mangadex(starter, has_mal, mal_user, mal_min_score)

    # Get Manga covers
    cover_filenames = obtain_cover_filenames(filtered)

    # Get result settings
    display_en = request.args['displayEn'] if 'displayEn' in request.args else False

    return render_template('index.html', context={
        'filtered': filtered,
        'covers': cover_filenames,
        'display_en': bool(display_en)
    })


@app.route('/about', methods=['GET'])
def about() -> None:
    return render_template('about.html')


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
        "offset": min(9999, offest),
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


def filter_mangadex(
        mangadex_res: dict,
        has_mal=True,
        malUser=False,
        minMalScore=0
    ) -> list:
    """
    Filters the MangaDex response using custom filters. Current conditions:
    - Has a MyAnimeList link
    - Not in a User's MyAnimeList Manga list
    - Has a minimum MyAnimelist score
    """
    filtered = []
    if has_mal:
        if malUser:
            # Check if in user Manga list
            res = r.get(
                f'https://api.myanimelist.net/v2/users/{malUser}/mangalist',
                params={
                    'limit': 1000,
                    'manga_id': 'Descending',
                    'nsfw': True
                },
                headers={
                    'X-MAL-CLIENT-ID': os.getenv('MAL_CID')
                }            
            )
            clean = res.json()


            # Validate
            if not 'data' in clean:
                print('Someting went wrong!', flush=True)
                return []
            id_hash_table = {item['node']['id']: True for item in clean['data']}


        # Ensure that there is a mal link
        for manga in mangadex_res['data']:
            links = manga['attributes']['links']
            if links and 'mal' in links:

                # Check the MAL score
                mal_link = links['mal']
                if minMalScore and not check_myanimelist_score(mal_link, minMalScore):
                    continue

                # Check that it is not in user's list
                if malUser and int(mal_link) in id_hash_table:
                    continue

                filtered.append(manga)
    else:
        return mangadex_res['data']

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

def check_myanimelist_score(myanimelist_id: int, min_score: float) -> bool:
    """
    Fetches MyAnimeList data to check score is above the minimum threshold.
    """
    # Make Request
    res = r.get(
        f'https://api.myanimelist.net/v2/manga/{myanimelist_id}?fields=mean',
        headers={
            'X-MAL-CLIENT-ID': os.getenv('MAL_CID')
        }
    )
    clean = res.json()
    
    # Validate
    if not 'mean' in clean:
        return False
    return clean['mean'] > float(min_score)