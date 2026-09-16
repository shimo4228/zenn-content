import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from note_publish import prepare, verify, Ledger


@pytest.fixture
def material(tmp_path):
    source = tmp_path / 'article.md'
    source.write_text('---\ntitle: Test\n---\n## Heading\n\nBody **bold** [link](https://example.com)[^x].\n\n[^x]: Footnote.\n')
    return prepare(source, tmp_path / 'assets', 'shimo4228', ['AI'], None)


def test_prepare_verify_and_missing_link(material):
    manifest = json.loads(material.read_text())
    assert manifest['title'] == 'Test'
    html = (material.parent / 'body.html').read_text()
    assert '[1]' in html and 'Footnote.' in html
    assert verify(material, html)['ok']
    result = verify(material, html.replace('https://example.com', 'https://wrong.example'))
    assert not result['ok'] and 'links' in result['mismatches']


def test_changed_material_blocks_claim(material, tmp_path):
    ledger = Ledger(tmp_path / 'ledger.sqlite')
    ledger.approve(material, 'User explicitly approved article and assets')
    (material.parent / 'body.html').write_text('changed')
    with pytest.raises(ValueError, match='changed'):
        ledger.claim()


def test_daily_and_uncertain_block(material, tmp_path):
    ledger = Ledger(tmp_path / 'ledger.sqlite')
    ledger.approve(material, 'User approval')
    first = ledger.claim()
    assert first['state'] == 'claimed'
    assert ledger.claim() is None
    ledger.transition(first['id'], 'publishing')
    ledger.transition(first['id'], 'uncertain')
    assert ledger.claim(datetime(2030, 1, 1, tzinfo=ZoneInfo('Asia/Tokyo'))) is None
    ledger.transition(first['id'], 'published', 'https://note.com/shimo4228/n/nabc', 'Public page verified')
    with pytest.raises(ValueError):
        ledger.approve(material, 'Repeated approval')


def test_no_approval_no_claim(tmp_path):
    ledger = Ledger(tmp_path / 'ledger.sqlite')
    assert ledger.claim() is None


def test_semantic_structure_and_anchor_coverage():
    from note_publish import Body
    original = '<blockquote><p><strong>Bold</strong> <a href="https://a">A</a> <a href="https://b">B</a></p></blockquote>'
    equivalent = original.replace('strong', 'b')
    damaged = '<p>Bold <a href="https://a">A B</a><a href="https://b"></a></p>'
    assert Body(original).summary() == Body(equivalent).summary()
    assert Body(original).summary()['structure'] != Body(damaged).summary()['structure']


def test_removed_quote_or_emphasis_fails_verification(tmp_path):
    source = tmp_path / 'quote.md'
    source.write_text('# Title\n\n> **Quoted** text\n')
    manifest = prepare(source, tmp_path / 'out', 'shimo4228', [], None)
    html = (manifest.parent / 'body.html').read_text()
    for tag in ('blockquote', 'strong'):
        altered = html.replace(f'<{tag}>', '').replace(f'</{tag}>', '')
        assert 'structure' in verify(manifest, altered)['mismatches']


def test_reject_zenn_directive(tmp_path):
    path = tmp_path / 'a.md'
    path.write_text('# Title\n\n:::message\nText\n:::')
    with pytest.raises(ValueError, match='Zenn'):
        prepare(path, tmp_path / 'out', 'shimo4228', [], None)


def test_h1_title_and_image_changes(tmp_path):
    source, image = tmp_path / 'note.md', tmp_path / 'image.png'
    source.write_text('# Title\n\n本文。')
    image.write_bytes(b'original')
    manifest = prepare(source, tmp_path / 'assets', 'shimo4228', [], image)
    assert json.loads(manifest.read_text())['title'] == 'Title'
    assert verify(manifest, '本文。', plain=True)['ok']
    image.write_bytes(b'changed')
    with pytest.raises(ValueError, match='Image changed'):
        verify(manifest, '本文。', plain=True)


def test_transitions_require_account_url_and_evidence(material, tmp_path):
    ledger = Ledger(tmp_path / 'ledger.sqlite')
    with pytest.raises(ValueError, match='approval'):
        ledger.approve(material, '')
    ledger.approve(material, 'Approved')
    item = ledger.claim()['id']
    with pytest.raises(ValueError, match='Invalid transition'):
        ledger.transition(item, 'published')
    ledger.transition(item, 'publishing')
    with pytest.raises(ValueError, match='URL'):
        ledger.transition(item, 'published', 'https://note.com/other/n/nabc', 'seen')
    ledger.transition(item, 'published', 'https://note.com/shimo4228/n/nabc', 'seen')
    assert ledger.status()[0]['published_day']


def test_source_and_manifest_changes(material):
    data = json.loads(material.read_text())
    data['tags'].append('unapproved')
    material.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='Manifest changed'):
        verify(material, '')


def test_long_body_and_headings_detected(tmp_path):
    source = tmp_path / 'long.md'
    source.write_text('# Title\n\n## Heading\n\n' + ('長い文章。' * 3000) + '\n\n> Quote\n')
    manifest = prepare(source, tmp_path / 'assets', 'shimo4228', [], None)
    html = (manifest.parent / 'body.html').read_text()
    assert verify(manifest, html)['ok']
    assert 'headings' in verify(manifest, html.replace('<h2', '<p').replace('</h2>', '</p>'))['mismatches']


@pytest.fixture(autouse=True)
def close_ledgers(monkeypatch):
    instances = []
    original = Ledger.__init__

    def tracked(self, path):
        original(self, path)
        instances.append(self)

    monkeypatch.setattr(Ledger, '__init__', tracked)
    yield
    for ledger in instances:
        ledger.close()


def test_cli_prepare_verify_status(tmp_path, monkeypatch, capsys):
    from note_publish import main
    source = tmp_path / 'cli.md'
    source.write_text('# CLI title\n\nBody')
    output = tmp_path / 'assets'
    monkeypatch.setattr('sys.argv', ['note_publish', 'prepare', str(source), '--output', str(output)])
    main()
    assert str(output / 'manifest.json') in capsys.readouterr().out
    monkeypatch.setattr('sys.argv', ['note_publish', 'verify', str(output / 'manifest.json'), str(output / 'body.html')])
    main()
    assert json.loads(capsys.readouterr().out)['ok']
    monkeypatch.setattr('sys.argv', ['note_publish', 'status', '--db', str(tmp_path / 'queue.sqlite')])
    main()
    assert json.loads(capsys.readouterr().out) == []


def test_table_becomes_bullet_list_with_headers(tmp_path):
    source = tmp_path / 'table.md'
    source.write_text('# Title\n\n| 列A | 列B |\n|---|---|\n| **あ** | い |\n| う | [え](https://e.example) |\n')
    manifest = prepare(source, tmp_path / 'out', 'shimo4228', [], None)
    html = (manifest.parent / 'body.html').read_text()
    assert '<table' not in html and html.count('<li>') == 2
    assert '<strong>列A</strong>: <strong>あ</strong> / <strong>列B</strong>: い' in html
    assert '<a href="https://e.example">え</a>' in html
    assert verify(manifest, html)['ok']
