import argparse

import requests


def login_and_get_token(base_url: str, email: str, password: str) -> str:
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Send GET request with optional Bearer token")
    parser.add_argument("--url", default="http://127.0.0.1:8000/users/me")
    parser.add_argument("--token", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    token = args.token
    if not token and args.email and args.password:
        base_url = args.url.split("/", 3)[:3]
        token = login_and_get_token("/".join(base_url), args.email, args.password)

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(args.url, headers=headers, timeout=10)

    print(response.status_code)
    try:
        print(response.json())
    except ValueError:
        print(response.text)


if __name__ == "__main__":
    main()
