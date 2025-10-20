from wikidot_post import WikidotPOST

api = WikidotPOST("username", "password", "example.wikidot.com", user_agent="Mozilla/5.0")
try:
    api.login()
    result = api.post_page(
        title="测试标题",
        page="test-page",
        source="正文内容",
        comments="自动发文测试"
    )
    print("发文状态:", result["success"])
    print("HTTP 状态码:", result["status_code"])
except Exception as e:
    print("发生错误：", e)
