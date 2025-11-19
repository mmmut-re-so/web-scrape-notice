from bs4 import BeautifulSoup
import requests
import time


BASE_URL = "https://mmmut.ac.in/"
NOTICE_URL = BASE_URL + "ExaminationSchedule"


def fetch_page_with_retries(url, headers, max_retries=3, timeout=30):
    """Fetch a webpage with retry + exponential backoff."""
    session = requests.Session()

    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
                continue
            raise Exception(f"Failed after {max_retries} attempts: {e}")

        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    raise Exception("Failed to fetch the webpage.")


def get_complete_link(href: str) -> str:
    """Return a fully qualified link."""
    if href.startswith("http"):
        return href
    return BASE_URL + href.lstrip("/")


def notice_scrape():
    """Scrape MMMUT ExaminationSchedule notices (first 10 items)."""

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    html = fetch_page_with_retries(NOTICE_URL, headers)
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"id": "ContentPlaceHolder2_ContentPlaceHolder3_GridView1"})
    if not table:
        raise Exception("Notice table not found. Page structure may have changed.")

    notices = []
    rows = table.find_all("tr")

    for row in rows:
        # Skip pagination rows
        if row.get("class") and "pagination-ys" in row.get("class"):
            continue
            
        link_tag = row.find("a", class_="float-right text-danger")
        if not link_tag:
            continue

        href = link_tag.get("href")
        if not href or href == "#" or "javascript:" in href:
            continue

        title_tag = row.find("span", id=lambda x: x and "Label1_" in x) or row.find("span")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled Notice"

        notices.append({
            "title": title,
            "link": get_complete_link(href)
        })

        if len(notices) >= 10:
            break

    if not notices:
        raise Exception("No valid notices found.")

    return {
        "links_list": [n["link"] for n in notices],
        "link_titles": [n["title"] for n in notices],
        "notices": notices,
    }


