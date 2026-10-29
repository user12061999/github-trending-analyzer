import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from src.search_server import search_github, search_and_analyze, find_similar_repositories
from src.analyzer import RepoAnalysis, analyze_repository
from src.scraper import TrendingRepo
from src.html_dashboard import generate_html_dashboard


class TestGitHubSearch(unittest.TestCase):
    @patch('src.search_server.urllib.request.urlopen')
    def test_search_passes_query_and_count_and_maps_repos(self, request):
        response = {'total_count': 123, 'incomplete_results': True, 'items': [
            {'full_name': 'team/tool', 'description': 'Voice tool', 'language': 'Python', 'stargazers_count': 120, 'forks_count': 3}]}
        request.return_value.__enter__.return_value.read.return_value = json.dumps(response).encode()
        repos, total, incomplete = search_github('voice, clone', 2, 'any', 'Python', 'stars')
        params = parse_qs(urlsplit(request.call_args.args[0].full_url).query)
        self.assertIn('voice OR clone', params['q'][0])
        self.assertIn('is:public', params['q'][0])
        self.assertIn('language:"Python"', params['q'][0])
        self.assertEqual(params['per_page'], ['2'])
        self.assertEqual(params['sort'], ['stars'])
        self.assertEqual(repos[0].timeframe, 'search')
        self.assertEqual(repos[0].url, 'https://github.com/team/tool')
        self.assertEqual(total, 123)
        self.assertTrue(incomplete)

    @patch('src.search_server.urllib.request.urlopen')
    def test_name_and_content_scope_are_distinct(self, request):
        request.return_value.__enter__.return_value.read.return_value = b'{"items":[],"total_count":0}'
        for scope, qualifier, excluded in [('name', 'in:name', 'in:readme'), ('content', 'in:readme', 'in:name'), ('topic', 'topic:voice', 'in:name')]:
            search_github('voice', scope=scope)
            query = parse_qs(urlsplit(request.call_args.args[0].full_url).query)['q'][0]
            self.assertIn(qualifier, query)
            self.assertNotIn(excluded, query)
        with self.assertRaises(ValueError): search_github('voice', scope='invalid')

    def test_invalid_controls_fail_before_network(self):
        for limit in (0, 31, 1.5, True, '10'):
            with self.assertRaises(ValueError): search_github('voice', limit)
        with self.assertRaises(ValueError): search_github('x'*257)
        with self.assertRaises(ValueError): search_github('voice', language='\nBad')
        with self.assertRaises(ValueError): search_and_analyze({'query': 'voice', 'deep': 'yes'})

    @patch('src.search_server.analyze_repository')
    @patch('src.search_server.search_github')
    @patch('src.search_server.get_star_growth')
    def test_search_result_is_not_marked_trending(self, growth, search, analyze):
        growth.return_value = {'daily': 3, 'weekly': 20, 'monthly': 70}
        search.return_value = [object()], 1, False
        analyze.return_value = RepoAnalysis('t/r','t','r','https://github.com/t/r','Rust','1','0','search','tool','CLI','tool',velocity_badge='Breakout')
        output = search_and_analyze({'query': 'tool', 'limit': 1, 'deep': True, 'scope': 'content'})
        search.assert_called_once_with('tool', 1, 'all', '', 'best-match', scope='content')
        self.assertEqual(output['scope'], 'content')
        self.assertEqual(output['results'][0]['velocity_badge'], '')
        self.assertIn('GitHub Search', output['results'][0]['why_trending'])
        self.assertTrue(analyze.call_args.kwargs['deep'])
        growth.assert_called_once_with('t', 'r')
        self.assertEqual(output['results'][0]['growth']['weekly'], 20)

    @patch('src.search_server.analyze_repository')
    @patch('src.search_server.search_github')
    @patch('src.search_server.get_trending_repos')
    def test_blank_query_ranks_all_trending_before_limit(self, trending, search, analyze):
        def repo(name, new, total):
            return TrendingRepo('t/'+name, 't', name, 'https://github.com/t/'+name, 'Tool', 'Python', '#fff', total, '0', new, 'weekly')
        trending.return_value = [repo('giant', '20', '500000'), repo('rising', '1,200', '2000'), repo('middle', '100', '500')]
        def result(r, **kwargs):
            return RepoAnalysis(r.name,r.owner,r.repo,r.url,r.language,r.stars_total,r.stars_since,r.timeframe,r.description,'CLI','Tool',velocity_badge='High Velocity')
        analyze.side_effect = result
        data = search_and_analyze({'query':'  ', 'limit':2, 'language':'Python', 'timeframe':'weekly', 'sort':'updated'})
        self.assertEqual([r['name'] for r in data['results']], ['t/rising','t/middle'])
        self.assertEqual(data['total_count'], 3)
        self.assertEqual(data['mode'], 'trending')
        self.assertEqual(data['timeframe'], 'weekly')
        self.assertEqual(data['results'][0]['velocity_badge'], 'High Velocity')
        trending.assert_called_once_with(language='python', since='weekly', limit=None)
        search.assert_not_called()

    @patch('src.search_server.get_trending_repos')
    def test_invalid_empty_query_controls_do_not_fetch(self, trending):
        for payload in ({'query':'', 'limit':0}, {'query':'', 'timeframe':'yearly'}):
            with self.assertRaises(ValueError): search_and_analyze(payload)
        trending.assert_not_called()

    def test_search_analysis_with_watchlist(self):
        repo = TrendingRepo('t/r', 't', 'r', 'https://github.com/t/r', 'Voice tool', 'Python', '#fff', '1', '0', '0', 'search')
        result = analyze_repository(repo, fetch_readme=False, watchlist={'keywords':['voice'], 'languages':['Python'], 'categories':[]})
        self.assertGreater(result.match_score, 0)

    def test_live_dashboard_has_real_search_endpoint(self):
        html = generate_html_dashboard([], search_endpoint='/api/search')
        self.assertIn('const searchEndpoint = "/api/search"', html)
        self.assertIn('await fetch(searchEndpoint', html)
        self.assertIn('id="resultLimit"', html)
        self.assertIn('id="githubLanguage"', html)
        self.assertIn('id="searchScope"', html)
        self.assertIn('id="searchError"', html)
        self.assertIn('id="statusFilter"', html)
        self.assertIn('id="syncWatchlistBtn"', html)
        self.assertIn('feedback-bar', html)
        self.assertIn('/api/feedback', html)
        self.assertIn('/api/sync-watchlist', html)

    def test_dashboard_bilingual_support(self):
        html = generate_html_dashboard([])
        self.assertIn('id="langSelect"', html)
        self.assertIn('setLanguage', html)
        self.assertIn('I18N', html)
        self.assertIn('WHAT IT DOES & CORE PURPOSE', html)
        self.assertIn('KEY FEATURES & HIGHLIGHTS', html)

    def test_dashboard_has_bookmarks_elements(self):
        html = generate_html_dashboard([], search_endpoint='/api/search')
        self.assertIn('presetBookmarks', html)
        self.assertIn('btn-bookmark', html)
        self.assertIn('countBookmarks', html)
        self.assertIn('exportModal', html)
        self.assertIn('/api/bookmarks', html)
        self.assertIn('optScopeTopic', html)
        self.assertIn('topicsBar', html)
        self.assertIn('topicsPills', html)

    def test_dashboard_has_comparison_ide_and_star_history_features(self):
        html = generate_html_dashboard([], search_endpoint='/api/search')
        # Feature 1: Side-by-side comparison
        self.assertIn('compareDock', html)
        self.assertIn('comparisonModal', html)
        self.assertIn('btn-compare', html)
        self.assertIn('toggleCompareRepo', html)
        self.assertIn('openComparisonModal', html)

        # Feature 2: 1-Click IDE launchers
        self.assertIn('cursor://vscode.git/clone', html)
        self.assertIn('vscode://vscode.git/clone', html)
        self.assertIn('https://github.dev/', html)
        self.assertIn('codespaces.new/', html)

        # Feature 4: Star History
        self.assertIn('star-history.com', html)
        self.assertIn('api.star-history.com/svg', html)
        self.assertIn('star_history', html)
        self.assertIn('card-sh-section', html)
        self.assertIn('card-star-history-img', html)
        self.assertIn('btnToggleAllCharts', html)
        self.assertIn('toggleCardStarHistory', html)
        self.assertIn('toggleAllStarCharts', html)

    @patch('src.search_server.get_hn_trending_repos')
    @patch('src.search_server.analyze_repository')
    def test_search_and_analyze_with_hn_source(self, mock_analyze, mock_hn):
        mock_repo = TrendingRepo('deepseek-ai/DeepInfer', 'deepseek-ai', 'DeepInfer', 'https://github.com/deepseek-ai/DeepInfer', 'DeepSeek inference', 'Python', '#fff', '▲ 2000', '💬 800', '2000', 'hn_weekly')
        mock_repo.hn_points = 2000
        mock_repo.hn_comments = 800
        mock_repo.hn_url = 'https://news.ycombinator.com/item?id=123'
        mock_hn.return_value = [mock_repo]

        mock_analysis = RepoAnalysis('deepseek-ai/DeepInfer', 'deepseek-ai', 'DeepInfer', 'https://github.com/deepseek-ai/DeepInfer', 'Python', '▲ 2000', '2000', 'hn_weekly', 'DeepSeek inference', 'AI', 'Inference framework')
        mock_analyze.return_value = mock_analysis

        data = search_and_analyze({'source': 'hn', 'timeframe': 'weekly', 'limit': 1})
        self.assertEqual(data['source'], 'hn')
        self.assertEqual(data['mode'], 'hn')
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['velocity_badge'], '📰 Hacker News Trend')
        self.assertIn('Hacker News', data['results'][0]['why_trending'])
        self.assertEqual(data['results'][0]['hn_points'], 2000)

    @patch('src.search_server.search_github')
    def test_find_similar_repositories_by_topics(self, mock_search):
        repo1 = TrendingRepo('org/src-repo', 'org', 'src-repo', 'https://github.com/org/src-repo', 'Source tool', 'Python', '#fff', '100', '10', '10', 'search')
        repo2 = TrendingRepo('peer/alt-tool', 'peer', 'alt-tool', 'https://github.com/peer/alt-tool', 'Alternative tool with agent capability', 'Python', '#fff', '500', '50', '50', 'search')
        mock_search.return_value = ([repo1, repo2], 2, False)

        result = find_similar_repositories({
            'full_name': 'org/src-repo',
            'topics': ['agent', 'llm'],
            'language': 'Python',
            'limit': 3
        })

        self.assertEqual(result['source_repo'], 'org/src-repo')
        self.assertEqual(result['query_used'], 'agent llm')
        self.assertEqual(len(result['similar_repos']), 1)
        self.assertEqual(result['similar_repos'][0]['name'], 'peer/alt-tool')
        self.assertIn('Chủ đề #agent', result['similar_repos'][0]['similarity_reason'])
        self.assertIn('Cùng ngôn ngữ Python', result['similar_repos'][0]['similarity_reason'])

    @patch('src.search_server.search_github')
    def test_find_similar_repositories_fallback_description(self, mock_search):
        repo_sim = TrendingRepo('another/comp', 'another', 'comp', 'https://github.com/another/comp', 'Speech synthesizer', 'Python', '#fff', '300', '30', '30', 'search')
        mock_search.return_value = ([repo_sim], 1, False)

        result = find_similar_repositories({
            'full_name': 'my/voice',
            'topics': ['python'],
            'description': 'Realtime neural voice synthesizer',
            'language': 'Rust',
        })
        self.assertEqual(len(result['similar_repos']), 1)
        self.assertEqual(result['similar_repos'][0]['name'], 'another/comp')

    def test_dashboard_has_similar_repos_elements(self):
        html = generate_html_dashboard([], search_endpoint='/api/search')
        self.assertIn('btn-similar', html)
        self.assertIn('similarModal', html)
        self.assertIn('openSimilarModal', html)
        self.assertIn('addSimilarToCompare', html)
        self.assertIn('/api/similar', html)
        self.assertIn('btnSimilar', html)

    def test_dashboard_has_architecture_mermaid_feature(self):
        html = generate_html_dashboard([], search_endpoint='/api/search')
        self.assertIn('cdn.jsdelivr.net/npm/mermaid', html)
        self.assertIn('mermaid.initialize', html)
        self.assertIn('renderMermaidSafe', html)
        self.assertIn('copyMermaidCode', html)
        self.assertIn('arch-wrapper', html)
        self.assertIn('arch-canvas', html)
        self.assertIn('mermaid.live', html)

    def test_dashboard_has_release_radar_feature(self):
        html = generate_html_dashboard([], search_endpoint='/api/search')
        self.assertIn('tag-release', html)
        self.assertIn('release-radar-wrapper', html)
        self.assertIn('release-hero-card', html)
        self.assertIn('release-highlights-box', html)
        self.assertIn('formatReleaseDate', html)
        self.assertIn('btn-release-github', html)

    def test_dashboard_has_community_pulse_feature(self):
        html = generate_html_dashboard([], search_endpoint='/api/search')
        self.assertIn('tag-pulse', html)
        self.assertIn('tag-license', html)
        self.assertIn('pulse-wrapper', html)
        self.assertIn('pulse-grid', html)
        self.assertIn('contributors-box', html)
        self.assertIn('pulse-verdict-box', html)



if __name__ == '__main__':
    unittest.main()
