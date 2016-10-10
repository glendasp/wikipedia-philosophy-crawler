import sys
from crawler import crawl


def main():
    if len(sys.argv) > 1:
        article = ' '.join(sys.argv[1:])
        crawl(article)
    else:
        article = None

    crawl(article, print)


if __name__ == '__main__':
    main()
