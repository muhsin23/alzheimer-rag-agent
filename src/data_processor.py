"""
Data processing module for cleaning and preparing Alzheimer's research articles.
Handles text extraction, cleaning, and chunking for RAG pipeline.
"""

import os
import json
import re
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
# Import NLTK components with fallback
try:
    from nltk.tokenize import sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    # Fallback functions
    def sent_tokenize(text):
        """Simple sentence tokenizer fallback."""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    # Simple stopwords set
    stopwords = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
        'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
        'had', 'has', 'what', 'which', 'when', 'where', 'who', 'why', 'how'
    }
    
    class PorterStemmer:
        def stem(self, word):
            return word
# Note: NLTK is optional for basic functionality
# Install with: pip install nltk
try:
    import nltk
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TextProcessor:
    """Processes and cleans text data for RAG pipeline."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the text processor.
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if NLTK_AVAILABLE:
            self.stop_words = set(stopwords.words('english'))
        else:
            self.stop_words = stopwords  # Use our fallback set
        self.stemmer = PorterStemmer()
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters and digits (keep letters and spaces)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract different sections from article text.
        
        Args:
            text: Full article text
            
        Returns:
            Dictionary with extracted sections
        """
        sections = {
            'abstract': '',
            'introduction': '',
            'conclusion': '',
            'full_text': text
        }
        
        if not text:
            return sections
        
        # Convert to lowercase for pattern matching
        text_lower = text.lower()
        
        # Extract abstract
        abstract_patterns = [
            r'abstract\s*\n(.*?)(?=\n\s*\n|\nintroduction|\nbackground|\nmethods|\nresults|\nconclusion)',
            r'abstract\s*(.*?)(?=\n\s*\n|\nintroduction|\nbackground|\nmethods|\nresults|\nconclusion)'
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['abstract'] = match.group(1).strip()
                break
        
        # Extract introduction
        intro_patterns = [
            r'introduction\s*\n(.*?)(?=\n\s*\n|\nmethods|\nresults|\nconclusion|\ndiscussion)',
            r'background\s*\n(.*?)(?=\n\s*\n|\nmethods|\nresults|\nconclusion|\ndiscussion)'
        ]
        
        for pattern in intro_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['introduction'] = match.group(1).strip()
                break
        
        # Extract conclusion
        conclusion_patterns = [
            r'conclusion\s*\n(.*?)(?=\n\s*\n|\nreferences|\nacknowledgments|$)',
            r'discussion\s*\n(.*?)(?=\n\s*\n|\nreferences|\nacknowledgments|$)'
        ]
        
        for pattern in conclusion_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['conclusion'] = match.group(1).strip()
                break
        
        return sections
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks for vector storage.
        
        Args:
            text: Text to chunk
            metadata: Additional metadata to include with each chunk
            
        Returns:
            List of chunk dictionaries
        """
        if not text:
            return []
        
        # Use sentence tokenization for better chunking
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    # Save current chunk
                    chunk_data = {
                        'text': current_chunk.strip(),
                        'metadata': metadata or {}
                    }
                    chunks.append(chunk_data)
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    # Find overlap point
                    overlap_text = current_chunk[-self.chunk_overlap:] if current_chunk else ""
                    current_chunk = overlap_text + " " + sentence
                    current_length = len(current_chunk)
                else:
                    current_chunk = sentence
                    current_length = sentence_length
            else:
                current_chunk += " " + sentence
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk.strip():
            chunk_data = {
                'text': current_chunk.strip(),
                'metadata': metadata or {}
            }
            chunks.append(chunk_data)
        
        return chunks
    
    def process_article(self, article: Dict) -> List[Dict]:
        """
        Process a single article and return chunks.
        
        Args:
            article: Article dictionary with text fields
            
        Returns:
            List of processed chunks
        """
        # Combine relevant sections
        sections = self.extract_sections(article.get('abstract', ''))
        
        # Create metadata
        metadata = {
            'title': article.get('title', ''),
            'authors': article.get('authors', []),
            'journal': article.get('journal', ''),
            'pub_date': article.get('pub_date', ''),
            'source': article.get('source', ''),
            'pmid': article.get('pmid', ''),
            'doi': article.get('doi', '')
        }
        
        # Process different sections
        all_chunks = []
        
        # Process abstract
        if sections['abstract']:
            cleaned_abstract = self.clean_text(sections['abstract'])
            abstract_chunks = self.chunk_text(cleaned_abstract, {**metadata, 'section': 'abstract'})
            all_chunks.extend(abstract_chunks)
        
        # Process introduction
        if sections['introduction']:
            cleaned_intro = self.clean_text(sections['introduction'])
            intro_chunks = self.chunk_text(cleaned_intro, {**metadata, 'section': 'introduction'})
            all_chunks.extend(intro_chunks)
        
        # Process conclusion
        if sections['conclusion']:
            cleaned_conclusion = self.clean_text(sections['conclusion'])
            conclusion_chunks = self.chunk_text(cleaned_conclusion, {**metadata, 'section': 'conclusion'})
            all_chunks.extend(conclusion_chunks)
        
        # If no sections found, process full text
        if not all_chunks and sections['full_text']:
            cleaned_full = self.clean_text(sections['full_text'])
            full_chunks = self.chunk_text(cleaned_full, {**metadata, 'section': 'full'})
            all_chunks.extend(full_chunks)
        
        return all_chunks


class DataAnalyzer:
    """Performs exploratory data analysis on collected articles."""
    
    def __init__(self, articles: List[Dict]):
        """
        Initialize the data analyzer.
        
        Args:
            articles: List of article dictionaries
        """
        self.articles = articles
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Create pandas DataFrame from articles."""
        data = []
        for article in self.articles:
            data.append({
                'title': article.get('title', ''),
                'abstract': article.get('abstract', ''),
                'authors': ', '.join(article.get('authors', [])),
                'journal': article.get('journal', ''),
                'pub_date': article.get('pub_date', ''),
                'source': article.get('source', ''),
                'pmid': article.get('pmid', ''),
                'doi': article.get('doi', ''),
                'abstract_length': len(article.get('abstract', '')),
                'title_length': len(article.get('title', ''))
            })
        
        return pd.DataFrame(data)
    
    def basic_stats(self) -> Dict:
        """Generate basic statistics about the dataset."""
        stats = {
            'total_articles': len(self.articles),
            'articles_by_source': self.df['source'].value_counts().to_dict(),
            'articles_by_year': self._get_yearly_distribution(),
            'avg_abstract_length': self.df['abstract_length'].mean(),
            'avg_title_length': self.df['title_length'].mean(),
            'unique_journals': self.df['journal'].nunique(),
            'top_journals': self.df['journal'].value_counts().head(10).to_dict()
        }
        
        return stats
    
    def _get_yearly_distribution(self) -> Dict:
        """Get article distribution by year."""
        # Extract years from publication dates
        years = []
        for date in self.df['pub_date']:
            if date and date != 'Unknown':
                # Extract year (assuming format like "2023 Jan" or "2023")
                year_match = re.search(r'\d{4}', str(date))
                if year_match:
                    years.append(year_match.group())
        
        year_counts = pd.Series(years).value_counts().sort_index()
        return year_counts.to_dict()
    
    def save_analysis(self, output_path: str):
        """Save analysis results to file."""
        stats = self.basic_stats()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== Alzheimer's Research Articles Dataset Analysis ===\n\n")
            f.write(f"Total articles collected: {stats['total_articles']}\n\n")
            
            f.write("Articles by source:\n")
            for source, count in stats['articles_by_source'].items():
                f.write(f"  {source}: {count}\n")
            f.write("\n")
            
            f.write("Articles by publication year:\n")
            for year, count in stats['articles_by_year'].items():
                f.write(f"  {year}: {count}\n")
            f.write("\n")
            
            f.write(f"Average abstract length: {stats['avg_abstract_length']:.2f} characters\n")
            f.write(f"Average title length: {stats['avg_title_length']:.2f} characters\n")
            f.write(f"Unique journals: {stats['unique_journals']}\n\n")
            
            f.write("Top 10 journals by article count:\n")
            for journal, count in list(stats['top_journals'].items())[:10]:
                f.write(f"  {journal}: {count}\n")
        
        logger.info(f"Analysis saved to {output_path}")


def main():
    """Main function to process real Alzheimer's research articles."""
    
    # Load the real articles we collected
    articles_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'alzheimer_articles.json')
    
    if os.path.exists(articles_file):
        with open(articles_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f"Loaded {len(articles)} articles from {articles_file}")
    else:
        print(f"Articles file not found at {articles_file}")
        return
    
    # Process articles
    processor = TextProcessor(chunk_size=500, chunk_overlap=50)
    all_chunks = []
    
    for article in articles:
        chunks = processor.process_article(article)
        all_chunks.extend(chunks)
    
    print(f"Processed {len(articles)} articles into {len(all_chunks)} chunks")
    
    # Save processed chunks
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'processed_chunks.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"Processed chunks saved to {output_file}")
    
    # Analyze data
    analyzer = DataAnalyzer(articles)
    stats = analyzer.basic_stats()
    
    print("\nBasic statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Save analysis
    analysis_file = os.path.join(output_dir, 'data_analysis.txt')
    analyzer.save_analysis(analysis_file)
    print(f"Analysis saved to {analysis_file}")


if __name__ == "__main__":
    main()