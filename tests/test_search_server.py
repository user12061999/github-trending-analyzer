import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from src.search_server import search_github, search_and_analyze
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
        for scope, qualifier, excluded in [('name', 'in:name', 'in:readme'), ('content', 'in:readme', 'in:name')]:
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


if __name__ == '__main__': unittest.main()
