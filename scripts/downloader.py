#!/bin/python

import os

from bs4 import BeautifulSoup
import requests


BASE_URL = "https://archive.usaultimate.org/huddle/issue{:03d}.aspx"
HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(HERE, "..", "archive")
IMAGE_DIR = os.path.join(HERE, "..", "static", "images")
SESSION = requests.Session()


def download_image(url, force=False):
    name = os.path.basename(url)
    path = os.path.join(IMAGE_DIR, name)
    if not force and os.path.exists(path):
        print(f"Skipping image: {name} ...")
        return

    response = SESSION.get(url)
    if not response.status_code == 200:
        print(f"Failed to download image {name} with code: {response.status_code}")
        return

    with open(path, "wb") as f:
        f.write(response.content)


def download_article(url, force=False):
    # Broken index page in Issue 23
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

    soup = BeautifulSoup(text, "html.parser")
    for img in soup.findAll("img"):
        src = img.attrs.get("src")
        if not src.startswith("https://www.usaultimate.org/assets/1/News/"):
            continue
        name = os.path.basename(src)
        img.attrs["src"] = f"/images/{name}"
        url = src.replace("www.", "archive.")
        download_image(url, force=force)

    with open(path, "w") as f:
        f.write(str(soup))


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
    os.makedirs(IMAGE_DIR, exist_ok=True)
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
