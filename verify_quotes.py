"""Check every footnote quote in an answer against the raw text of its source page.

Footnote format, one per line:
    [^1]: https://example.com/page "sentence copied verbatim from the page"
Quotes may use "..." / “...” / 「...」. Join omitted parts with … (parts must appear in order).

Usage:
    python -X utf8 verify_quotes.py answer.md
    python -X utf8 verify_quotes.py --text URL    # print a page's raw text (copy quotes from here)
    python -X utf8 verify_quotes.py --selftest
Exit code 0 when every quote is found and every body link is footnoted, 1 otherwise.

Optional extras, used only when needed:
    pip install pdfminer.six                           # PDF sources
    pip install playwright && playwright install chromium   # pages rendered by JavaScript
"""
import gzip
import html
import io
import re
import ssl
import sys
import unicodedata
import urllib.error
import urllib.request

# A bare URL or [name](URL); models vary in how they write it.
FOOTNOTE = re.compile(r'^\[\^([^\]]+)\]:\s*(?:\[[^\]]*\]\()?(https?://[^\s)]+)\)?\s*[「"“](.+)[」"”]\s*$')
# Heading that opens the unverified section, in the languages users most often answer in.
UNVERIFIED = re.compile(r'unverified|未確認|未验证|未驗證|미확인|non vérifié|no verificado|nicht verifiziert', re.I)
USER_AGENT = 'verified-research/1.0 (+https://github.com/MetamoL/skills)'
MIN_TEXT = 200  # shorter than this, the page body did not come through


class Unfetchable(Exception):
    pass


def norm(text):
    # Ignore width, case and whitespace (CJK text has no spaces between words, so drop them all).
    text = unicodedata.normalize('NFKC', text).lower()
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'[\s|`]+', '', text)  # | and ` too: models quote markdown tables and code spans


def page_text(raw):
    raw = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', raw)
    return html.unescape(re.sub(r'<[^>]+>', ' ', raw))


def contains(page, quote):
    pos = 0
    for part in re.split(r'…|\.\.\.', quote):
        # A quoted sentence may end where the page's heading or clause has no full stop.
        part = norm(part).strip('.,;:!?。、．，')
        if not part:
            continue
        pos = page.find(part, pos)
        if pos < 0:
            return False
        pos += len(part)
    return True


def pdf_text(data):
    try:  # pdfminer.six over pypdf: pypdf garbles CJK fonts without a ToUnicode map
        from pdfminer.high_level import extract_text
    except ImportError:
        raise Unfetchable('PDF: run `pip install pdfminer.six`')
    return extract_text(io.BytesIO(data))


def decode_html(data, charset):
    # Servers often omit the charset (Shift_JIS pages in particular); fall back to the page's own <meta>.
    if not charset:
        m = re.search(rb'charset=["\']?([\w-]+)', data[:4096], re.I)
        charset = m.group(1).decode() if m else 'utf-8'
    try:
        return data.decode(charset, errors='replace')
    except LookupError:
        return data.decode('utf-8', errors='replace')


def rendered_text(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise Unfetchable('page needs JavaScript: run `pip install playwright && playwright install chromium`')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state('networkidle', timeout=15000)
            return page.inner_text('body')
        finally:
            browser.close()


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    ctx = ssl.create_default_context()
    ctx.options |= getattr(ssl, 'OP_LEGACY_SERVER_CONNECT', 0x4)  # older government servers need it
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as res:
            ctype = res.headers.get('Content-Type', '')
            data = res.read()
            if res.headers.get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
            charset = res.headers.get_content_charset()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429, 451):
            # The site refuses automated readers; respect that and find another copy.
            raise Unfetchable(f'HTTP {e.code}, site refuses automated access: cite an official API (e.g. Europe PMC for PubMed), DOI/abstract page, or archive copy instead')
        raise Unfetchable(f'HTTP {e.code}')
    if 'pdf' in ctype or data[:5] == b'%PDF-':
        return pdf_text(data)
    text = page_text(decode_html(data, charset))
    if len(norm(text)) < MIN_TEXT:
        text = rendered_text(url)
    return text


def unchecked_links(raw, footnote_urls):
    # A link in the body (above the unverified section) that no footnote checks is a bypass.
    found = []
    for line in raw:
        if UNVERIFIED.search(line):
            break
        if line.startswith('[^'):
            continue
        for url in re.findall(r'https?://[^\s)\]」>]+', line):
            if url not in footnote_urls:
                print(f'UNCHECKED LINK in body (move it to a footnote with a quote): {url}')
                found.append(url)
    return found


def check(path):
    cache = {}
    with open(path, encoding='utf-8') as f:
        raw = f.read().splitlines()
    lines = [m.groups() for m in map(FOOTNOTE.match, raw) if m]
    if not lines:
        print('No footnotes found (format: [^1]: URL "quote")')
        return 1
    loose = len(unchecked_links(raw, {url for _, url, _ in lines}))
    bad = 0
    for label, url, quote in lines:
        try:
            if url not in cache:
                cache[url] = norm(fetch(url))
            text = cache[url]
            if len(text) < MIN_TEXT:
                raise Unfetchable('no page text')
        except Exception as e:  # unfetchable is reported apart from "quote not on page"
            print(f'[^{label}] UNFETCHABLE ({e}) {url}')
            bad += 1
            continue
        if contains(text, quote):
            print(f'[^{label}] OK')
        else:
            print(f'[^{label}] NOT ON PAGE {url}\n    "{quote}"')
            bad += 1
    print(f'{len(lines) - bad}/{len(lines)} quotes verified')
    return 1 if bad or loose else 0


def selftest():
    page = norm(page_text('<p>東京都最低賃金は<b>10月1日</b>から\n時間額1,280円</p><script>x</script>'))
    assert contains(page, '時間額１，２８０円')
    assert contains(page, '東京都最低賃金は…1,280円')
    assert not contains(page, '1,280円…東京都')
    assert not contains(page, 'x')
    assert contains(norm('The API is  Closed to new customers.'), 'the api is closed…customers')
    assert contains(norm('Python is officially supported Binary releases'), 'Python is officially supported.')
    assert contains(norm('26.x Active LTS Lithium'), '26.x | Active LTS | Lithium')
    assert not contains(norm('price 1,280 yen'), '1,290')
    assert contains(norm('io_method=io_uring is available'), '`io_method=io_uring` is available')
    sjis = '<meta charset="Shift_JIS"><p>軽減税率</p>'.encode('cp932')
    assert '軽減税率' in decode_html(sjis, None)
    assert FOOTNOTE.match('[^1]: https://a.example/b 「引用」').groups() == ('1', 'https://a.example/b', '引用')
    assert FOOTNOTE.match('[^2]: [name](https://a.example/b) "quote"').groups() == ('2', 'https://a.example/b', 'quote')
    for heading in ('**Unverified**', '**未確認**'):
        body = ['Answer [doc](https://a.example/b)', 'see https://c.example/d', heading, 'https://e.example/f']
        assert unchecked_links(body, {'https://a.example/b'}) == ['https://c.example/d']
    print('selftest ok')
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1:] == ['--selftest']:
        sys.exit(selftest())
    if len(sys.argv) == 3 and sys.argv[1] == '--text':
        try:
            text = re.sub(r'\s+', ' ', fetch(sys.argv[2])).strip()
        except Exception as e:
            sys.exit(f'UNFETCHABLE ({e})')
        print(text)
        sys.exit(0)
    if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help'):
        sys.exit(__doc__)
    sys.exit(check(sys.argv[1]))
