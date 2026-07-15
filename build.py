#!/usr/bin/env python3
import html
import json
import shutil
from pathlib import Path

SOURCE = Path('/home/chris/pitch-pipeline/01_scraped/spa-creek-marina.json')
ASSETS_SOURCE = Path('/home/chris/pitch-pipeline/01_scraped/spa-creek-marina-assets')
ROOT = Path(__file__).parent
PUBLIC = ROOT / 'public'
SITE = 'https://spa-creek-marina-preview.pages.dev'

data = json.loads(SOURCE.read_text())

pages = [
    ('index.html', 'Home'),
    ('additional-slips.html', 'Additional Slips'),
    ('pelicans-roost-rental.html', "Pelican's Roost Rental"),
    ('knot10-yacht-sales.html', 'Knot10 Yacht Sales'),
    ('contact.html', 'Contact'),
    ('privacy-policy.html', 'Privacy Policy'),
]

nav = [
    ('Home', 'index.html'),
    ('About', 'index.html'),
    ('Additional Slips', 'additional-slips.html'),
    ("Pelican's Roost Rental", 'pelicans-roost-rental.html'),
    ('Client Love', 'index.html'),
    ('Knot10 Yacht Sales', 'knot10-yacht-sales.html'),
    ('Contact', 'contact.html'),
    ('Privacy Policy', 'privacy-policy.html'),
]

alts = {
    'boats-2.jpg': 'Boats moored at docks along a tree-lined creek',
    'boats-3.jpg': 'Sailboats and powerboats moored beside wooden docks',
    'boats-6.jpg': 'Waterfront marina building, dock, and moored boats',
}

def esc(value):
    return html.escape(str(value), quote=True)

def jsonld():
    payload = {
        '@context': 'https://schema.org',
        '@type': 'Marina',
        'name': data['business_name'],
        'telephone': data['phone'],
        'email': data['contact_email'],
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': '140 Spa Dr',
            'addressLocality': 'Annapolis',
            'addressRegion': 'MD',
            'postalCode': '21403',
            'addressCountry': 'US',
        },
        'geo': {
            '@type': 'GeoCoordinates',
            'latitude': data['geo']['lat'],
            'longitude': data['geo']['lng'],
        },
        'aggregateRating': {
            '@type': 'AggregateRating',
            'ratingValue': data['rating'],
        },
    }
    return json.dumps(payload, separators=(',', ':'))

def header(current):
    links = ''.join(
        f'<li><a href="{href}"' + (' aria-current="page"' if label == current else '') + f'>{esc(label)}</a></li>'
        for label, href in nav
    )
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="index.html" aria-label="{esc(data['business_name'])} home">
      <img src="assets/logo.png" alt="{esc(data['business_name'])} logo" width="64" height="64">
      <span>{esc(data['business_name'])}</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav">Menu</button>
    <nav id="primary-nav" class="primary-nav" aria-label="Primary navigation"><ul>{links}</ul></nav>
    <a class="header-call" href="tel:+14104568849">{esc(data['phone'])}</a>
  </div>
</header>'''

def footer():
    links = ''.join(f'<li><a href="{href}">{esc(label)}</a></li>' for label, href in nav)
    return f'''<section class="cta-strip" aria-labelledby="cta-title">
  <div class="section-inner cta-inner">
    <div><p class="eyebrow">40-foot to 50-foot boat slip rentals</p><h2 id="cta-title">Call {esc(data['phone'])} and speak to Paul about availability</h2></div>
    <a class="button button-light" href="tel:+14104568849">Call {esc(data['phone'])}</a>
  </div>
</section>
<footer class="site-footer">
  <div class="section-inner footer-grid">
    <div><img src="assets/logo.png" alt="{esc(data['business_name'])} logo" width="88" height="88"><p>{esc(data['business_name'])}</p></div>
    <div><h2>Contact</h2><address>{esc(data['address'])}<br><a href="tel:+14104568849">{esc(data['phone'])}</a><br><a href="mailto:{esc(data['contact_email'])}">{esc(data['contact_email'])}</a></address></div>
    <nav aria-label="Footer navigation"><h2>Navigation</h2><ul>{links}</ul></nav>
  </div>
</footer>'''

def shell(filename, label, description, body, og_image='assets/images/boats-2.jpg', extra_class=''):
    canonical = f'{SITE}/' if filename == 'index.html' else f'{SITE}/{filename}'
    title = f'{label} | {data["business_name"]}' if label != 'Home' else f'{data["business_name"]} | 14-Boat Slip Marina in Annapolis'
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" type="image/png" href="assets/favicon.png">
  <link rel="stylesheet" href="css/shared.css">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{SITE}/{og_image}">
  <script type="application/ld+json">{jsonld()}</script>
</head>
<body class="{extra_class}">
{header(label)}
<main id="main">{body}</main>
{footer()}
<script src="js/site.js" defer></script>
</body>
</html>'''

def list_items(items, cls='check-list'):
    return '<ul class="' + cls + '">' + ''.join(f'<li>{esc(x)}</li>' for x in items) + '</ul>'

def homepage():
    slide_parts = []
    for i, img in enumerate(data['images']):
        filename = Path(img['path']).name
        active = ' is-active' if i == 0 else ''
        priority = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
        slide_parts.append(f'<li class="slide{active}" data-slide="{i}"><img src="assets/images/{filename}" alt="{esc(alts[filename])}" width="1600" height="900"{priority}></li>')
    slides = ''.join(slide_parts)
    services = ''.join(f'<article class="service-card"><span aria-hidden="true">0{i}</span><h3>{esc(item)}</h3></article>' for i, item in enumerate(data['services'], 1))
    testimonials = ''.join(f'<figure class="quote-card"><blockquote>“{esc(t["text"])}”</blockquote><figcaption>— {esc(t["author"])}</figcaption></figure>' for t in data['testimonials'])
    attractions = ''.join(f'<li>{esc(x)}</li>' for x in data['nearby_attractions'])
    details = data['marina_details']
    body = f'''<section class="hero" aria-labelledby="hero-title">
  <div class="hero-slider" aria-label="Marina photographs"><ul>{slides}</ul><div class="slider-dots" aria-label="Choose hero image"><button class="is-active" aria-label="Show image 1"></button><button aria-label="Show image 2"></button><button aria-label="Show image 3"></button></div></div>
  <div class="hero-overlay"></div>
  <div class="section-inner hero-content">
    <p class="eyebrow">{esc(details[1])}</p>
    <h1 id="hero-title">{esc(details[0])}</h1>
    <p class="hero-copy">{esc(details[2])}</p>
    <div class="hero-actions"><a class="button" href="tel:+14104568849">Call about availability</a><a class="text-link" href="contact.html">{esc(data['contact_email'])}</a></div>
    <dl class="trust-row"><div><dt>Rating</dt><dd>{esc(data['rating'])}</dd></div><div><dt>Boat slips</dt><dd>14</dd></div><div><dt>Slip rentals</dt><dd>40-foot to 50-foot</dd></div></dl>
  </div>
</section>
<section class="section services" aria-labelledby="services-title"><div class="section-inner"><p class="eyebrow">Services</p><h2 id="services-title">Boat slip rentals</h2><div class="card-grid four">{services}</div></div></section>
<section id="about" class="section split-section" aria-labelledby="about-title"><div class="section-inner split-grid"><div><p class="eyebrow">About</p><h2 id="about-title">{esc(details[0])}</h2><p class="lead">{esc(details[1])}. {esc(details[2])}.</p><p><a class="button button-outline" href="tel:+14104568849">{esc(details[3])}</a></p></div><div class="panel"><h3>Amenities</h3>{list_items(data['amenities'])}</div></div></section>
<section class="section attractions" aria-labelledby="attractions-title"><div class="section-inner"><p class="eyebrow">Nearby attractions</p><h2 id="attractions-title">Annapolis</h2><ul class="pill-list">{attractions}</ul></div></section>
<section id="client-love" class="section testimonials" aria-labelledby="love-title"><div class="section-inner"><p class="eyebrow">Testimonials</p><h2 id="love-title">Client Love</h2><div class="card-grid three">{testimonials}</div></div></section>'''
    desc = f'{details[0]}, {details[1]}. {data["services"][0]}. Call {data["phone"]} and speak to Paul about availability.'
    return shell('index.html', 'Home', desc, body, extra_class='home')

def simple_hero(label, text):
    return f'<section class="page-hero"><div class="section-inner"><p class="eyebrow">{esc(data["business_name"])}</p><h1>{esc(label)}</h1><p class="lead">{esc(text)}</p></div></section>'

def additional():
    cards = ''.join(f'<article class="link-card"><h2>{esc(x["name"])}</h2><a class="text-link" href="{esc(x["url"])}" rel="noopener noreferrer">{esc(x["url"])}</a></article>' for x in data['additional_slip_resources'])
    body = simple_hero('Additional Slips', data['services'][0]) + f'<section class="section"><div class="section-inner card-grid three">{cards}</div></section>'
    desc = 'Additional Slips: ' + ', '.join(x['name'] for x in data['additional_slip_resources']) + '.'
    return shell('additional-slips.html', 'Additional Slips', desc, body)

def offering(index, filename, label):
    item = data['related_offerings'][index]
    body = simple_hero(label, item['description']) + f'<section class="section"><div class="section-inner narrow"><article class="detail-card"><h2>{esc(item["name"])}</h2><p>{esc(item["description"])}</p><a class="button" href="{esc(item["url"])}" rel="noopener noreferrer">{esc(item["url"])}</a></article></div></section>'
    return shell(filename, label, item['description'], body)

def contact():
    body = simple_hero('Contact', data['marina_details'][3]) + f'''<section class="section"><div class="section-inner contact-grid">
      <article class="detail-card"><h2>{esc(data['business_name'])}</h2><address>{esc(data['address'])}</address><p><a href="tel:+14104568849">{esc(data['phone'])}</a></p><p><a href="mailto:{esc(data['contact_email'])}">{esc(data['contact_email'])}</a></p></article>
      <form class="contact-form" action="mailto:{esc(data['contact_email'])}" method="post" enctype="text/plain"><h2>Slip Inquiry</h2><label>Name<input name="Name" autocomplete="name" required></label><label>Email<input type="email" name="Email" autocomplete="email" required></label><label>Message<textarea name="Message" rows="6" required></textarea></label><button class="button" type="submit">Email {esc(data['contact_email'])}</button></form>
    </div></section>'''
    desc = f'Contact {data["business_name"]} at {data["phone"]}, {data["contact_email"]}, or {data["address"]}.'
    return shell('contact.html', 'Contact', desc, body)

def privacy():
    body = simple_hero('Privacy Policy', data['business_name']) + f'<section class="section"><div class="section-inner narrow"><article class="detail-card"><h2>Contact</h2><p><a href="mailto:{esc(data["contact_email"])}">{esc(data["contact_email"])}</a></p><p><a href="tel:+14104568849">{esc(data["phone"])}</a></p></article></div></section>'
    desc = f'Privacy Policy | {data["business_name"]}'
    return shell('privacy-policy.html', 'Privacy Policy', desc, body)

def main():
    if PUBLIC.exists():
        for p in PUBLIC.glob('*.html'):
            p.unlink()
    (PUBLIC / 'css').mkdir(parents=True, exist_ok=True)
    (PUBLIC / 'js').mkdir(parents=True, exist_ok=True)
    (PUBLIC / 'assets' / 'images').mkdir(parents=True, exist_ok=True)
    shutil.copy2(ASSETS_SOURCE / 'logo.png', PUBLIC / 'assets' / 'logo.png')
    shutil.copy2(ASSETS_SOURCE / 'favicon.png', PUBLIC / 'assets' / 'favicon.png')
    for img in data['images']:
        shutil.copy2(img['path'], PUBLIC / 'assets' / 'images' / Path(img['path']).name)
    generated = {
        'index.html': homepage(),
        'additional-slips.html': additional(),
        'pelicans-roost-rental.html': offering(0, 'pelicans-roost-rental.html', "Pelican's Roost Rental"),
        'knot10-yacht-sales.html': offering(1, 'knot10-yacht-sales.html', 'Knot10 Yacht Sales'),
        'contact.html': contact(),
        'privacy-policy.html': privacy(),
    }
    for name, content in generated.items():
        (PUBLIC / name).write_text(content)
    (PUBLIC / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    urls = '\n'.join(f'  <url><loc>{SITE}/{"" if f == "index.html" else f}</loc></url>' for f, _ in pages)
    (PUBLIC / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')

if __name__ == '__main__':
    main()
