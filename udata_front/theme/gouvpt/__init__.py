import logging
import re

import feedparser
import requests

from dateutil.parser import parse
from flask import g, current_app, url_for

from udata_front import theme
from udata.app import cache
from udata.models import Dataset
from udata_front.frontend import nav
from udata.i18n import lazy_gettext as _


log = logging.getLogger(__name__)

RE_POST_IMG = re.compile(
    r'''
    <img .*? (?:(?:
        src="(?P<src>https?://.+?)"
        |
        srcset="(?P<srcset>.+?)"
        |
        sizes="(?P<sizes>.+?)"
    )\s*)+ .*?/>
    ''',
    re.I | re.X | re.S
)

RE_STRIP_TAGS = re.compile(r'</?(img|br|p|div|ul|li|ol)[^<>]*?>', re.I | re.M)

# Add some html5 allowed attributes
EXTRA_ATTRIBUTES = ('srcset', 'sizes')
feedparser.sanitizer._HTMLSanitizer.acceptable_attributes.update(set(EXTRA_ATTRIBUTES))

# Wordpress ATOM timeout
WP_TIMEOUT = 5

# Feed allowed enclosure type as thumbnails
FEED_THUMBNAIL_MIMES = ('image/jpeg', 'image/png', 'image/webp')


gouvpt_menu = nav.Bar('gouvpt_menu', [
    nav.Item(_('Data'), 'datasets.list'),
    nav.Item(_('Reuses'), 'reuses.list'),
    nav.Item(_('Organizations'), 'organizations.list'),
    nav.Item(_('Getting started on dados.gov.pt'), None, items=[
        nav.Item(
            _('Sobre dados abertos'), 
            'gouvpt_faq.faq', 
            {'section': 'about_opendata'}
        ),
        nav.Item(
            _('Sobre o dados.gov'), 
            'gouvpt_faq.faq', 
            {'section': 'about_dadosgov'}
        ),
        nav.Item(
            _('Publicar dados'), 
            'gouvpt_faq.faq', 
            {'section': 'publish'}
        ),
        nav.Item(
            _('Reutilizar dados'), 
            'gouvpt_faq.faq', 
            {'section': 'reuse'}
        ),
    ]),
    nav.Item(_('Documentação'), None, items=[
        nav.Item(_('Licences'), 'gouvpt_faq.faq', {'section': 'licenses'}),
        nav.Item(_('Terms of use'), 'site.terms'),
        nav.Item(_('Acessibilidade'), 'gouvpt_faq.faq', {'section': 'acessibilidade'}),
        nav.Item(_('API'), 'gouvpt_faq.docapi'),
    ]),
    nav.Item(_('News'), 'posts.list'),
    nav.Item(_('Contact us'), 'gouvpt_faq.contact'),
])

theme.menu(gouvpt_menu)

opendata_links = [
    #nav.Item(_('Featured topics'), 'gouvpt.show_page', args={'slug': 'thematiques-a-la-une'}),
    #nav.Item(_('Reference Data'), 'gouvpt.show_page', args={'slug': 'spd/reference'}),
    nav.Item(_('Portal for European data'), None, url='https://data.europa.eu'),
    nav.Item(_('Data'), 'datasets.list'),
    nav.Item(_('Reuses'), 'reuses.list'),
    nav.Item(_('Organizations'), 'organizations.list'),
]

export_dataset_id = current_app.config.get('EXPORT_CSV_DATASET_ID')
if export_dataset_id:
    try:
        export_dataset = Dataset.objects.get(id=export_dataset_id)
    except Dataset.DoesNotExist:
        pass
    else:
        export_url = url_for('datasets.show', dataset=export_dataset,
                             _external=True)
        opendata_links.append(nav.Item(_('Data catalog'), None, url=export_url))
#opendata_links.append(nav.Item(_('Release notes'), 'gouvpt.show_page', args={'slug': 'nouveautes'}))

nav.Bar('gouvpt_opendata', opendata_links)


support_links = [
    nav.Item(_("Platform's documentation"), 'gouvpt_faq.faq', {'section': 'about_opendata'}),
    #nav.Item(_("Portal's API"), None, url=current_app.config.get('API_DOC_EXTERNAL_LINK', '#')),
    nav.Item(_("Portal's API"), 'gouvpt_faq.docapi'),
    #nav.Item(_('Open data guides'), None, url=current_app.config.get('ETALAB_GUIDES_URL', '#')),
    nav.Item(_('Contact us'), 'gouvpt_faq.contact'),
]

nav.Bar('gouvpt_support', support_links)

footer_links = [
    nav.Item(_('Licences'), 'gouvpt_faq.faq', {'section': 'licenses'}),
    nav.Item(_('Terms of use'), 'site.terms'),
    #nav.Item(_('Tracking and privacy'), 'gouvpt.suivi'),
    #nav.Item(_('Accessibility: partially compliant'),
    #         'gouvpt.show_page', args={'slug': 'legal/accessibility'}),
    nav.Item(_('Acessibilidade'), 'gouvpt_faq.faq', {'section': 'acessibilidade'}),
]

nav.Bar('gouvpt_footer', footer_links)

NETWORK_LINKS = [
    ('República Portuguesa', 'https://www.portugal.gov.pt/pt/gc23'),
    #('Agência para a Modernização Administrativa', 'https://www.ama.gov.pt/'),
    ('Compete 2020', 'https://www.compete2020.gov.pt/'),
    ('Portugal 2020', 'https://portugal2020.pt/'),
    ('Comissão Europeia', 'https://ec.europa.eu/info/funding-tenders/find-funding/funding-management-mode/2014-2020-european-structural-and-investment-funds_pt'),
    #('Selo de Usabilidade', 'https://selo.usabilidade.gov.pt'),
]

nav.Bar(
    'gouvpt_network',
    [nav.Item(label, label, url=url) for label, url in NETWORK_LINKS]
)


@cache.memoize(50)
def get_blog_post(lang):
    '''
    Extract the latest post summary from an RSS or an Atom feed.

    Image is searched and extracted from (in order of priority):
      - mediarss `media:thumbnail` attribute
      - enclosures of image type (first match)
      - first image found in content
    Image size is ot taken in account but could in future improvements.
    '''
    wp_atom_url = current_app.config.get('WP_ATOM_URL')
    if not wp_atom_url:
        return

    feed = None

    for code in lang, current_app.config['DEFAULT_LANGUAGE']:
        feed_url = wp_atom_url.format(lang=code)
        try:
            response = requests.get(feed_url, timeout=WP_TIMEOUT)
        except requests.Timeout:
            log.error('Timeout while fetching %s', feed_url, exc_info=True)
            continue
        except requests.RequestException:
            log.error('Error while fetching %s', feed_url, exc_info=True)
            continue
        feed = feedparser.parse(response.content)

        if len(feed.entries) > 0:
            break

    if not feed or len(feed.entries) <= 0:
        return

    post = feed.entries[0]

    blogpost = {
        'title': post.title,
        'link': post.link,
        'date': parse(post.published)
    }
    description = post.get('description', None)
    content = post.get('content', [{}])[0].get('value') or description
    summary = post.get('summary', content)
    blogpost['summary'] = RE_STRIP_TAGS.sub('', summary).strip()

    for thumbnail in post.get('media_thumbnail', []):
        blogpost['image_url'] = thumbnail['url']
        break

    if 'image_url' not in blogpost:
        for enclosure in post.get('enclosures', []):
            if enclosure.get('type') in FEED_THUMBNAIL_MIMES:
                blogpost['image_url'] = enclosure['href']
                break

    if 'image_url' not in blogpost:
        match = RE_POST_IMG.search(content)
        if match:
            blogpost['image_url'] = match.group('src').replace('&amp;', '&')
            if match.group('srcset'):
                blogpost['srcset'] = match.group('srcset').replace('&amp;', '&')
            if match.group('sizes'):
                blogpost['sizes'] = match.group('sizes')

    return blogpost


@theme.context('home')
def home_context(context):
    context['blogpost'] = get_blog_post(g.lang_code)
    return context
