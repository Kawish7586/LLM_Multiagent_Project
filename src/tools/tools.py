import os
import re
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from readability import Document
from tavily import TavilyClient
import trafilatura

# Load environment varibale
load_dotenv()

# Initialize Tavily Search
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("Tavily_API_KEY environment varibale is not set.")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


@tool

def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information on a topic.
    Returns Titles, URLs, and a snippet of the content.
    """
    try:
        results = tavily.search(query = query,max_result = 5)
        out = []

        for r in results.get('results', []):
            out.append(
                f"Title: {re.get('title','No Title')}\n"
                f"URL: {re.get('url','No URL')}\n"
                f"Snippet: {re.get('content','')[:300]}\n"
            )

            return "\n-----------\n".join(out) if out else "No results found."

    except Exception as e:
        return f"Error during web search: {str(e)}"

@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability
    """
    headers = {
        "User-Agent":( "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com"
        }
    try:
        #--- Fetch page-------------------------------------------------------------
        response = requests.get(url, headers=headers,timeout=15)
        response.raise_for_status()
        html = response.text

        # ----------------------------------------------------------------------------
        # Strategy 1: trafilatura (BEST for aticle/blogs)
        # ----------------------------------------------------------------------------

        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)

        if extracted and len(extracted.strip()) > 200:
            return re.sub(r'\s+', ' ', extracted)[:5000]

        # Define elements to remove from fallback strategy
        decompose_tags = ['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']

        # ----------------------------------------------------------------------------
        # Strategy 2: readability-lxml
        # ----------------------------------------------------------------------------

        doc = Document(html)
        clean_html = doc.summary()
        soup = BeautifulSoup(clean_html, 'html.parser')

        for tag in soup(decompose_tags):
            tag.decompose()

        text = soup.get_text(separator=' ', strip=True)

        if text and len(text.strip()) > 200:
            return re.sub(r'\s+', ' ', text)[:5000]
        # ----------------------------------------------------------------------------
        # Strategy 2: readability-lxml
        # ----------------------------------------------------------------------------

        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup(decompose_tags):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]
        
        return "Could not extract meaningful content from the page."

    except requests.exceptions.Timeout:
        return "Request timed out while trying to access the URL."
    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {str(e)}"
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
