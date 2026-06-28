# AI for Africa Bootcamp 2026 Website

Static landing page for the official AI for Africa Bootcamp 2026 website.

## Local development

1. Edit the structured content in `content/*.json`.
2. Run `python3 build.py` to generate the site in `site/`.
3. Open `site/index.html` in a browser or serve `site/` with any static file server.

## Build

Run `python3 build.py` to regenerate the production output in `site/`.

## Source structure

- `content/site.json` contains site metadata, navigation, hero copy, facts, and footer text.
- `content/about.json`, `content/keynotes.json`, `content/program.json`, `content/announcements.json`, and `content/organizers.json` hold the section content.
- `src/site.css` contains the shared stylesheet.
- `src/site.js` contains the minimal navigation behavior.
- `static/` contains the favicon and placeholder portrait asset copied into the published site.
