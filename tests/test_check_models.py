import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

SCRIPT = Path(__file__).resolve().parents[1] / "skills/sinapisai-integration/scripts/check_models.py"
SPEC = importlib.util.spec_from_file_location("check_models", SCRIPT)
check_models = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_models)
FAKE_KEY = "fixture-only-not-a-real-key"


class CheckModelsTests(unittest.TestCase):
    def run_check(self, payload=None, args=None, key=FAKE_KEY, error=None):
        opener = MagicMock()
        response = MagicMock()
        response.read.return_value = json.dumps(payload).encode()
        opener.open.return_value.__enter__.return_value = response
        if error is not None:
            opener.open.side_effect = error
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = check_models.main(args or [], {"SINAPISAI_API_KEY": key}, opener)
        self.assertNotIn(FAKE_KEY, stdout.getvalue() + stderr.getvalue())
        return code, stdout.getvalue(), stderr.getvalue(), opener

    def test_single_authenticated_get_checks_exact_model(self):
        code, stdout, stderr, opener = self.run_check({"data": [{"id": "sinapisai/mio"}]})
        self.assertEqual(code, 0)
        self.assertIn("尚未发送对话", stdout)
        self.assertEqual(stderr, "")
        opener.open.assert_called_once()
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, check_models.MODELS_URL)
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.get_header("Authorization"), "Bearer " + FAKE_KEY)
        self.assertIsNone(request.data)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 20)

    def test_missing_key_does_not_request(self):
        code, _, stderr, opener = self.run_check(key="")
        self.assertEqual(code, 1)
        self.assertIn("SINAPISAI_API_KEY", stderr)
        opener.open.assert_not_called()

    def test_invalid_header_key_does_not_request_or_print(self):
        code, _, stderr, opener = self.run_check(key="fake\nheader")
        self.assertEqual(code, 1)
        self.assertNotIn("fake", stderr)
        opener.open.assert_not_called()

    def test_missing_model_is_not_success(self):
        code, stdout, stderr, _ = self.run_check({"data": [{"id": "other/model"}]})
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("未返回所选模型", stderr)

    def test_requested_model_is_preserved(self):
        code, _, _, _ = self.run_check({"data": [{"id": "other/model"}]}, ["--model", "other/model"])
        self.assertEqual(code, 0)

    def test_list_prints_only_sorted_distinct_ids(self):
        code, stdout, _, _ = self.run_check({"data": [{"id": "z/model", "private_field": "fixture-private"}, {"id": "a/model"}, {"id": "z/model"}]}, ["--list"])
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "a/model\nz/model\n")
        self.assertNotIn("fixture-private", stdout)

    def test_invalid_model_shapes_are_errors(self):
        for payload in [None, [], {}, {"data": {}}, {"data": [None]}, {"data": [{"id": 123}]}, {"data": [{"id": ""}]}, {"data": [{"id": "bad\nmodel"}]}]:
            with self.subTest(payload=payload):
                code, stdout, stderr, _ = self.run_check(payload)
                self.assertEqual(code, 1)
                self.assertEqual(stdout, "")
                self.assertIn("无法识别", stderr)

    def test_empty_list_is_valid_but_not_model_access(self):
        code, _, _, _ = self.run_check({"data": []})
        self.assertEqual(code, 2)

    def test_http_errors_do_not_retry_or_disclose_body(self):
        for status in [301, 401, 403, 429, 500]:
            with self.subTest(status=status):
                error = HTTPError(check_models.MODELS_URL, status, FAKE_KEY, {}, io.BytesIO(FAKE_KEY.encode()))
                code, stdout, stderr, opener = self.run_check(error=error)
                self.assertEqual(code, 1)
                self.assertEqual(stdout, "")
                self.assertIn(str(status), stderr)
                opener.open.assert_called_once()
                self.assertTrue(error.fp.closed)

    def test_network_errors_are_sanitized_and_not_retried(self):
        for error in [URLError(FAKE_KEY), TimeoutError(FAKE_KEY), OSError(FAKE_KEY)]:
            with self.subTest(error=type(error)):
                code, _, stderr, opener = self.run_check(error=error)
                self.assertEqual(code, 1)
                self.assertIn("网络", stderr)
                opener.open.assert_called_once()

    def test_redirect_handler_does_not_forward_credentials(self):
        self.assertIsNone(check_models.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://example.invalid"))
        with patch.object(check_models, "build_opener", return_value=MagicMock()) as build:
            with contextlib.redirect_stderr(io.StringIO()):
                check_models.main([], {"SINAPISAI_API_KEY": FAKE_KEY})
            self.assertIsInstance(build.call_args.args[0], check_models.NoRedirect)

    def test_malformed_json_is_sanitized(self):
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value.read.return_value = FAKE_KEY.encode()
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = check_models.main([], {"SINAPISAI_API_KEY": FAKE_KEY}, opener)
        self.assertEqual(code, 1)
        self.assertNotIn(FAKE_KEY, stdout.getvalue() + stderr.getvalue())

    def test_response_size_is_bounded(self):
        opener = MagicMock()
        response = opener.open.return_value.__enter__.return_value
        response.read.return_value = b"x" * (check_models.MAX_RESPONSE_BYTES + 1)
        with contextlib.redirect_stderr(io.StringIO()):
            code = check_models.main([], {"SINAPISAI_API_KEY": FAKE_KEY}, opener)
        self.assertEqual(code, 1)
        response.read.assert_called_once_with(check_models.MAX_RESPONSE_BYTES + 1)


if __name__ == "__main__":
    unittest.main()
