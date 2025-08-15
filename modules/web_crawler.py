import requests, logging
from bs4 import BeautifulSoup

def crawl(payload):
    """
    Crawls a given URL and returns all found hyperlinks.
    payload example: {"url": "https://example.com"}
    """
    url = payload.get("url")
    if not url:
        return {"status": "error", "message": "No URL provided"}

    logging.info(f"🌐 Crawling: {url}")
    try:
        r = requests.get(url, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True)]
        return {"status": "ok", "links": links, "count": len(links)}
    except Exception as e:
        logging.error(f"Crawler error: {str(e)}")
        return {"status": "error", "message": str(e)}
