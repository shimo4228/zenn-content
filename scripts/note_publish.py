"""Prepare note assets and maintain a private, fail-closed publication ledger.

Run with: uv run --project scripts python scripts/note_publish.py --help
This tool never controls a browser or grants itself publication approval.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import frontmatter


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True).encode()


def normalize(text):
    return re.sub(r'\s+', '', text)


class Body(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.links = []
        self.headings = []
        self.images = []
        self.structure = []
        self.open_spans = []
        self.position = 0
        self.heading = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        semantic = {'b': 'strong', 'i': 'em'}.get(tag, tag)
        if semantic in ('strong', 'em', 'blockquote', 'a', 'ul', 'ol', 'li', 'pre', 'code', 'table', 'tr', 'td', 'th', 'del'):
            span = {'kind': semantic, 'start': self.position}
            if tag == 'a':
                span['href'] = attrs.get('href', '')
            if tag == 'ol':
                span['start_number'] = attrs.get('start', '1')
            self.structure.append(span)
            self.open_spans.append((semantic, span))
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag == 'img':
            self.images.append(attrs.get('src', ''))
        if re.fullmatch(r'h[1-6]', tag):
            self.heading = []

    def handle_endtag(self, tag):
        semantic = {'b': 'strong', 'i': 'em'}.get(tag, tag)
        for index in range(len(self.open_spans) - 1, -1, -1):
            kind, span = self.open_spans[index]
            if kind == semantic:
                span['end'] = self.position
                del self.open_spans[index]
                break
        if re.fullmatch(r'h[1-6]', tag) and self.heading is not None:
            self.headings.append(normalize(''.join(self.heading)))
            self.heading = None

    def handle_data(self, data):
        self.text.append(data)
        self.position += len(normalize(data))
        if self.heading is not None:
            self.heading.append(data)

    def summary(self):
        return {'body': normalize(''.join(self.text)), 'links': self.links,
                'headings': self.headings, 'images': self.images,
                'structure': self.structure}


def render(body):
    if re.search(r'^:::', body, re.M):
        raise ValueError('Zenn directives require manual format conversion')
    result = subprocess.run(['pandoc', '-f', 'gfm', '-t', 'json'], input=body,
                            text=True, capture_output=True, check=True)
    ast = json.loads(result.stdout)
    notes = []

    def cells(row):
        return [cell[4] for cell in row[1]]

    def inlines(blocks):
        return [inline for block in blocks if block['t'] in ('Plain', 'Para') for inline in block['c']]

    def table_to_list(table):
        # note's editor cannot render <table>: each body row becomes one bullet
        # "header: value / header: value" so every cell survives as text.
        _, _, _, head, bodies, _ = table
        headers = [inlines(cell) for row in head[1] for cell in cells(row)] if head[1] else []
        items = []
        for body in bodies:
            for row in body[2] + body[3]:
                parts = []
                for index, cell in enumerate(cells(row)):
                    if parts:
                        parts.append({'t': 'Str', 'c': ' / '})
                    if index < len(headers) and headers[index]:
                        parts += [{'t': 'Strong', 'c': headers[index]}, {'t': 'Str', 'c': ': '}]
                    parts += inlines(cell)
                items.append([{'t': 'Plain', 'c': parts}])
        return {'t': 'BulletList', 'c': items}

    def convert(value):
        if isinstance(value, list):
            return [convert(item) for item in value]
        if not isinstance(value, dict):
            return value
        if value.get('t') == 'Table':
            return convert(table_to_list(value['c']))
        if value.get('t') == 'Note':
            number = len(notes) + 1
            notes.append(value['c'])
            return {'t': 'Str', 'c': f'[{number}]'}
        return {key: convert(item) for key, item in value.items()}

    ast['blocks'] = convert(ast['blocks'])
    for number, blocks in enumerate(notes, 1):
        prefix = [{'t': 'Str', 'c': f'[{number}]'}, {'t': 'Space'}]
        if blocks and blocks[0]['t'] in ('Para', 'Plain'):
            blocks[0]['c'] = prefix + blocks[0]['c']
        else:
            blocks.insert(0, {'t': 'Para', 'c': prefix})
        ast['blocks'].extend(blocks)
    return subprocess.run(['pandoc', '-f', 'json', '-t', 'html', '--wrap=none'],
                          input=json.dumps(ast), text=True, capture_output=True,
                          check=True).stdout


def prepare(source, output, account, tags, image):
    source, output = Path(source).resolve(), Path(output).resolve()
    post = frontmatter.load(source)
    title, body = post.get('title'), post.content
    if not title and body.startswith('# '):
        title, _, body = body.partition('\n')
        title = title[2:].strip()
    if not isinstance(title, str) or not title.strip():
        raise ValueError('Nonempty title required')
    if not re.fullmatch(r'[a-zA-Z0-9_]+', account):
        raise ValueError('Invalid note account')
    html = render(body)
    output.mkdir(parents=True, exist_ok=True)
    assets = {'body.html': html, 'title.txt': title, 'article.md': f'# {title}\n\n{body}\n'}
    for name, text in assets.items():
        (output / name).write_text(text)
    files = {name: digest((output / name).read_bytes()) for name in assets}
    media = None
    if image:
        image = Path(image).resolve()
        media = {'path': str(image), 'sha256': digest(image.read_bytes())}
    manifest = {'version': 1, 'source': str(source), 'source_sha256': digest(source.read_bytes()),
                'title': title, 'account': account, 'tags': tags, 'media': media,
                'files': files, 'expected': Body(html).summary()}
    manifest['material_hash'] = digest(canonical(manifest))
    path = output / 'manifest.json'
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return path


def checked(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text())
    expected = data.pop('material_hash')
    if digest(canonical(data)) != expected:
        raise ValueError('Manifest changed; prepare and obtain approval again')
    data['material_hash'] = expected
    for name, hashed in data['files'].items():
        if digest((path.parent / name).read_bytes()) != hashed:
            raise ValueError(f'Asset changed: {name}')
    if digest(Path(data['source']).read_bytes()) != data['source_sha256']:
        raise ValueError('Source changed')
    media = data['media']
    if media and digest(Path(media['path']).read_bytes()) != media['sha256']:
        raise ValueError('Image changed')
    return data


def verify(path, observed, plain=False):
    data = checked(path)
    actual = {'body': normalize(observed)} if plain else Body(observed).summary()
    mismatches = [key for key, value in actual.items() if value != data['expected'][key]]
    return {'ok': not mismatches, 'mismatches': mismatches,
            'scope': 'text only; links/headings/images unchecked' if plain else 'body HTML',
            'expected_characters': len(data['expected']['body']),
            'observed_characters': len(actual['body'])}


class Ledger:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=10)
        path.chmod(0o600)
        self.db.row_factory = sqlite3.Row
        self.db.execute('''CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY, manifest TEXT NOT NULL, hash TEXT UNIQUE NOT NULL,
            source TEXT UNIQUE NOT NULL, approval TEXT NOT NULL, state TEXT NOT NULL,
            day TEXT UNIQUE, published_day TEXT UNIQUE, url TEXT, evidence TEXT)''')

    def close(self):
        self.db.close()

    def approve(self, manifest, evidence):
        if not evidence.strip():
            raise ValueError('Explicit author approval evidence is required')
        data = checked(manifest)
        try:
            with self.db:
                cursor = self.db.execute('''INSERT INTO queue
                    (manifest, hash, source, approval, state) VALUES (?, ?, ?, ?, 'approved')''',
                    (str(Path(manifest).resolve()), data['material_hash'], data['source'], evidence))
                return cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValueError('Article already queued or published; inspect ledger') from exc

    def claim(self, now=None):
        day = (now or datetime.now(ZoneInfo('Asia/Tokyo'))).astimezone(ZoneInfo('Asia/Tokyo')).date().isoformat()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if self.db.execute("SELECT 1 FROM queue WHERE state IN ('claimed','publishing','uncertain') OR day=? OR published_day=?", (day, day)).fetchone():
                return None
            row = self.db.execute("SELECT * FROM queue WHERE state='approved' ORDER BY id LIMIT 1").fetchone()
            if row is None:
                return None
            data = checked(row['manifest'])
            if data['material_hash'] != row['hash']:
                raise ValueError('Approved material changed')
            self.db.execute("UPDATE queue SET state='claimed', day=? WHERE id=?", (day, row['id']))
            return dict(self.db.execute('SELECT * FROM queue WHERE id=?', (row['id'],)).fetchone())

    def transition(self, item, state, url=None, evidence=None):
        allowed = {'claimed': {'publishing'}, 'publishing': {'uncertain', 'published'},
                   'uncertain': {'published'}}
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM queue WHERE id=?', (item,)).fetchone()
            if row is None or state not in allowed.get(row['state'], set()):
                raise ValueError('Invalid transition; inspect existing publication before resuming')
            data = checked(row['manifest'])
            if data['material_hash'] != row['hash']:
                raise ValueError('Approved material changed')
            if state == 'published':
                parsed = urlparse(url or '')
                if parsed.scheme != 'https' or parsed.netloc != 'note.com' or not re.fullmatch('/' + re.escape(data['account']) + r'/n/n[a-zA-Z0-9]+', parsed.path) or not evidence:
                    raise ValueError('Verified account publication URL and evidence required')
            published_day = datetime.now(ZoneInfo('Asia/Tokyo')).date().isoformat() if state == 'published' else None
            self.db.execute('UPDATE queue SET state=?, url=?, evidence=?, published_day=? WHERE id=?',
                            (state, url, evidence, published_day, item))

    def status(self):
        return [dict(row) for row in self.db.execute('SELECT * FROM queue ORDER BY id')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare')
    prep.add_argument('source', type=Path)
    prep.add_argument('--output', required=True, type=Path)
    prep.add_argument('--account', default='shimo4228')
    prep.add_argument('--tag', action='append', default=[])
    prep.add_argument('--image', type=Path)
    check = commands.add_parser('verify')
    check.add_argument('manifest', type=Path)
    check.add_argument('observed', type=Path, help='body-only HTML or text, excluding title/UI')
    check.add_argument('--plain', action='store_true')
    for name in ('approve', 'claim', 'status', 'transition'):
        command = commands.add_parser(name)
        command.add_argument('--db', required=True, type=Path)
        if name == 'approve':
            command.add_argument('manifest', type=Path)
            command.add_argument('--evidence', required=True)
        if name == 'transition':
            command.add_argument('id', type=int)
            command.add_argument('state', choices=['publishing', 'uncertain', 'published'])
            command.add_argument('--url')
            command.add_argument('--evidence')
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = str(prepare(args.source, args.output, args.account, args.tag, args.image))
        elif args.command == 'verify':
            result = verify(args.manifest, args.observed.read_text(), args.plain)
        else:
            ledger = Ledger(args.db)
            if args.command == 'approve':
                result = ledger.approve(args.manifest, args.evidence)
            elif args.command == 'transition':
                result = ledger.transition(args.id, args.state, args.url, args.evidence)
            else:
                result = getattr(ledger, args.command)()
            ledger.close()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == 'verify' and not result['ok']:
            raise SystemExit(1)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'error: {exc}\n')


if __name__ == '__main__':
    main()
