import io
import json
import unittest
from unittest.mock import patch
from contextlib import redirect_stderr

from src.analyzer import analyze_repository, analyze_repo_heuristic, analyze_repo_ai
from src.formatter import generate_markdown_report
from src.html_dashboard import generate_html_dashboard
from src.research import sections, linked_documents, collect_sources, research_context
from src.scraper import TrendingRepo
from src.maturity import extract_quick_run


def repo():
    return TrendingRepo('team/tool', 'team', 'tool', 'https://github.com/team/tool',
                        'Agent retrieval toolkit', 'Python', '#fff', '100', '10', '20', 'daily')

README = '''# Tool
An agent retrieval toolkit.

## Features
- Retrieve documents using indexed embeddings and rank relevant chunks

## Architecture
Input query -> index lookup -> ranked context -> response.

## Usage
```python
client.search("example")
# ## This is code, not a Markdown section
```

## Requirements
Requires a local database and API credentials.

## Installation
pip install tool

## Comparison
Unlike a hosted service, storage is managed locally.

[Architecture](docs/architecture.md)
'''


class TestResearch(unittest.TestCase):
    def test_headings_in_code_do_not_split_sections(self):
        usage = dict(sections(README))['Usage']
        self.assertIn('This is code', usage)
        self.assertIn('Requirements', dict(sections(README)))

    def test_document_links_are_bounded_and_stay_in_repo(self):
        links = '[a](docs/architecture.md) [b](../secret.md) [c](https://evil.test/doc.md) [d](README.md) [e](https://github.com/team/tool/blob/main/docs/usage.md)'
        self.assertEqual(linked_documents(links, 'team', 'tool', 'main'), ['docs/architecture.md', 'docs/usage.md'])

    @patch('src.research.request_text')
    def test_deep_collects_metadata_and_document(self, request):
        request.side_effect = [json.dumps({'default_branch': 'main', 'archived': False, 'license': {'spdx_id': 'MIT'}}), '# Architecture\nDatabase retrieves chunks.']
        sources, gaps = collect_sources(repo(), README, deep=True)
        self.assertEqual(len(sources), 3)
        self.assertEqual(sources[2]['title'], 'docs/architecture.md')
        self.assertEqual(gaps, [])
        self.assertIn('MIT', sources[1]['content'])

    @patch('src.research.request_text', side_effect=TimeoutError)
    def test_partial_source_failure_is_visible(self, request):
        sources, gaps = collect_sources(repo(), README, deep=True)
        self.assertEqual(len(sources), 1)
        self.assertEqual(len(gaps), 2)

    @patch('src.analyzer.fetch_repo_readme', return_value=README)
    def test_pipeline_keeps_specific_sections_and_sources(self, fetch):
        analysis = analyze_repository(repo())
        self.assertIn('ranked context', analysis.how_it_works[0])
        self.assertIn('credentials', analysis.limitations[0])
        self.assertTrue(analysis.comparisons)
        self.assertTrue(analysis.evidence)
        report = generate_markdown_report([analysis])
        self.assertIn('Cách hoạt động', report)
        self.assertIn('[S1]', report)
        self.assertIn('Nguồn đã đọc', report)

    def test_quick_run_keeps_full_arguments_and_prefers_installation(self):
        for command in ('pip install tool==1.2.3', 'npx skills add team/tool', 'docker run -e TOKEN=$TOKEN image'):
            self.assertEqual(extract_quick_run('## Installation\n```bash\n' + command + '\n```'), command)
        self.assertEqual(extract_quick_run('## Skills\n`npx skills add team/tool`\n## Installation\n`pip install actual-tool`'), 'pip install actual-tool')

    def test_features_preserve_link_label(self):
        analysis = analyze_repo_heuristic(repo(), '## Features\n- [Sandbox](docs/sandbox.md): runtime isolation for agents')
        self.assertIn('Sandbox', analysis.key_features[0])

    def test_missing_readme_does_not_invent_features(self):
        analysis = analyze_repo_heuristic(repo())
        self.assertEqual(analysis.key_features, [])
        self.assertNotIn('tối ưu hiệu năng', analysis.core_purpose)
        self.assertIn('Chưa xác định', analysis.why_trending)

    def test_long_readme_preserves_late_important_section(self):
        sources, _ = collect_sources(repo(), '# Intro\n' + 'padding ' * 1200 + '\n## Limitations\nOnly local storage is supported.')
        context = research_context(sources, budget=4000)
        self.assertIn('Only local storage is supported.', context)

    @patch('src.analyzer.urllib.request.urlopen')
    def test_ai_schema_rejection_falls_back_with_warning(self, request):
        request.return_value.__enter__.return_value.read.return_value = json.dumps({'candidates': [{'content': {'parts': [{'text': json.dumps({'core_purpose': 'tool', 'key_features': 'wrong type'})}]}}]}).encode()
        stream = io.StringIO()
        with redirect_stderr(stream):
            analysis = analyze_repo_ai(repo(), README, gemini_api_key='fake-test-key', model='test-model')
        self.assertIsNone(analysis)
        self.assertIn('ValueError', stream.getvalue())
        self.assertIn('x-goog-api-key', {key.lower(): value for key, value in request.call_args.args[0].header_items()})

    def test_dashboard_escapes_untrusted_data_and_no_inline_copy(self):
        analysis = analyze_repository(repo(), fetch_readme=False)
        analysis.description = '</script><script>alert(1)</script>'
        analysis.quick_run = 'docker run -e A="value" image'
        html = generate_html_dashboard([analysis])
        self.assertNotIn(analysis.description, html)
        self.assertIn('\\u003c/script>', html)
        self.assertNotIn('onclick="copyCmd', html)
        self.assertIn('paragraph.textContent = text', html)


if __name__ == '__main__':
    unittest.main()
