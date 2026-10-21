"""Create a source release using an explicit file allowlist."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'github-trending-analyzer-2026-10-01'


def main():
    files = [ROOT / name for name in (
        'gh_trending.py', 'trending', 'README.md', '.env.example',
        'watchlist.json', 'SKILL.md', 'PROJECT_REVIEW.md', 'RESEARCH_SAMPLE_VI.md')]
    for folder, pattern in [('src', '*.py'), ('tests', '*.py'), ('docs', '*.md'), ('scripts', '*.py'), ('.agents/skills/github-trending-analyzer', '*.md')]:
        files.extend(sorted((ROOT / folder).rglob(pattern)))
    files = sorted(set(files))
    manifest = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    archive = output / (NAME + '.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as release:
        for path in files:
            release.write(path, 'github-trending-analyzer/' + str(path.relative_to(ROOT)))
        release.writestr('github-trending-analyzer/MANIFEST.json', json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / (NAME + '.sha256')).write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
    print(f'{archive}\n{len(files)} files + MANIFEST.json; {archive.stat().st_size:,} bytes\nSHA-256: {digest}')


if __name__ == '__main__':
    main()
