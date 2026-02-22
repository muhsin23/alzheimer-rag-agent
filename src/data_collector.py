"""
Data collection module for Alzheimer's disease research articles.
Collects articles from PubMed and bioRxiv APIs.
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import requests
from urllib.parse import quote
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ArticleCollector:
    """Collects scientific articles from various sources."""
    
    def __init__(self, output_dir: str = "data/raw"):
        """
        Initialize the article collector.
        
        Args:
            output_dir: Directory to save collected articles
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # PubMed E-utilities base URL
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        # bioRxiv base URL
        self.biorxiv_base = "https://api.biorxiv.org/"
        
    def search_pubmed(self, query: str, max_results: int = 50) -> List[str]:
        """
        Search PubMed for articles using E-utilities.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
        """
        logger.info(f"Searching PubMed for: {query}")
        
        # First, get the list of PMIDs
        search_url = f"{self.pubmed_base}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pmids = data['esearchresult']['idlist']
            
            logger.info(f"Found {len(pmids)} articles in PubMed")
            return pmids
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    def fetch_pubmed_details(self, pmid: str) -> Optional[Dict]:
        """
        Fetch detailed information for a PubMed article.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with article details
        """
        try:
            # Fetch article details
            fetch_url = f"{self.pubmed_base}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse XML response using ElementTree
            root = ET.fromstring(response.content)
            
            # Find the first PubmedArticle
            article = root.find('.//PubmedArticle')
            if article is None:
                return None
            
            # Get title
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "No title"
            
            # Get abstract
            abstract_elem = article.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else "No abstract"
            
            # Get authors
            authors = []
            for author in article.findall('.//Author'):
                last_name = author.find('LastName')
                fore_name = author.find('ForeName')
                if last_name is not None and fore_name is not None:
                    authors.append(f"{last_name.text} {fore_name.text}")
            
            # Get journal
            journal_elem = article.find('.//Title')
            journal = journal_elem.text if journal_elem is not None else "Unknown"
            
            # Get publication date
            pub_date = "Unknown"
            pub_date_elem = article.find('.//PubDate')
            if pub_date_elem is not None:
                year = pub_date_elem.find('Year')
                month = pub_date_elem.find('Month')
                if year is not None:
                    pub_date = year.text
                    if month is not None:
                        pub_date += f" {month.text}"
            
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal,
                'pub_date': pub_date,
                'source': 'pubmed'
            }
            
        except Exception as e:
            logger.error(f"Error fetching PubMed details for {pmid}: {e}")
            return None
    
    def search_biorxiv(self, query: str, max_results: int = 30) -> List[Dict]:
        """
        Search bioRxiv for preprints.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of article details
        """
        logger.info(f"Searching bioRxiv for: {query}")
        
        try:
            # bioRxiv API endpoint
            search_url = f"{self.biorxiv_base}details/10.1101/{quote(query)}/"
            
            response = requests.get(search_url)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            if 'collection' in data:
                for item in data['collection'][:max_results]:
                    articles.append({
                        'doi': item.get('doi', ''),
                        'title': item.get('title', ''),
                        'abstract': item.get('abstract', ''),
                        'authors': item.get('authors', '').split(';'),
                        'journal': 'bioRxiv',
                        'pub_date': item.get('date', ''),
                        'source': 'biorxiv'
                    })
            
            logger.info(f"Found {len(articles)} articles in bioRxiv")
            return articles
            
        except Exception as e:
            logger.error(f"Error searching bioRxiv: {e}")
            return []
    
    def collect_articles(self, queries: List[str], max_per_query: int = 20) -> List[Dict]:
        """
        Collect articles from multiple queries.
        
        Args:
            queries: List of search queries
            max_per_query: Maximum articles per query
            
        Returns:
            List of collected articles
        """
        all_articles = []
        
        for query in queries:
            logger.info(f"Processing query: {query}")
            
            # Search PubMed
            pmids = self.search_pubmed(query, max_per_query)
            
            # Fetch details for each PMID
            for pmid in tqdm(pmids, desc=f"PubMed articles for '{query}'"):
                details = self.fetch_pubmed_details(pmid)
                if details:
                    all_articles.append(details)
                time.sleep(0.34)  # Respect NCBI rate limits (3 requests per second)
            
            # Search bioRxiv
            biorxiv_articles = self.search_biorxiv(query, max_per_query // 2)
            all_articles.extend(biorxiv_articles)
            
            time.sleep(1)  # Brief pause between queries
        
        logger.info(f"Total articles collected: {len(all_articles)}")
        return all_articles
    
    def save_articles(self, articles: List[Dict], filename: str = "articles.json"):
        """
        Save collected articles to JSON file.
        
        Args:
            articles: List of article dictionaries
            filename: Output filename
        """
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Articles saved to {filepath}")


def main():
    """Main function to demonstrate article collection."""
    
    # Define search queries related to Alzheimer's disease
    queries = [
        "Alzheimer's disease therapeutic targets",
        "Alzheimer's disease drug targets",
        "Alzheimer's disease potential targets",
        "Alzheimer's disease molecular targets",
        "Alzheimer's disease treatment targets"
    ]
    
    # Initialize collector
    collector = ArticleCollector()
    
    # Collect articles
    articles = collector.collect_articles(queries, max_per_query=15)
    
    # Save articles
    collector.save_articles(articles, "alzheimer_articles.json")
    
    print(f"Successfully collected {len(articles)} articles")


if __name__ == "__main__":
    main()