import gzip
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from accuracy_archive import archive


class ArchiveTests(unittest.TestCase):
    def test_disabled(self):
        with patch.dict(os.environ, {'NFL_AUDIT_DIR': ''}):
            self.assertIsNone(archive('NFL', 'inputs', 'run', {}))

    def test_roundtrip_and_no_environment_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {'NFL_AUDIT_DIR': directory,
                                        'GITHUB_SHA': 'abc', 'ODDS_API_KEY': 'not-for-export'}):
                path = archive('NFL', 'inputs', 'run', {
                    'history': pd.DataFrame([{'yards': 12, 'unknown': float('nan')}]),
                    'odds': [None, -110], 'missing': float('nan')})
                with gzip.open(path, 'rt') as handle:
                    text = handle.read()
                result = json.loads(text)
                self.assertEqual(result['inputs']['history'][0]['yards'], 12)
                self.assertIsNone(result['inputs']['missing'])
                self.assertFalse(result['publication_receipt'])
                self.assertNotIn('not-for-export', text)
                self.assertEqual(result['commit'], 'abc')


if __name__ == '__main__':
    unittest.main()

