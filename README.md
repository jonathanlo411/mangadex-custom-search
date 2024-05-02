# MangaDex Custom Search
<a  href="https://github.com/jonathanlo411/mangadex-custom-search/releases"><img  src="https://img.shields.io/github/v/release/jonathanlo411/mangadex-custom-search"></a><a  href="https://github.com/jonathanlo411/mangadex-custom-search/blob/main/LICENSE"><img  src="https://img.shields.io/github/license/jonathanlo411/mangadex-custom-search"></a>

This website serves as a custom way to search through MangaDex titles. It has most of the functionallity of the original but is more tailored for me. Currently it only shows entries that have a MyAnimeList link.

## Using Locally
1. Clone the repository.
2. `cd` into the repo directory and create a virtual enviroment. Download the packages as defined in `requirements.txt`.
```bash
python3 -m venv venv
. venv/bin/activate  # or . venv/Scripts/activate if on windows
pip install -r requirements.txt
```
3. Create a `.env` file following the schema of `sample.env`
4. Launch the Flask app by running the following
```
flask --app api/search run
```

## License
This project is licensed under the MIT License. See `LICENSE` for more information.
