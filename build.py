from __future__ import annotations

import json
import html
import shutil
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "site"
SRC_DIR = ROOT / "src"
STATIC_DIR = ROOT / "static"
CONTENT_DIR = ROOT / "content"
ASSET_VERSION = date.today().isoformat()


def load_json(filename: str):
    with (CONTENT_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


site = load_json("site.json")
about = load_json("about.json")
keynotes = load_json("keynotes.json")
program = load_json("program.json")
announcements = load_json("announcements.json")
organizers = load_json("organizers.json")


def format_date(value: str) -> str:
    day = date.fromisoformat(value)
    return f"{day.day} {day.strftime('%b %Y')}"


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_button(cta: dict) -> str:
    classes = "button button-primary" if cta.get("emphasis") else "button button-secondary"
    attrs = []
    target = cta.get("target")
    rel = cta.get("rel")
    if target:
        attrs.append(f'target="{escape(target)}"')
        if target == "_blank" and not rel:
            attrs.append('rel="noopener noreferrer"')
    if rel:
        attrs.append(f'rel="{escape(rel)}"')
    attr_text = f" {' '.join(attrs)}" if attrs else ""
    icon = ""
    if cta.get("icon") == "computer":
        icon = """
        <svg class="button-icon" aria-hidden="true" viewBox="0 0 24 24" focusable="false">
          <rect x="4" y="5" width="16" height="11" rx="2"></rect>
          <path d="M8 19h8M10 16l-1 3M14 16l1 3"></path>
        </svg>"""
    return f'<a class="{classes}" href="{escape(cta["href"])}"{attr_text}>{icon}{escape(cta["label"])}</a>'


def resolve_asset_path(value: str) -> str:
    if value.startswith(("http://", "https://", "//")):
        return value
    if value.startswith("/static/images/"):
        return "./images/" + value.rsplit("/", 1)[-1]
    return "." + value if value.startswith("/") else value


def initials(name: str) -> str:
    parts = [part for part in name.split() if part]
    return "".join(part[0].upper() for part in parts[:2])


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def render_facts() -> str:
    items = []
    for fact in site["facts"]:
        items.append(
            f"""
        <article class="panel fact">
          <div class="fact-label">{escape(fact['label'])}</div>
          <div class="fact-value">{escape(fact['value'])}</div>
        </article>"""
        )
    return "".join(items)


def render_about() -> str:
    intro = about.get("intro")
    cards = []
    for card in about["cards"]:
        logo = ""
        if card.get("logo"):
            logo_img = f'<img src="{escape(resolve_asset_path(card["logo"]))}" alt="{escape(card.get("logo_alt", card["title"]))}" loading="lazy">'
            if card.get("href"):
                logo_img = f'<a class="about-card-logo-link" href="{escape(card["href"])}" target="_blank" rel="noopener noreferrer">{logo_img}</a>'
            logo = f"""
        <div class="about-card-brand">
          {logo_img}
        </div>"""
        cards.append(
            f"""
      <article class="card about-card">
        {logo}
        <h3 class="card-title">{escape(card['title'])}</h3>
        <p class="muted">{escape(card['body'])}</p>
      </article>"""
        )
    return f"""
  <section class="section" id="about">
    <div class="section-header">
      <div>
        <h2 class="section-title">{escape(about['title'])}</h2>
      </div>
    </div>
    <div class="content-grid">
      <article class="card about-intro">
        <p>{escape(intro)}</p>
      </article>
      {''.join(cards)}
    </div>
  </section>"""


def render_keynotes() -> str:
    cards = "".join(
        f"""
      <article class="card keynote-card">
        <div class="keynote-media">
          <img src="{escape(resolve_asset_path(item.get('image', '/static/images/portrait-placeholder.svg')))}" alt="{escape(item.get('image_alt', item['name']))}" loading="lazy">
        </div>
        <div class="keynote-body">
          <div class="keynote-meta">
            <span>{escape(item['day'])}</span>
            <span>{escape(item['date'])}</span>
          </div>
          <h3 class="card-title">{escape(item['name'])}</h3>
          <div class="keynote-affiliation">{escape(item['affiliation'])}</div>
          <p class="muted">{escape(item['bio'])}</p>
          <div class="keynote-location">{escape(item['location'])}</div>
        </div>
      </article>"""
        for item in keynotes
    )

    return f"""
  <section class="section" id="keynotes">
    <div class="section-header">
      <div>
        <h2 class="section-title">Keynotes</h2>
      </div>
    </div>
    <div class="keynote-grid">
      {cards}
    </div>
  </section>"""


def render_program() -> str:
    convention_by_slug = {
        item["slug"]: item
        for item in program.get("conventions", [])
        if item.get("slug")
    }

    filter_buttons = [
        """
        <button class="program-filter is-active" type="button" data-program-filter="all" aria-pressed="true">
          All
        </button>"""
    ]
    for item in program.get("conventions", []):
        slug = item.get("slug") or slugify(item["label"])
        filter_buttons.append(
            f"""
        <button class="program-filter" type="button" data-program-filter="{escape(slug)}" aria-pressed="false">
          <span aria-hidden="true">{escape(item['emoji'])}</span>
          <span>{escape(item['label'])}</span>
        </button>"""
        )

    days = []
    for item in program["days"]:
        blocks = "".join(
            f"""
            <li class="program-block" data-program-block data-program-category="{escape(block['category'])}">
              <div class="program-time">{escape(block['start'])}–{escape(block['end'])}</div>
              <div class="program-block-copy">
                <div class="program-block-title">
                  <span class="program-block-emoji" aria-hidden="true">{escape(convention_by_slug.get(block['category'], {}).get('emoji', '•'))}</span>
                  <strong>{escape(block['title'])}</strong>
                </div>
                <span>{escape(block['location'])}</span>
              </div>
            </li>"""
            for block in item["blocks"]
        )
        days.append(
            f"""
      <article class="card program-day" data-program-day>
        <div class="program-day-head">
          <div>
            <div class="schedule-day-label">{escape(item['day'])}</div>
            <h3 class="card-title">{escape(item['date'])}</h3>
          </div>
          <div class="program-day-range">07:00-22:00</div>
        </div>
        <ul class="program-list">
          {blocks}
        </ul>
      </article>"""
        )
    return f"""
  <section class="section" id="program">
    <div class="section-header">
      <div>
        <h2 class="section-title">{escape(program['title'])}</h2>
      </div>
    </div>
    <div class="program-toolbar" data-program-toolbar>
      <div class="program-conventions-title">Filter by convention</div>
      <div class="program-filters">
        {''.join(filter_buttons)}
      </div>
    </div>
    <div class="program-scroll">
      <div class="program-strip">
      {''.join(days)}
      </div>
    </div>
    <div class="program-note" role="note">{escape(program.get('disclaimer', 'Program timings are subject to change.'))}</div>
  </section>"""


def render_announcements() -> str:
    sorted_announcements = sorted(
        announcements,
        key=lambda item: item["date"],
        reverse=True,
    )
    if sorted_announcements:
        cards = []
        for item in sorted_announcements:
            cards.append(
                f"""
                  <article class="card announcement">
                    <div class="announcement-date">
                      <span>{escape(item['tag'])}</span>
                      {escape(format_date(item['date']))}
                    </div>
                    <div>
                      <h3>{escape(item['title'])}</h3>
                      <p>{escape(item['summary'])}</p>
                    </div>
                  </article>"""
            )
        body = f'<div class="announcement-list">{"".join(cards)}</div>'
    else:
        body = '<div class="empty-state">No announcements yet.</div>'

    return f"""
  <section class="section" id="announcements">
    <div class="section-header">
      <div>
        <h2 class="section-title">Announcements</h2>
      </div>
    </div>
    {body}
  </section>"""


def render_person_card(person: dict) -> str:
    photo = person.get("photo")
    role_title = person.get("role_title") or person.get("role") or ""
    if photo:
        media = f'<img src="{escape(resolve_asset_path(photo))}" alt="{escape(person["name"])} portrait">'
    else:
        media = f'<div class="person-fallback" aria-hidden="true">{escape(initials(person["name"] or role_title))}</div>'

    institution = person.get("institution")
    if institution:
        role = f"""
        <div class="role">
          <span class="role-title">{escape(role_title)}</span>
          <span class="role-org">{escape(institution)}</span>
        </div>"""
    else:
        role = f"""
        <div class="role">
          <span class="role-title">{escape(role_title)}</span>
        </div>"""

    return f"""
    <article class="card person">
      <div class="person-media">{media}</div>
      <div class="person-body">
        {role}
        <h3>{escape(person['name'])}</h3>
        <p>{escape(person['bio'])}</p>
      </div>
    </article>"""


def render_people_group(title: str, items: list[dict]) -> str:
    section_id = title.lower().replace(" ", "-")
    if items:
        cards = "".join(render_person_card(person) for person in items)
        body = f"""
    <div class="people-scroll" aria-label="{escape(title)} carousel">
      <div class="people-strip">{cards}</div>
    </div>"""
    else:
        body = f'<div class="empty-state">No {escape(title.lower())} have been added yet.</div>'

    return f"""
  <section class="section" id="{section_id}">
    <div class="section-header">
      <div>
        <h2 class="section-title">{escape(title)}</h2>
      </div>
    </div>
    {body}
  </section>"""


def page_shell(title: str, body: str) -> str:
    nav_items = "".join(
        f'<li><a href="{escape(item["href"])}">{escape(item["label"])}</a></li>'
        for item in site["nav"]
    )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{escape(site['description'])}">
    <meta name="theme-color" content="#f6f1e8">
    <link rel="icon" href="./favicon.svg">
    <title>{escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="./assets/site.css?v={ASSET_VERSION}">
    <script defer src="./assets/site.js?v={ASSET_VERSION}"></script>
  </head>
    <body>
    <a class="skip-link" href="#content">Skip to content</a>
    <header class="site-header">
      <div class="container header-inner">
        <a class="brand" href="#top" aria-label="{escape(site['title'])}">
          <span class="brand-logos" aria-hidden="true">
            <img src="{escape(resolve_asset_path('/static/images/mbzuai-brand-logo.svg'))}" alt="">
            <img src="{escape(resolve_asset_path('/static/images/ala-logo-horizontal.png'))}" alt="">
          </span>
          <span class="brand-text">
            <span class="brand-title">{escape(site['title'])}</span>
          </span>
        </a>
        <nav class="nav" data-nav data-open="false" aria-label="Primary">
          <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="primary-nav">
            <span class="nav-toggle-lines" aria-hidden="true"><span></span><span></span><span></span></span>
            Menu
          </button>
          <ul class="nav-list" id="primary-nav">
            {nav_items}
          </ul>
        </nav>
      </div>
    </header>
    <main id="content">
      {body}
    </main>
    <footer class="site-footer">
      <div class="container">
        <div class="panel footer-card">
          <a class="button button-secondary" href="#top">Back to top</a>
        </div>
      </div>
    </footer>
  </body>
</html>"""


def render_home() -> str:
    hero_ctas = "".join(render_button(cta) for cta in site["hero"]["ctas"])
    hero_image = site["hero"].get("image")
    hero_image_alt = site["hero"].get("image_alt", site["hero"]["title"])
    hero_art = ""
    if hero_image:
        hero_art = f"""
          <figure class="hero-art">
            <img src="{escape(resolve_asset_path(hero_image))}" alt="{escape(hero_image_alt)}" loading="eager" fetchpriority="high">
          </figure>"""
    body = f"""
    <div id="top"></div>
    <section class="hero">
      <div class="container hero-grid">
        <article class="panel hero-copy">
          <div class="hero-copy-main">
            <div class="eyebrow">{escape(site['hero']['eyebrow'])}</div>
            <h1>{escape(site['hero']['title'])}</h1>
            <p class="hero-summary">{escape(site['hero']['summary'])}</p>
            <div class="hero-actions">
              {hero_ctas}
            </div>
          </div>
          {hero_art}
        </article>
      </div>
    </section>
    <section class="facts">
      <div class="container">
        <div class="facts-grid">
          {render_facts()}
        </div>
      </div>
    </section>
    <div class="container">
      {render_about()}
      {render_keynotes()}
      {render_program()}
      {render_announcements()}
      {render_people_group(
          "Organizers",
          organizers,
      )}
    </div>"""
    return page_shell(site["title"], body)


def render_404() -> str:
    body = """
    <section class="hero">
      <div class="container">
        <article class="panel hero-copy" style="max-width: 52rem;">
          <div class="eyebrow">404</div>
          <h1>Page not found</h1>
          <p class="hero-summary">The requested page does not exist. Return to the homepage for the bootcamp overview, program, and updates.</p>
          <div class="hero-actions">
            <a class="button button-primary" href="./index.html">Go home</a>
            <a class="button button-secondary" href="./index.html#announcements">Read announcements</a>
          </div>
        </article>
      </div>
    </section>"""
    return page_shell(f"{site['title']} | 404", body)


def copy_static_assets() -> None:
    shutil.copy2(SRC_DIR / "site.css", OUT_DIR / "assets" / "site.css")
    shutil.copy2(SRC_DIR / "site.js", OUT_DIR / "assets" / "site.js")
    shutil.copy2(STATIC_DIR / "favicon.svg", OUT_DIR / "favicon.svg")
    for image in (STATIC_DIR / "images").iterdir():
        if image.is_file():
            shutil.copy2(image, OUT_DIR / "images" / image.name)


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    (OUT_DIR / "assets").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "images").mkdir(parents=True, exist_ok=True)

    copy_static_assets()
    (OUT_DIR / "index.html").write_text(render_home(), encoding="utf-8")
    (OUT_DIR / "404.html").write_text(render_404(), encoding="utf-8")
    (OUT_DIR / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{site['url']}</loc>
  </url>
</urlset>
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
