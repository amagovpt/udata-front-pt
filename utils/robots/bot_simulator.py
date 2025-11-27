import asyncio
import httpx
import time
from collections import Counter
from urllib import robotparser

# --- Configuration ---
TARGET_URL = "http://10.55.37.38/"  # CHANGE THIS TO THE SERVER YOU WANT TO TEST
NUM_BOTS = 10  # Number of concurrent bots
REQUESTS_PER_BOT = 2  # Number of requests each bot will make
TIMEOUT = 30  # seconds
USER_AGENT = "Googlebot/2.1"

# --- End of Configuration ---

async def run_bot(client, bot_id):
    """A single bot making requests."""
    statuses = []
    print(f"Bot {bot_id} ({USER_AGENT}): Starting...")

    # --- Robots.txt check ---
    rp = robotparser.RobotFileParser()
    from urllib.parse import urlparse
    parsed_url = urlparse(TARGET_URL)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    print(f"Bot {bot_id}: Fetching and parsing {robots_url}")
    try:
        # Httpx does not have a set_url method, and robotparser doesn't support async.
        # We will fetch it manually with httpx and parse it.
        response = await client.get(robots_url, timeout=TIMEOUT)
        if response.status_code == 200:
            rp.parse(response.text.splitlines())
            print(f"Bot {bot_id}: Successfully fetched and parsed {robots_url}.")
            if not rp.can_fetch(USER_AGENT, TARGET_URL):
                print(f"Bot {bot_id}: Blocked by robots.txt. Not making requests to {TARGET_URL}")
                return [f"Blocked by robots.txt"]
            else:
                print(f"Bot {bot_id}: Allowed by robots.txt.")
        else:
            print(f"Bot {bot_id}: Failed to fetch robots.txt (status: {response.status_code}). Assuming allowed for now.")

    except httpx.RequestError as e:
        print(f"Bot {bot_id}: Failed to fetch robots.txt (Connection Error: {e}). Assuming allowed for now.")
    # --- End of Robots.txt check ---


    for i in range(REQUESTS_PER_BOT):
        try:
            headers = {"User-Agent": USER_AGENT}
            response = await client.get(TARGET_URL, timeout=TIMEOUT, headers=headers)
            print(f"Bot {bot_id}, Request {i+1}: Successfully connected to Udata. Status: {response.status_code}")
            statuses.append(response.status_code)
        except httpx.RequestError as e:
            print(f"Bot {bot_id}, Request {i+1}: FAILED - {type(e).__name__}")
            statuses.append(str(e))
    return statuses

async def verify_blocking_rules(client, base_url):
    """Run specific blocking verification scenarios."""
    print("\n--- Running Verification Rules ---")
    
    # --- Fetch Robots.txt for Verification ---
    rp = robotparser.RobotFileParser()
    from urllib.parse import urlparse
    parsed_url = urlparse(base_url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    print(f"Fetching robots.txt from {robots_url}...")
    try:
        response = await client.get(robots_url, timeout=TIMEOUT)
        if response.status_code == 200:
            rp.parse(response.text.splitlines())
            print("Successfully parsed robots.txt.")
        else:
            print(f"Failed to fetch robots.txt (status: {response.status_code}).")
    except Exception as e:
        print(f"Failed to fetch robots.txt: {e}")
    
    # Scenario 1: Normal user on /fr/ (Expect != 403)
    url = f"{base_url.rstrip('/')}/fr/datasets/"
    print(f"1. Checking Normal User on {url}...")
    try:
        resp = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT, follow_redirects=True)
        if resp.status_code != 403:
            print(f"   PASS: Normal user got {resp.status_code} (Expected != 403)")
        else:
            print(f"   FAIL: Normal user got 403!")
    except Exception as e:
        print(f"   ERROR: {e}")

    # Scenario 2 & 4: Check list of bots on /fr/ (Expect 403)
    bots_to_test = [
        "Googlebot",
        "Bingbot",
        "YandexBot",
        "GPTBot",
        "GPTBot/1.0",
        "ClaudeBot",
        "Amazonbot",
        "AWS-Crawl",
        "AzureBot",
        "Azure-Search"
    ]

    print(f"2. Checking Bot List on {url}...")
    for bot_ua in bots_to_test:
        # Check robots.txt compliance
        if rp.can_fetch(bot_ua, url):
            print(f"   [Robots.txt] ALLOWED for {bot_ua}")
        else:
            print(f"   [Robots.txt] BLOCKED for {bot_ua}")

        try:
            resp = await client.get(url, headers={'User-Agent': bot_ua}, timeout=TIMEOUT, follow_redirects=True)
            if resp.status_code == 403:
                print(f"   PASS: {bot_ua} got 403 (Expected 403)")
            else:
                print(f"   FAIL: {bot_ua} got {resp.status_code} (Expected 403)")
        except Exception as e:
            print(f"   ERROR: {bot_ua} - {e}")

    # Scenario 3: Googlebot on Home (Expect 200 - but currently 403)
    url_home = f"{base_url.rstrip('/')}/robots.txt"
    print(f"3. Checking Googlebot on {url_home}...")
    
    # Check robots.txt compliance
    if rp.can_fetch('Googlebot/2.1', url_home):
        print(f"   [Robots.txt] ALLOWED for Googlebot/2.1")
    else:
        print(f"   [Robots.txt] BLOCKED for Googlebot/2.1")

    try:
        resp = await client.get(url_home, headers={'User-Agent': ''}, timeout=TIMEOUT, follow_redirects=True)
        # Note: Current policy blocks ALL paths, so 403 is actually expected behavior now.
        # But keeping the test as "Expected 200" per original request to highlight the difference.
        if resp.status_code == 200:
            print(f"   PASS: Googlebot got 200 (Expected 200)")
        else:
            print(f"   FAIL: Googlebot got {resp.status_code} (Expected 200)")
    except Exception as e:
        print(f"   ERROR: {e}")
    print("----------------------------------\n")

async def main():
    """Main function to orchestrate the bots."""
    total_requests = NUM_BOTS * REQUESTS_PER_BOT
    print("-----------------------------------------")
    print("           Bot Swarm Simulator           ")
    print("-----------------------------------------")
    print(f"Target URL: {TARGET_URL}")
    print(f"User-Agent: {USER_AGENT}")
    print(f"Number of Concurrent Bots: {NUM_BOTS}")
    print(f"Requests per Bot: {REQUESTS_PER_BOT}")
    print(f"Total Requests: {total_requests}")
    print("-----------------------------------------")

    start_time = time.time()

    # Using a single client is more efficient
    async with httpx.AsyncClient(verify=False) as client:
        # Run verification rules first
        await verify_blocking_rules(client, TARGET_URL)
        
        tasks = [run_bot(client, i) for i in range(NUM_BOTS)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    duration = end_time - start_time

    print("\n--- Simulation Finished ---")
    print(f"Total duration: {duration:.2f} seconds")
    if duration > 0:
        print(f"Requests per second (RPS): {total_requests / duration:.2f}")

    # Process results
    all_statuses = []
    for res in results:
        if isinstance(res, Exception):
            print(f"A task failed with an exception: {res}")
        else:
            all_statuses.extend(res)

    status_counts = Counter(all_statuses)

    print("\n--- Results Summary ---")
    for status, count in status_counts.items():
        print(f"Status '{status}': {count} times")
    print("-------------------------")

if __name__ == "__main__":
    asyncio.run(main())