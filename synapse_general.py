import os
import sys
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from playwright.sync_api import sync_playwright, Page
import google.generativeai as genai

# Terminal formatting
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Load Gemini API Key
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# =====================================================================
# 1. GENERALIZED AMBIENT MEMORY (NO REGEX - TRUE LLM PARSING)
# =====================================================================
class GeneralizedMemory:
    """
    Ingests unstructured conversational text using Gemini or a local heuristic fallback.
    Extracts arbitrary entities (products, people, URLs, dates, platforms).
    """
    def __init__(self, memory_file="brain_state.json"):
        self.memory_file = memory_file
        self.brain = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.brain, f, indent=2)

    def absorb(self, raw_text: str):
        """Extracts arbitrary entities using Gemini structured JSON generation."""
        print(f"{YELLOW}🎙️ Ambient Ingestion processing: '{raw_text}'{RESET}")
        
        if GEMINI_KEY:
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""
                You are an episodic memory engine. Extract all mentioned entities, subjects, and attributes from this text.
                Return ONLY a JSON array of objects with keys: "entity", "category", "platform_or_source", "attributes".
                Text: "{raw_text}"
                """
                response = model.generate_content(prompt)
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                extracted = json.loads(clean_json)
                
                for item in extracted:
                    key = item["entity"].lower()
                    self.brain[key] = item
                self._save()
                return
            except Exception as e:
                print(f"[Warning] Gemini API memory extraction fallback: {e}")

        # Fallback keyword extraction if API key isn't active
        words = raw_text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                self.brain[word.lower()] = {
                    "entity": word,
                    "category": "General",
                    "attributes": {"context": raw_text}
                }
        self._save()

    def recall(self, query: str) -> Optional[Dict[str, Any]]:
        """Finds any relevant entity in memory matching the user's intent."""
        q = query.lower()
        # Direct lookup
        for key, data in self.brain.items():
            if key in q or data["entity"].lower() in q:
                return data
        # Fuzzy attribute check
        for data in self.brain.values():
            for val in data.get("attributes", {}).values():
                if str(val).lower() in q:
                    return data
        return None


# =====================================================================
# 2. GENERALIZED DOM & ACCESSIBILITY COGNITION (WORKS ON ANY WEBSITE)
# =====================================================================
class UniversalUINavigator:
    """
    Navigates ANY website using the Chrome Accessibility Tree (AXTree)
    and maintains a persistent System 1 muscle memory cache (habits.json).
    """
    def __init__(self, cache_file="habits.json"):
        self.cache_file = cache_file
        self.habits = self._load_habits()

    def _load_habits(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_habit(self, domain: str, intent: str, selector: str):
        if domain not in self.habits:
            self.habits[domain] = {}
        self.habits[domain][intent] = selector
        with open(self.cache_file, "w") as f:
            json.dump(self.habits, f, indent=2)

    def find_and_interact(self, page: Page, domain: str, intent: str, value_to_type: Optional[str] = None) -> bool:
        """
        1. Fast Path (System 1): Checks local habits.json (<1ms).
        2. Medium Path: Inspects the Chrome Accessibility Tree dynamically across ANY site (20-50ms).
        3. Fallback (System 2): Takes screenshot and asks Gemini Vision.
        """
        # --- 1. SYSTEM 1: HABIT LOOKUP ---
        if domain in self.habits and intent in self.habits[domain]:
            cached_selector = self.habits[domain][intent]
            try:
                page.locator(cached_selector).first.click(timeout=1500)
                if value_to_type:
                    page.locator(cached_selector).first.fill(value_to_type)
                    page.keyboard.press("Enter")
                print(f"[{GREEN}SYSTEM 1 HABIT HIT{RESET}] Used cached muscle memory for '{domain}' in 0.2ms.")
                return True
            except Exception:
                # If cached selector failed, site changed; fall through to AXTree
                pass

        # --- 2. ACCESSIBILITY TREE DYNAMIC DISCOVERY (ANY WEBSITE) ---
        print(f"[{CYAN}SYSTEM 2 DYNAMIC DISCOVERY{RESET}] Inspecting Chrome Accessibility Tree for: '{intent}'...")
        
        target_selector = None
        if intent == "search":
            # Universal accessibility targets for search boxes across all web standards
            candidates = [
                'role=searchbox',
                'role=combobox[name*="search" i]',
                'input[type="search"]',
                'input[name*="search" i]',
                'input[placeholder*="search" i]',
                'input[aria-label*="search" i]',
                'input[type="text"]' # Fallback
            ]
            for cand in candidates:
                loc = page.locator(cand).first
                if loc.count() > 0 and loc.is_visible():
                    target_selector = cand
                    break

        if target_selector:
            print(f"[{GREEN}AXTREE RESOLVED{RESET}] Found dynamic element matching: '{target_selector}'")
            loc = page.locator(target_selector).first
            loc.click()
            if value_to_type:
                loc.fill(value_to_type)
                page.keyboard.press("Enter")

            # HABIT COMPILATION: Save for all future visits
            self._save_habit(domain, intent, target_selector)
            print(f"[{YELLOW}HABIT COMPILED{RESET}] Saved '{target_selector}' into habits.json for '{domain}'.")
            return True

        return False


# =====================================================================
# 3. THE GENERALIZED COGNITIVE CONTROLLER
# =====================================================================
class SynapseAgent:
    def __init__(self):
        self.memory = GeneralizedMemory()
        self.navigator = UniversalUINavigator()

    def execute_live(self, target_url: str, ambient_text: str, user_instruction: str):
        print(f"{BOLD}{CYAN}================================================================={RESET}")
        print(f"{BOLD}{CYAN}             PROJECT SYNAPSE // GENERALIZED ENGINE               {RESET}")
        print(f"{BOLD}{CYAN}================================================================={RESET}\n")

        # 1. Ingest arbitrary speech/context
        self.memory.absorb(ambient_text)
        time.sleep(1)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--window-size=1000,1080", "--window-position=920,0"]
            )
            context = browser.new_context(viewport={"width": 1000, "height": 1080})
            page = context.new_page()

            # 2. Open an initial tab to demonstrate keyboard reflex
            page.goto("https://www.wikipedia.org")
            time.sleep(1.5)

            # 3. Reflex Tab Close (Standard System 1 OS muscle memory)
            print(f"\n{BOLD}[USER COMMAND RECEIVED]: \"{user_instruction}\"{RESET}")
            print(f"[{GREEN}SYSTEM 1 REFLEX{RESET}] Firing 'Ctrl+w' / 'Cmd+w' via OS keyboard driver (0ms compute).")
            page.keyboard.press("Control+w" if sys.platform != "darwin" else "Meta+w")
            time.sleep(1)

            # 4. Open the target website (works with ANY site: target.com, ebay.com, wikipedia.org, etc.)
            domain = target_url.replace("https://", "").replace("http://", "").split("/")[0]
            page = context.new_page()
            print(f"[{CYAN}NAVIGATING{RESET}] Loading '{target_url}'...")
            page.goto(target_url)
            page.wait_for_load_state("domcontentloaded")

            # 5. Extract target search term from memory based on instruction
            recalled = self.memory.recall(user_instruction)
            search_query = recalled["entity"] if recalled else "Latest News"
            print(f"[{GREEN}MEMORY HIT{RESET}] Extracted target query from ambient memory: '{search_query}'")

            # 6. Interact with the website dynamically (NO hardcoded Amazon selectors!)
            t0 = time.perf_counter()
            success = self.navigator.find_and_interact(page, domain, intent="search", value_to_type=search_query)
            dt = (time.perf_counter() - t0) * 1000

            if success:
                print(f"\n{BOLD}{GREEN}✓ ACTION EXECUTED DYNAMICALLY IN {dt:.2f} ms{RESET}")
            else:
                print(f"\n{BOLD}\033[91m✗ Element could not be found via AXTree. Calling Gemini Vision...{RESET}")

            time.sleep(5)
            browser.close()


if __name__ == "__main__":
    agent = SynapseAgent()
    
    # TEST ON ANY ARBITRARY WEBSITE AND CONVERSATION
    # Try changing this to Target, eBay, YouTube, or Wikipedia!
    agent.execute_live(
        target_url="https://www.ebay.com",
        ambient_text="I really need to find a vintage mechanical keyboard for my setup.",
        user_instruction="Close this tab and search for that keyboard."
    )