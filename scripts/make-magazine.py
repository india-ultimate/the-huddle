#!/usr/bin/env python
"""Script to convert the mirrored pages to a hugo blog."""

import glob
import json
from os import makedirs
from os.path import abspath, basename, dirname, join
import re

from bs4 import BeautifulSoup
from dateutil import parser
import html2text
import pytoml

HERE = dirname(abspath(__file__))
WWW_DIR = join(HERE, "..", "www.usaultimate.org", "huddle")
CONTENT_DIR = join(HERE, "..", "content")
DATA_DIR = join(HERE, "..", "data")


def create_md_content_dir():
    """Create a markdown content dir from the mirror directory."""

    makedirs(CONTENT_DIR, exist_ok=True)
    content = [
        parse_article(path)
        for path in glob.glob("{}/issue*_*.aspx".format(WWW_DIR))
    ]
    for post in content:
        create_hugo_post(post, CONTENT_DIR)


def parse_article(article_path):
    """Parse article and return a dict with metadata and markdown content."""

    with open(article_path) as f:
        soup = BeautifulSoup(f, "html.parser")

    title_node = soup.select_one(".georgia")
    title = re.sub("\s+", " ", title_node.text)
    author_node = title_node.next_sibling.next_sibling
    author = " ".join(author_node.text.split()[1:])
    date = (
        soup.select_one("img[width=300]").parent.parent.select_one("em").text
    )
    date = parser.parse(date).date().isoformat()

    hr_node = author_node.next_sibling.next_sibling
    html_content = " ".join(map(str, hr_node.next_siblings)).strip()
    content = html2text.html2text(html_content)
    issue = basename(article_path).split("_")[0].strip("issue")

    data = {
        "issue": issue,
        "title": title,
        "author": author,
        "content": content,
        "date": date,
    }
    return data


def create_hugo_post(content, dest_dir):
    """Create a hugo post from the given content."""

    text = content.pop("content")
    post = "+++\n{}+++\n\n{}\n".format(pytoml.dumps(content), text.strip())
    issue_dir = join(dest_dir, "issue-{}".format(content["issue"]))
    makedirs(issue_dir, exist_ok=True)
    post_path = join(issue_dir, "{}.md".format(slugify(content["title"])))
    with open(post_path, "w") as f:
        f.write(post)


def slugify(title):
    """Convert title to a slug"""
    return re.sub("[^a-z0-9]+", "-", title.lower())


def create_issue_index():
    issues = sorted(glob.glob("{}/issue???.aspx".format(WWW_DIR)))
    data = [
        {"number": i, "title": parse_issue_title(issue)}
        for i, issue in enumerate(issues, start=1)
    ]
    makedirs(DATA_DIR, exist_ok=True)
    with open(join(DATA_DIR, "issues.json"), "w") as f:
        json.dump(data, f, indent=2)

    return data


def parse_issue_title(issue_path):
    with open(issue_path) as f:
        soup = BeautifulSoup(f, "html.parser")

    title = re.sub("\s+", " ", soup.select_one("h3").text).strip()
    return " ".join(x.capitalize() for x in title.split())


if __name__ == "__main__":
    create_md_content_dir()
    create_issue_index()
