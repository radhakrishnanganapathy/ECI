import json
import time
import random
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_eci_selenium():
    # Setup selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Stealth-ish headers
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print("Initializing WebDriver...")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception as e:
        print(f"Failed to initialize driver: {e}")
        return []

    results = []
    page_num = 1
    
    target_url = "https://affidavit.eci.gov.in/CandidateCustomFilter?electionType=32-AC-GENERAL-3-60&election=32-AC-GENERAL-3-60&states=U07&submitName=100&page=1"

    print(f"Navigating to: {target_url}")
    try:
        driver.get(target_url)
        # Wait for data or card elements
        WebDriverWait(driver, 45).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h4.bg-blu, .card, table#data-tab, .row")))
    except Exception as e:
        print(f"Initial page load failed or took too long: {e}")
        driver.save_screenshot("error_screenshot.png")
        driver.quit()
        return []

    while True:
        print(f"Scraping page {page_num}...")
        
        # Human-like delay
        time.sleep(random.uniform(3, 5))
        
        # Scroll to bottom to ensure any dynamic content/images load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Identify rows - could be inside a table or card grid
        rows = soup.select("#data-tab tbody tr")
        if not rows:
             # Fallback: check for .card blocks
             rows = soup.select(".card")
        
        if not rows:
            print(f"Attempting alternative layout for page {page_num}...")
            # Try finding any row containing "Party :"
            rows = [el for el in soup.find_all(True) if "Party :" in el.get_text() and el.name in ['div', 'tr']]

        if not rows:
            print("No candidate indicators found. Ending scrape.")
            break
            
        page_results = []
        for row in rows:
            text = row.get_text(separator=' ', strip=True)
            # Skip noise or headers
            if "LIST OF CANDIDATES" in text or len(text) < 50:
                continue
                
            # Candidate name is often in h4.bg-blu or a similar header
            name_el = row.select_one("h4.bg-blu")
            if not name_el:
                name_el = row.select_one("h1, h2, h3, h4, h5, b, strong")
            
            name = name_el.get_text(strip=True) if name_el else "N/A"
            
            # Additional cleanup for name if it picks up page titles
            if name == "N/A" or name.lower().startswith("election") or name.lower() == "list of candidates":
                # Find the longest line in the row text before "Party :" as a fallback
                parts = text.split("Party :")
                if parts:
                    name_parts = parts[0].split("\n")
                    name = max(name_parts, key=len).strip() if name_parts else "N/A"

            if name == "N/A" or "Election" in name:
                continue

            def extract_val(label):
                # Search for label followed by a colon and captured value 
                # Stop at common delimiters or the 'View more' button text
                pattern = rf"{label}\s*:\s*(.*?)(?=\s*\||Party|Status|State|Constituency|View more|$|\n)"
                match = re.search(pattern, text, re.IGNORECASE)
                return match.group(1).strip() if match else "N/A"

            view_more_link = row.select_one('a[href*="show-profile"]')
            
            candidate_url = "N/A"
            if view_more_link and 'href' in view_more_link.attrs:
                 href = view_more_link['href']
                 if href.startswith("/"):
                     candidate_url = "https://affidavit.eci.gov.in" + href
                 else:
                     candidate_url = href

            page_results.append({
                "name": name,
                "party": extract_val("Party"),
                "state": extract_val("State"),
                "status": extract_val("Status"),
                "constituency": extract_val("Constituency"),
                "view_more_link": candidate_url,
                "years": 2026,
                "Election": "Assembely election"
            })
        
        # Deduplicate names on the same page
        unique_page_results = []
        seen_names = set()
        for c in page_results:
            if c['name'] not in seen_names and c['name'] != "N/A":
                unique_page_results.append(c)
                seen_names.add(c['name'])

        print(f"Found {len(unique_page_results)} unique candidates on page {page_num}.")
        results.extend(unique_page_results)
        
        # Pagination handling
        try:
            # Look for the link that contains "Next" or the » symbol
            next_btn = None
            try:
                # Direct search for rel='next' or 'Next' text
                next_btn = driver.find_element(By.XPATH, "//a[contains(., 'Next') or contains(., '»') or @rel='next']")
            except:
                pass

            if next_btn:
                # Debugging info
                parent_li = None
                try:
                    parent_li = next_btn.find_element(By.XPATH, "./parent::li")
                except:
                    pass
                
                li_class = parent_li.get_attribute("class") if parent_li else "N/A"
                btn_class = next_btn.get_attribute("class") if next_btn else "N/A"
                print(f"DEBUG: Next button found. LI class: {li_class}, Btn class: {btn_class}, Displayed: {next_btn.is_displayed()}")

                is_disabled = "disabled" in (li_class or "").lower() or "disabled" in (btn_class or "").lower()

                if not is_disabled:
                    print(f"Moving to Next Page (Page {page_num + 1})...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_btn)
                    page_num += 1
                    # Robust wait: wait for the results count or names to change
                    time.sleep(random.uniform(5, 8))
                else:
                    print("Next button is disabled. Scrape complete.")
                    break
            else:
                print("No 'Next' button found on this page. Scrape complete.")
                break
        except Exception as e:
            print(f"Pagination error: {e}. Stopping.")
            break

    driver.quit()
    return results

if __name__ == "__main__":
    print("Starting Selenium + BeautifulSoup ECI Scraper...")
    scraped_data = scrape_eci_selenium()
    
    if scraped_data:
        output_file = "eci_candidates.json"
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=4, ensure_ascii=False)
        print(f"SUCCESS: Saved {len(scraped_data)} candidates to {output_file}")
    else:
        print("FAILED: No data extracted.")
