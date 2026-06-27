from __future__ import annotations

import json
import html
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "site"
SRC_DIR = ROOT / "src"
STATIC_DIR = ROOT / "static"
CONTENT_DIR = ROOT / "content"


def load_json(filename: str):
    with (CONTENT_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


site = load_json("site.json")
about = load_json("about.json")
program = load_json("program.json")
announcements = load_json("announcements.json")
people = load_json("people.json")


def format_date(value: str) -> str:
    day = date.fromisoformat(value)
    return f"{day.day} {day.strftime('%b %Y')}"


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def resolve_asset_path(value: str) -> str:
    if value.startswith(("http://", "https://", "//")):
        return value
    return "." + value if value.startswith("/") else value


def initials(name: str) -> str:
    parts = [part for part in name.split() if part]
    return "".join(part[0].upper() for part in parts[:2])


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
    points = "".join(f"<li>{escape(point)}</li>" for point in about["points"])
    return f"""
  <section class="section" id="about">
    <div class="section-header">
      <div>
        <h2 class="section-title">{escape(about['title'])}</h2>
      </div>
      <p class="section-summary">{escape(about['intro'])}</p>
    </div>
    <div class="content-grid">
      <article class="card">
        <h3 class="card-title">What the bootcamp emphasizes</h3>
        <ul class="list">
          {points}
        </ul>
      </article>
      <article class="card">
        <h3 class="card-title">Maintenance model</h3>
        <p class="muted">{escape(about['note'])}</p>
      </article>
    </div>
  </section>"""


def render_program() -> str:
    items = []
    for index, phase in enumerate(program["phases"], start=1):
        items.append(
            f"""
            <article class="timeline-item">
              <div class="timeline-step">{index:02d}</div>
              <div>
                <h3 class="card-title">{escape(phase['title'])}</h3>
                <p>{escape(phase['summary'])}</p>
              </div>
            </article>"""
        )
    return f"""
  <section class="section" id="program">
    <div class="section-header">
      <div>
        <h2 class="section-title">{escape(program['title'])}</h2>
      </div>
      <p class="section-summary">{escape(program['intro'])}</p>
    </div>
    <div class="timeline panel">
      {''.join(items)}
    </div>
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
      <p class="section-summary">Recent updates are shown in reverse chronological order so the latest note is always first.</p>
    </div>
    {body}
  </section>"""


def render_person_card(person: dict) -> str:
    photo = person.get("photo")
    if photo:
        media = f'<img src="{escape(resolve_asset_path(photo))}" alt="{escape(person["name"])} portrait">'
    else:
        media = f'<div class="person-fallback" aria-hidden="true">{escape(initials(person["name"] or person["role"]))}</div>'

    return f"""
    <article class="card person">
      <div class="person-media">{media}</div>
      <div class="person-body">
        <div class="role">{escape(person['role'])}</div>
        <h3>{escape(person['name'])}</h3>
        <p>{escape(person['bio'])}</p>
      </div>
    </article>"""


def render_people_group(title: str, items: list[dict], summary: str) -> str:
    section_id = title.lower().replace(" ", "-")
    if items:
        cards = "".join(render_person_card(person) for person in items)
        body = f'<div class="people-grid">{cards}</div>'
    else:
        body = f'<div class="empty-state">No {escape(title.lower())} have been added yet.</div>'

    return f"""
  <section class="section" id="{section_id}">
    <div class="section-header">
      <div>
        <h2 class="section-title">{escape(title)}</h2>
      </div>
      <p class="section-summary">{escape(summary)}</p>
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
    <link rel="stylesheet" href="./assets/site.css">
    <script defer src="./assets/site.js"></script>
  </head>
  <body>
    <a class="skip-link" href="#content">Skip to content</a>
    <header class="site-header">
      <div class="container header-inner">
        <a class="brand" href="#top" aria-label="{escape(site['title'])}">
          <span class="brand-mark">AI</span>
          <span class="brand-text">
            <span class="brand-eyebrow">ALA x MBZUAI</span>
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
          <p>{escape(site['footer'])}</p>
          <a href="#top">Back to top</a>
        </div>
      </div>
    </footer>
  </body>
</html>"""


def render_home() -> str:
    hero_ctas = "".join(
        f'<a class="button {"button-primary" if cta.get("emphasis") else "button-secondary"}" href="{escape(cta["href"])}">{escape(cta["label"])}</a>'
        for cta in site["hero"]["ctas"]
    )
    hero_meta = "".join(
        f"""
                <div class="hero-meta-card">
                  <strong>{escape(fact['value'])}</strong>
                  <p>{escape(fact['label'])}</p>
                </div>"""
        for fact in site["facts"][:2]
    )
    body = f"""
    <div id="top"></div>
    <section class="hero">
      <div class="container hero-grid">
        <article class="panel hero-copy">
          <div class="eyebrow">{escape(site['hero']['eyebrow'])}</div>
          <h1>{escape(site['hero']['title'])}</h1>
          <p class="hero-summary">{escape(site['hero']['summary'])}</p>
          <div class="hero-actions">
            {hero_ctas}
          </div>
        </article>
        <aside class="panel hero-meta" aria-label="Quick facts">
          {hero_meta}
          <div class="hero-meta-card">
            <strong>Program story</strong>
            <p>Responsible AI, leadership, and project work in a residential format.</p>
          </div>
        </aside>
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
      {render_program()}
      {render_announcements()}
      {render_people_group(
          "Organizers",
          people["organizers"],
          "Organizing roles are shown as structured cards so new names or photos can be added without changing the page layout.",
      )}
      {render_people_group(
          "Keynote speakers",
          people["keynotes"],
          "Keynote slots stay visible even before final speaker details are confirmed.",
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
    shutil.copy2(
        STATIC_DIR / "images" / "portrait-placeholder.svg",
        OUT_DIR / "images" / "portrait-placeholder.svg",
    )


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
