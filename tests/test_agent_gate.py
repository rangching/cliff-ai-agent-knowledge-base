import unittest
from scripts.agent_gate import validate


class AgentGateTests(unittest.TestCase):
    def pr(self, body=None):
        return {'head': {'ref': 'codex/example'}, 'body': body if body is not None else 'Closes #1\nBuilder: claude\nReviewer: codex\n## Security Impact\n無：僅更新說明文件。\n## Tests\nCI'}

    def test_valid(self):
        self.assertEqual(validate(self.pr()), ([], ['1']))

    def test_missing_metadata(self):
        self.assertEqual(len(validate(self.pr(''))[0]), 4)

    def test_same_reviewer_case_insensitive(self):
        pr = self.pr()
        pr['body'] = pr['body'].replace('Reviewer: codex', 'Reviewer: CLAUDE')
        self.assertTrue(any('不得相同' in x for x in validate(pr)[0]))

    def test_comment_cannot_supply_issue(self):
        pr = self.pr()
        pr['body'] = pr['body'].replace('Closes #1', '<!--\nCloses #1\n-->')
        self.assertTrue(validate(pr)[0])

    def test_placeholder_and_main_rejected(self):
        pr = self.pr()
        pr['head']['ref'] = 'main'
        pr['body'] = pr['body'].replace('無：僅更新說明文件。', 'TBD')
        self.assertEqual(len(validate(pr)[0]), 2)

    def test_duplicate_role_rejected(self):
        pr = self.pr()
        pr['body'] += '\nBuilder: opencode\n'
        self.assertTrue(validate(pr)[0])
