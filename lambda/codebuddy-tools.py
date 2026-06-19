import json
import os
import re
import urllib.request

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

def bedrock_response(event, status_code, body):
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "apiPath": event.get("apiPath"),
            "httpMethod": event.get("httpMethod"),
            "httpStatusCode": status_code,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(body, ensure_ascii=False)
                }
            }
        }
    }

def github_request(url, method="GET", data=None):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "CodeBuddy-Agent"
    }

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers
    )

    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))

def get_params(event):
    params = {}

    for p in event.get("parameters", []):
        params[p.get("name")] = p.get("value")

    request_body = event.get("requestBody", {})
    content = request_body.get("content", {})
    app_json = content.get("application/json", {})
    properties = app_json.get("properties", [])

    for p in properties:
        params[p.get("name")] = p.get("value")

    return params

def get_github_pr(event):
    params = get_params(event)

    owner = params.get("owner")
    repo = params.get("repo")
    pr_number = params.get("pr_number")

    if not owner or not repo or not pr_number:
        return bedrock_response(event, 400, {"error": "owner, repo, pr_number are required"})

    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

    pr = github_request(pr_url)
    files = github_request(files_url)

    return bedrock_response(event, 200, {
        "title": pr.get("title"),
        "body": pr.get("body"),
        "state": pr.get("state"),
        "author": pr.get("user", {}).get("login"),
        "html_url": pr.get("html_url"),
        "changed_files": [
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
                "patch": f.get("patch", "")
            }
            for f in files
        ]
    })

def post_pr_comment(event):
    params = get_params(event)

    owner = params.get("owner")
    repo = params.get("repo")
    pr_number = params.get("pr_number")
    comment = params.get("comment")

    if not owner or not repo or not pr_number or not comment:
        return bedrock_response(event, 400, {"error": "owner, repo, pr_number, comment are required"})

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    data = json.dumps({"body": comment}).encode("utf-8")
    result = github_request(url, method="POST", data=data)

    return bedrock_response(event, 200, {
        "success": True,
        "comment_url": result.get("html_url")
    })

def analyze_complexity(event):
    params = get_params(event)
    code = params.get("code", "")

    if not code:
        return bedrock_response(event, 400, {"error": "code is required"})

    keywords = ["if", "elif", "for", "while", "case", "except", "and", "or"]
    complexity = 1

    for keyword in keywords:
        complexity += len(re.findall(rf"\b{keyword}\b", code))

    if complexity <= 10:
        level = "좋음"
        suggestion = "복잡도는 낮은 편입니다."
    elif complexity <= 20:
        level = "주의"
        suggestion = "함수 분리와 조건문 단순화를 고려하세요."
    else:
        level = "위험"
        suggestion = "리팩토링이 필요합니다. 함수를 여러 개로 나누는 것을 권장합니다."

    return bedrock_response(event, 200, {
        "complexity_score": complexity,
        "level": level,
        "suggestion": suggestion
    })

def send_slack(event):
    params = get_params(event)
    message = params.get("message")

    if not message:
        return bedrock_response(event, 400, {"error": "message is required"})

    if not SLACK_WEBHOOK_URL:
        return bedrock_response(event, 200, {
            "success": False,
            "message": "Slack webhook URL is not configured"
        })

    data = json.dumps({"text": message}).encode("utf-8")

    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"}
    )

    urllib.request.urlopen(req)

    return bedrock_response(event, 200, {
        "success": True,
        "message": "Slack notification sent"
    })

def lambda_handler(event, context):
    try:
        api_path = event.get("apiPath")

        if api_path == "/pr":
            return get_github_pr(event)

        if api_path == "/comment":
            return post_pr_comment(event)

        if api_path == "/complexity":
            return analyze_complexity(event)

        if api_path == "/slack":
            return send_slack(event)

        return bedrock_response(event, 404, {
            "error": f"Unknown apiPath: {api_path}"
        })

    except Exception as e:
        return bedrock_response(event, 500, {"error": str(e)})