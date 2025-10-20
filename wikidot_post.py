import requests

class WikidotPOST:
    """
    Wikidot 远程发文接口
    用于远程bot账户登录并发文
    """

    LOGIN_URL = "https://www.wikidot.com/default--flow/login__LoginPopupScreen"
    TEST_URL = "https://www.wikidot.com/my/account"
    POST_URL_TEMPLATE = "https://{subsite}/ajax-module-connector.php"
    TARGET_URL_TEMPLATE = "https://{subsite}/"

    def __init__(self, username: str, password: str, subsite: str, user_agent: str = None):
        self.username = username
        self.password = password
        self.subsite = subsite
        self.session = requests.Session()
        if user_agent:
            self.session.headers.update({"User-Agent": user_agent})
        self.token7 = None

    def login(self) -> None:
        """登录 Wikidot"""
        post_data = {
            "login": self.username,
            "password": self.password,
            "originSiteId": "648902",
            "action": "Login2Action",
            "event": "login"
        }
        try:
            resp = self.session.post(self.LOGIN_URL, data=post_data, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"登录请求失败: {e}")

        test_resp = self.session.get(self.TEST_URL)
        if "Sign in" in test_resp.text or "Login" in test_resp.text:
            raise Exception("登录失败，用户名或密码错误")

    def prepare(self) -> None:

        target_url = self.TARGET_URL_TEMPLATE.format(subsite=self.subsite)
        try:
            resp = self.session.get(target_url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"访问子域失败: {e}")

        for c in self.session.cookies:
            if c.domain.endswith(self.subsite) and c.name == "wikidot_token7":
                self.token7 = c.value
                return
        raise Exception("未获取到 token7，请确认子域是否正确或已登录")

    def post_page(self, title: str, page: str, source: str, comments: str = "") -> dict:

        if not self.token7:
            self.prepare()  

        payload = {
            "title": title,
            "wiki_page": page,
            "source": source,
            "comments": comments,  
            "action": "WikiPageAction",
            "event": "savePage",
            "mode": "page",
            "wikidot_token7": self.token7
        }

        post_url = self.POST_URL_TEMPLATE.format(subsite=self.subsite)
        try:
            resp = self.session.post(post_url, data=payload, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"发文请求失败: {e}")

        return {
            "status_code": resp.status_code,
            "success": "wrong token7" not in resp.text.lower() and "error" not in resp.text.lower(),
            "response_text": resp.text[:200]  
        }
