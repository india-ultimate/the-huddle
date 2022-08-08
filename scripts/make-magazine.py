#!/usr/bin/env python
"""Script to convert the mirrored pages to a hugo blog."""

import glob
import json
from os import makedirs
from os.path import abspath, basename, dirname, exists, join
import re
import subprocess

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
        parse_article(path) for path in glob.glob("{}/issue*_*.aspx".format(WWW_DIR))
    ]
    for post in content:
        create_hugo_post(post, CONTENT_DIR)


def add_premise_questions():
    paths = [path for path in glob.glob("{}/issue[0-9][0-9][0-9].aspx".format(WWW_DIR))]
    for path in sorted(paths):
        parse_premise_questions(path)


def parse_premise_questions(article_path):
    with open(article_path) as f:
        soup = BeautifulSoup(f, "html.parser")
    row = soup.find("td", {"width": "600"})
    row.select_one("table").replace_with("")
    row.select_one(".fb-like").replace_with("")
    row.select_one("hr").replace_with("")
    for line_break in row.select("br"):
        line_break.replace_with("\n")
    for tag in row():
        if "text-align: center" in tag.attrs.get("style", ""):
            tag.replace_with("")
        elif tag.name == "span":
            for t in tag():
                if t.name == "font":
                    t.replace_with(t.text)
            tag.replace_with(tag.renderContents().decode("utf8"))
        else:
            del tag["style"]

        if "thehuddle@usaultimate.org" in tag.text:
            try:
                tag.replace_with("")
            except ValueError:
                pass

    html = row.renderContents().decode("utf8").strip()
    temp_html_path = "/tmp/foo.html"
    with open(temp_html_path, "w") as g:
        g.write(html)
    markdown = subprocess.check_output(
        ["pandoc", "-r", "html", "-w", "markdown", temp_html_path]
    )
    issue = re.search("issue(\d{3}).aspx", article_path).group(1)
    issue_file = "{}/issue-{}/_index.md".format(CONTENT_DIR, issue)
    if not (exists(issue_file)):
        print(f"Could not parse premise questions for {issue_file}")
        return
    with open(issue_file, "w") as f:
        f.write(markdown.decode("utf8"))


def parse_article(article_path):
    """Parse article and return a dict with metadata and markdown content."""

    with open(article_path) as f:
        soup = BeautifulSoup(f, "html.parser")

    title_node = soup.select_one(".georgia")
    title = re.sub("\s+", " ", title_node.text)
    author_node = title_node.next_sibling.next_sibling
    author = " ".join(author_node.text.split()[1:])
    date = soup.select("table em")[-1].text
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
    title_date = [
        (i, parse_issue_title_and_date(issue))
        for i, issue in enumerate(issues, start=1)
        if i < 34
    ]

    data = [
        {"number": i, "title": title, "date": date} for i, (title, date) in title_date
    ]
    makedirs(DATA_DIR, exist_ok=True)
    with open(join(DATA_DIR, "issues.json"), "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    return data


def parse_issue_title_and_date(issue_path):
    with open(issue_path) as f:
        soup = BeautifulSoup(f, "html.parser")

    title = re.sub("\s+", " ", soup.select_one("h3").text).strip()
    date = soup.select("table em")[-1].text
    date = parser.parse(date).date().isoformat()
    return " ".join(x.capitalize() for x in title.split()), date


if __name__ == "__main__":
    create_md_content_dir()
    create_issue_index()
    add_premise_questions()
