import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import build_knowledge_base as kb


class KnowledgeBaseTests(unittest.TestCase):
    def test_filename_and_episode(self):
        self.assertEqual(kb.sanitize_filename(' A/B: C? '), 'A_B__C')
        self.assertEqual(len(kb.sanitize_filename('a' * 150)), 100)
        self.assertEqual(kb.parse_ep('基本功 EP095')[0], 9.5)
        self.assertEqual(kb.parse_ep('EP 12')[0], 12.0)
        self.assertEqual(kb.parse_ep('無集數')[1], '專題影片')

    def test_vtt_to_markdown_offline_integration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.vtt'
            path.write_text('WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<c>你好</c>\n你好\n\n00:00:50.000 --> 00:00:52.000\n再見\n', encoding='utf-8')
            result = kb.vtt_to_markdown(path, '標題', 'https://example.com/video', 'id', '類別')
        self.assertIn('**[00:00:01]** 你好', result)
        self.assertIn('**[00:00:50]** 再見', result)
        self.assertNotIn('<c>', result)
        self.assertNotIn('你好你好', result)

    def test_channel_results_are_deduplicated_without_network(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(kb, 'TEMP_DIR', directory), patch.object(kb.yt_dlp, 'YoutubeDL') as downloader:
            downloader.return_value.__enter__.return_value.extract_info.return_value = {'entries': [{'id': 'abc', 'title': 'Claude EP01', 'url': 'https://example.com'}]}
            videos = kb.fetch_channel_videos()
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]['id'], 'abc')
