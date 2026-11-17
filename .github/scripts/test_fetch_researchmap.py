"""Run with: python3 -m unittest discover -s .github/scripts -v"""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("fetch_researchmap.sh")
VALID_RESPONSE = '{"items": [{"paper_title": {"en": "Example paper"}}]}'


class FetchResearchMapTest(unittest.TestCase):
    def fetch(self, responses):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "responses.json").write_text(json.dumps(responses))
            curl = root / "curl"
            curl.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, pathlib, sys\n"
                "root = pathlib.Path(os.environ['MOCK_ROOT'])\n"
                "counter = root / 'count'\n"
                "index = int(counter.read_text()) if counter.exists() else 0\n"
                "counter.write_text(str(index + 1))\n"
                "responses = json.loads((root / 'responses.json').read_text())\n"
                "status, body, code = responses[min(index, len(responses) - 1)]\n"
                "pathlib.Path(sys.argv[sys.argv.index('--output') + 1]).write_text(body)\n"
                "sys.stdout.write(status)\n"
                "sys.exit(code)\n"
            )
            curl.chmod(0o755)
            sleep = root / "sleep"
            sleep.write_text("#!/usr/bin/env bash\nexit 0\n")
            sleep.chmod(0o755)
            result = subprocess.run(
                ["bash", str(SCRIPT), "https://api.researchmap.jp/example/published_papers"],
                env={**os.environ, "PATH": f"{root}:{os.environ['PATH']}", "MOCK_ROOT": str(root)},
                capture_output=True,
                text=True,
            )
            return result, int((root / "count").read_text())

    def test_success(self):
        result, attempts = self.fetch([("200", VALID_RESPONSE, 0)])
        self.assertEqual((result.returncode, result.stdout, attempts), (0, VALID_RESPONSE, 1))

    def test_temporary_failure_recovers(self):
        for first in [("503", "maintenance", 0), ("000", "", 6), ("429", "rate limited", 0)]:
            with self.subTest(first=first):
                result, attempts = self.fetch([first, ("200", VALID_RESPONSE, 0)])
                self.assertEqual((result.returncode, result.stdout, attempts), (0, VALID_RESPONSE, 2))

    def test_outage_exhausts_retries_without_emitting_data(self):
        for response in [("503", "{ error: 'access_error' }", 0), ("000", "", 6), ("429", "rate limited", 0)]:
            with self.subTest(response=response):
                result, attempts = self.fetch([response])
                self.assertEqual((result.returncode, result.stdout, attempts), (75, "", 3))

    def test_permanent_http_error_fails(self):
        result, attempts = self.fetch([("403", "forbidden", 0)])
        self.assertEqual((result.returncode, result.stdout, attempts), (1, "", 1))

    def test_bad_data_fails_without_emitting_data(self):
        for body in ["<html>maintenance</html>", "", "{}", '{"items": null}', '{"items": {}}', '{"items": []}\n{"items": []}']:
            with self.subTest(body=body):
                result, attempts = self.fetch([("200", body, 0)])
                self.assertEqual((result.returncode, result.stdout, attempts), (1, "", 1))


if __name__ == "__main__":
    unittest.main()
