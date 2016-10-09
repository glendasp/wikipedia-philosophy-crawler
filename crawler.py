"""A bot that crawls through Wikipedia until it reaches Philosophy."""

import sys
import wikipedia
from wikipedia.exceptions import DisambiguationError
from bs4 import BeautifulSoup


class NextArticleNotFound(Exception):
    """Raised when the next article cannot be found."""


# Context manager for temporarily redirecting stderr to nowhere.
# http://stackoverflow.com/a/6796752
class IgnoreStderr:
    def __enter__(self):
        self.old_stderr = sys.stderr
        self.old_stderr.flush()
        sys.stderr = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self.old_stderr


def _is_good_link(link):
    text = link.text.replace(' ', '')
    text = text.replace('-', '')

    if not text.isalpha():
        return False
    if text[:1].isupper():
        return False
    for sibling in link.previous_siblings:
        sibling_string = str(sibling)
        # Check if link is inside parentheses
        if sibling_string.count(')') > 0:
            return True
        if sibling_string.count('(') > sibling_string.count(')'):
            return False

    return True


def _find_next_article(page, link_num=0):
    soup = BeautifulSoup(page.html(), 'html.parser')
    links = [l for l in soup.select('p > a') if _is_good_link(l)]

    try:
        return links[link_num].get('title')
    except IndexError:
        raise NextArticleNotFound


def crawl(article=None, callback=None):
    """Crawl from an article to Philosophy.

    Args:
        article (str, optional): An optional article title to start at.  Start
            at a random article if no article is provided.
        callback (func, optional): An optional function that is called whenever
            the crawler reaches an article.

    Returns:
        A list of article titles in the order that the crawler went through.

    """

    if article is None:
        article = wikipedia.random()

    visited_articles = list()
    while article not in visited_articles:
        visited_articles.append(article)
        if callback is not None:
            callback(article)

        if article.lower() == 'philosophy':
            break

        try:
            # The wikipedia package dumps BeautifulSoup warnings to stderr
            # when a DisambiguationError is raised.  The warnings don't
            # affect us, so we can ignore them and prevent our crawler from
            # cluttering up the console.
            with IgnoreStderr():
                page = wikipedia.page(article)

            article = _find_next_article(page)
        except DisambiguationError as e:
            article = e.options[0]
            continue
        except NextArticleNotFound:
            break

    return visited_articles
