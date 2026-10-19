from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import random


def human_like_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))


def scrape_topic_page(driver, indexed_topic, topic_name, topic_url, conn, retries=3):
    """Scrape all pages of a single topic, automatic pagination."""
    wait = WebDriverWait(driver, 20)
    cur = conn.cursor()
    href = topic_url
    page_count = 1
    if topic_url[-1].isdecimal():
        topic_url, page_count = topic_url.split('_')
        page_count = int(page_count)

    try:
        while True:
            try:
                print(f"\t\t\t🔹 Page {page_count}")
                driver.get(href)
                human_like_delay(2, 5)

                wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".grid-item")))

                soup = BeautifulSoup(driver.page_source, "html.parser")
                quotes = soup.select(".grid-item")

                for rec in quotes:
                    quote_div = rec.select_one('a[title="view quote"] div')
                    if not quote_div:
                        continue
                    quote = quote_div.get_text(strip=True)
                    author_elem = rec.select_one('a[title="view author"]')
                    author = author_elem.get_text(
                        strip=True) if author_elem else "Unknown"

                    cur.execute(
                        "INSERT OR IGNORE INTO quotes (topic, author, quote) VALUES (?, ?, ?)",
                        (topic_name, author, quote)
                    )

                # Pagination check
                try:
                    next_link = driver.find_element(By.LINK_TEXT, "Next")
                    if "disabled" in next_link.get_attribute("class"):
                        print(
                            f"\t\t🔹 Reached last page of topic {topic_name}.")
                        break
                    href = next_link.get_attribute("href")
                    page_count += 1
                    human_like_delay(2, 4)
                except NoSuchElementException:
                    print(f"\t\t🔹 Reached last page of topic {topic_name}.")
                    break

            except TimeoutException:
                if retries > 0:
                    print(
                        f"\t\t\t⚠️ Timeout on page {page_count}, retrying...")
                    retries -= 1
                    human_like_delay(5, 10)
                    continue  # retry same page
                else:
                    print(
                        f"\t\t❌ Skipping {topic_name} after repeated timeouts.")
                    cur.execute(
                        "INSERT or ignore INTO errors (stage, indexed_t, topic, url, error_msg) VALUES (?, ?, ?, ?)",
                        ("page", indexed_topic, topic_name, f'{topic_url}_{page_count}' if page_count > 1 else topic_url,
                         "Timeout or bot verification")
                    )
                    conn.commit()
                    return False
            except Exception as e:
                print(f"\t\t❌ Unexpected error in page {page_count}: {e}")
                cur.execute(
                    "INSERT INTO errors (stage, indexed_t, topic, url, error_msg) VALUES (?, ?, ?, ?)",
                    ("page", indexed_topic, topic_name,
                     f'{topic_url}_{page_count}' if page_count > 1 else topic_url, str(e))
                )
                conn.commit()
                return False

        # ✅ Success: reached end of topic pages
        cur.execute(
            "INSERT OR IGNORE INTO topics (topic, pages) VALUES (?, ?)",
            (topic_name, page_count)
        )

        cur.execute(
            "update errors set handled = 1 where indexed_t = ? and topic = ?", (
                indexed_topic, topic_name)
        )
        conn.commit()
        # print(f"✅ Finished scraping topic: {topic_name}")
        return True

    except Exception as e:
        # outer fallback — if anything truly breaks the loop
        print(f"🔥 Critical failure in topic {topic_name}: {e}")
        cur.execute(
            "INSERT INTO errors (stage, indexed_t, topic, url, error_msg) VALUES (?, ?, ?, ?)",
            ("critical", indexed_topic, topic_name,
             f'{topic_url}_{page_count}' if page_count > 1 else topic_url, str(e))
        )
        conn.commit()
        return False
