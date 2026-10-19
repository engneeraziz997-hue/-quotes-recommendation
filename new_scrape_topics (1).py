# run_file.py
import time
import random
from new_scrape_pages import scrape_topic_page
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re


def human_like_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))


def get_topic_links(driver, start_letter=None, topic_index=None, url=None):
    """Get topic links from BrainyQuote for a letter or a topic index page."""
    wait = WebDriverWait(driver, 20)
    topics = []

    if start_letter:
        driver.get("https://www.brainyquote.com")
        human_like_delay(2, 4)

        topics_url = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Topics"))
        )
        driver.get(topics_url.get_attribute("href"))
        time.sleep(random.uniform(2, 4))

        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a.topicIndexChicklet")))
        topic_elements = driver.find_elements(
            By.CSS_SELECTOR, "a.topicIndexChicklet")

        for el in topic_elements:
            try:
                name_el = el.find_element(
                    By.CSS_SELECTOR, "span.topicContentName")
                name = name_el.text.strip()
            except:
                name = el.text.strip()

            if not name.lower().startswith(start_letter.lower()):
                continue

            href = el.get_attribute("href") or ""
            if not href:
                onclick = el.get_attribute("onclick") or ""
                m = re.search(r"['\"](/topics/[^'\"]+)['\"]", onclick)
                if m:
                    href = "https://www.brainyquote.com" + m.group(1)
            if href:
                topics.append((name, href))
        print(
            f"✅ Found {len(topics)} topics starting with '{start_letter.upper()}'")

    elif url:
        driver.get(url)
        human_like_delay(2, 4)
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "span.authorContentName")))
        topic_elements = driver.find_elements(
            By.CSS_SELECTOR, "span.authorContentName")
        link = None
        for el in topic_elements:
            try:
                link = el.find_element(By.XPATH, "..")
                name = el.text.strip()
            except:
                name = el.text.strip()
            href = link.get_attribute("href") or ""
            if not href:
                onclick = el.get_attribute("onclick") or ""
                m = re.search(r"['\"](/topics/[^'\"]+)['\"]", onclick)
                if m:
                    href = "https://www.brainyquote.com" + m.group(1)
            if href:
                topics.append((topic_index, name, href))

    return topics


def scrape_topics(driver, topic_index, topics, conn):
    """Scrape multiple topics under a topic index."""
    cur = conn.cursor()
    for _, topic, url in topics:
        try:
            cur.execute("INSERT OR IGNORE INTO indexed_topics (indexed_t, topic) VALUES (?, ?)",
                        (topic_index, topic))
            print(f"\t\t🚀 Scraping topic: {topic}")
            scrape_topic_page(driver, topic_index, topic, url, conn)
        except Exception as e:
            print(f"\t\t❌ Error on {topic}: {e}")
            cur.execute("INSERT INTO errors (stage, indexed_t, topic, url, error_msg) VALUES (?, ?, ?, ?, ?)",
                        ("topic", topic_index, topic, url, str(e)))
        finally:
            conn.commit()
        human_like_delay(3, 6)
