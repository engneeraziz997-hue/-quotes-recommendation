import sqlite3
import time
import random
from new_browser_utils import create_driver
from new_scrape_topics import get_topic_links, scrape_topics


def get_topic_of_index(driver, start_letter=None):
    """Fetch topics starting with a given letter from main topics page."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    wait = WebDriverWait(driver, 15)
    main_url = "https://www.brainyquote.com"
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    driver.get(main_url)
    time.sleep(random.uniform(2, 4))  # small buffer before elements appear

    topics_url = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Topics"))
    )
    driver.get(topics_url.get_attribute("href"))
    time.sleep(random.uniform(2, 4))

    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "h2 + .bq_fl a")))
    driver.minimize_window()

    topic_elements = driver.find_elements(By.CSS_SELECTOR, "h2 + .bq_fl a")
    topics = []
    for el in topic_elements:
        name = el.text.strip()
        if not name.lower().startswith(start_letter.lower()):
            continue
        href = el.get_attribute("href")
        topics.append((name, href))
    return topics


def scrape_indexed_topics(driver, letter, indexed_topics, conn):
    """Scrape all topics for a given letter and insert into DB."""
    cur = conn.cursor()

    for name, url in indexed_topics:
        cur.execute(
            "INSERT OR IGNORE INTO lett_of_ind_tops (letter, indexed_t) VALUES (?, ?)",
            (letter.upper(), name)
        )
        try:
            print(f"\t🚀 Scraping topics of index: {name.title()}")
            # Get subtopics under this indexed topic
            topics = get_topic_links(driver, topic_index=name, url=url)

            # existing_topics = [row[0] for row in cur.execute(
            #     "SELECT topic FROM indexed_topics where indexed_t = ?", (name,)
            # ).fetchall()]
            # topics = [topic for topic in topics if topic[1].lower()
            #           not in existing_topics]

            topics = [elem for elem in topics if elem[1] not in
                      [row[0] for row in cur.execute("""SELECT topic FROM indexed_topics
            where indexed_t = ?
            And topic not in
            (SELECT topic from errors where topic is not null and handled = 0)""", (name,)).fetchall()]]
            print(f"\t✅ Found {len(topics)} topics of index {name.title()}")

            cur.execute(
                "INSERT OR IGNORE INTO indexed_topics_info (name, num_of_topics) VALUES (?, ?)",
                (name, len(topics))
            )
            scrape_topics(driver, name, topics, conn)
        except Exception as e:
            print(f"\t❌ Error on {name}: {e}")
            cur.execute("""
                INSERT INTO errors (stage, letter, indexed_t, url, error_msg)
                VALUES (?, ?, ?, ?, ?)
            """, ("topic_index", letter, name, url, str(e)))
        finally:
            conn.commit()
        # Random delay before next topic
        time.sleep(random.uniform(10, 20))


# ------------------- Main -------------------
if __name__ == "__main__":
    letter = 'c'
    driver = create_driver()
    conn = sqlite3.connect("quotes.db", timeout=30)
    cur = conn.cursor()

    try:
        print(f"\n🚀 Scraping indexed topics of letter: {letter.upper()}")
        indexed_topics = get_topic_of_index(driver, start_letter=letter)
        print(
            f"✅ Found {len(indexed_topics)} indexed topics of letter {letter.upper()}")

        cur.execute(
            "INSERT OR IGNORE INTO letter_info (letter, num_of_ind_tops) VALUES (?, ?)",
            (letter.upper(), len(indexed_topics))
        )

        indexed_topics = [elem for elem in indexed_topics if elem[0] not in
                          [row[0] for row in cur.execute("""select indexed_t from lett_of_ind_tops
            where letter = ?
            And indexed_t not in (SELECT indexed_t from errors where indexed_t is not null and handled = 0);
            """, (letter.upper(),)).fetchall()]]

        scrape_indexed_topics(driver, letter, indexed_topics, conn)
        print("\n🎉 All scraping complete. Data saved to quotes.db.")
    finally:
        conn.commit()
        driver.quit()
