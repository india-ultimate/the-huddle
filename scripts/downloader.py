#!/bin/python

import os

from bs4 import BeautifulSoup
import requests


BASE_URL = "https://archive.usaultimate.org/huddle/issue{:03d}.aspx"
HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(HERE, "..", "archive")
SESSION = requests.Session()


def download_article(url, force=False):
    if "sparling-" in url:
        url = url.replace("sparling-", "sparling_")

    name = os.path.basename(url)
    path = os.path.join(ARCHIVE_DIR, name)
    if not force and os.path.exists(path):
        print(f"Skipping article: {name} ...")
        return

    print(f"Downloading article: {name} ...")
    response = SESSION.get(url)
    text = response.text
    if not response.status_code == 200:
        print(f"Failed to download article {name} with code: {response.status_code}")
        return

    with open(path, "w") as f:
        f.write(text)


def download_issue(num, force=False):
    url = BASE_URL.format(num)
    print(f"Downloading issue {num} ...")
    path = os.path.join(ARCHIVE_DIR, os.path.basename(url))
    response = SESSION.get(url)
    text = response.text
    with open(path, "w") as f:
        f.write(text)

    soup = BeautifulSoup(text, "html.parser")
    links = soup.findAll("table", {"width": "300"})[1].findAll("a")
    urls = {link.attrs.get("href").replace("www.", "archive.") for link in links}
    for url in urls:
        download_article(url, force=force)


def main(issue_number=None, force=False):
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    if issue_number:
        download_issue(issue_number, force)

    else:
        for issue_number in range(1, 34):
            download_issue(issue_number, force)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", type=int, required=False)
    parser.add_argument("--force", action="store_true", required=False)
    args = parser.parse_args()
    main(issue_number=args.issue, force=args.force)
