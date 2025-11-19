from bs4 import BeautifulSoup
from notice_scrape import fetch_page_with_retries, get_complete_link, BASE_URL

ANNOUNCEMENT_URL = BASE_URL + "AllRecord"


def announcement_scrape():
    """Scrape MMMUT AllRecord announcements (first 10 items)."""

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

    html = fetch_page_with_retries(ANNOUNCEMENT_URL, headers)
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"id": "ContentPlaceHolder2_GridView1"})
    if not table:
        raise Exception("Announcement table not found. Page structure may have changed.")

    announcements = []
    rows = table.find_all("tr")

    for row in rows:
        # Skip pagination rows
        if row.get("class") and "pagination-ys" in row.get("class"):
            continue

        # Find the nested table within the row
        nested_table = row.find("table")
        if not nested_table:
            continue

        # Find the title link in the first row of nested table
        title_link = nested_table.find("a", href=lambda x: x and "News_content" in x)
        if not title_link:
            continue

        title = title_link.get_text(strip=True)
        if not title:
            continue

        # Find the download link in the second row (HyperLink2_X pattern)
        download_link = nested_table.find("a", id=lambda x: x and "HyperLink2_" in x)
        if not download_link:
            # Fallback: use the title link href
            href = title_link.get("href")
        else:
            href = download_link.get("href")

        if not href or href == "#" or "javascript:" in href:
            continue

        announcements.append({
            "title": title,
            "link": get_complete_link(href)
        })

        if len(announcements) >= 10:
            break

    if not announcements:
        raise Exception("No valid announcements found.")

    return {
        "announcements": announcements,
    }

