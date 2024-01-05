from django.test import TestCase, RequestFactory

from passkeys.FIDO2 import get_current_platform


class TestCurrentPlatform(TestCase):
    def setUp(self) -> None:
        self.request_factory = RequestFactory()
        if not getattr(self, "assertEquals", None):
            self.assertEquals = self.assertEqual

    def check_platform(self,user_agent, platform):
        request = self.request_factory.get('/', HTTP_USER_AGENT=user_agent)
        self.assertEquals(get_current_platform(request), platform)

    def test_mac(self):
        self.check_platform("Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15","Apple")
    def test_ios(self):
        self.check_platform("Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15","Apple")
    def test_ipad(self):
        self.check_platform("Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1","Apple")

    def test_chrome_mac(self):
        self.check_platform("Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36","Chrome on Apple")

    def test_chrome_windows(self):
        self.check_platform("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36","Microsoft")

    def test_android(self):
        self.check_platform("Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36","Google")
        self.check_platform("Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36","Google")
        self.check_platform("Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36","Google")
