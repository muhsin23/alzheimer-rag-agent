# Alzheimer's RAG Agent

A Retrieval-Augmented Generation (RAG) system designed to help researchers find potential drug targets for Alzheimer's disease treatment.

## 🎯 Project Overview

This RAG agent assists researchers in discovering new potential therapeutic targets for Alzheimer's disease by:

- **Collecting** scientific articles from PubMed and bioRxiv
- **Processing** and cleaning text data for optimal retrieval
- **Storing** knowledge in vector databases for semantic search
- **Generating** comprehensive answers with proper citations
- **Providing** an interactive interface for easy querying

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Models and Technologies](#models-and-technologies)
- [Evaluation Metrics](#evaluation-metrics)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)

## ✨ Features

### Data Collection
- Automated collection from PubMed and bioRxiv APIs
- Support for multiple search queries
- Rate limiting and error handling
- JSON export of collected articles

### Text Processing
- Text cleaning and normalization
- Section extraction (abstract, introduction, conclusion)
- Smart chunking with overlap
- Metadata preservation

### RAG Pipeline
- Vector embeddings using Sentence Transformers
- ChromaDB for vector storage
- Retrieval with similarity search
- Generation with OpenAI or HuggingFace models
- Source citation and confidence scoring

### Interactive Interface
- Streamlit web application
- Real-time querying
- Source document display
- Confidence visualization
- Example questions

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd alzheimer_rag_agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
   ```

## 💻 Usage

### 1. Data Collection

```python
from src.data_collector import ArticleCollector

# Initialize collector
collector = ArticleCollector()

# Define search queries
queries = [
    "Alzheimer's disease therapeutic targets",
    "Alzheimer's disease drug targets"
]

# Collect articles
articles = collector.collect_articles(queries, max_per_query=20)

# Save articles
collector.save_articles(articles, "alzheimer_articles.json")
```

### 2. Data Processing

```python
from src.data_processor import TextProcessor, DataAnalyzer

# Process articles
processor = TextProcessor(chunk_size=500, chunk_overlap=50)
all_chunks = []

for article in articles:
    chunks = processor.process_article(article)
    all_chunks.extend(chunks)

# Analyze data
analyzer = DataAnalyzer(articles)
stats = analyzer.basic_stats()
analyzer.save_analysis("data/analysis_results.txt")
```

### 3. RAG Pipeline

```python
from src.rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Add documents to vector store
pipeline.add_documents(all_chunks)

# Set up QA chain
pipeline.setup_qa_chain(use_openai=True, openai_api_key="your-key")

# Query the system
result = pipeline.query("What are potential targets for Alzheimer's disease treatment?")
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
```

### 4. Web Interface

```bash
# Run the Streamlit app
streamlit run src/streamlit_app.py
```

Navigate to `http://localhost:8501` to access the web interface.

### 5. Jupyter Analysis

Open `notebooks/interactive_analysis.ipynb` for interactive exploration and analysis.

## 📁 Project Structure

```
alzheimer_rag_agent/
├── data/                    # Raw and processed data
│   ├── raw/                # Raw article data
│   ├── processed/          # Cleaned and chunked data
│   └── vector_store/       # Vector database
├── notebooks/              # Jupyter notebooks for analysis
│   └── interactive_analysis.ipynb
├── src/                    # Source code
│   ├── data_collector.py   # Article collection
│   ├── data_processor.py   # Text processing
│   ├── rag_pipeline.py     # RAG system
│   └── streamlit_app.py    # Web interface
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .env                   # Environment variables
```

## 🤖 Models and Technologies

### Embedding Models
- **Sentence Transformers**: `all-MiniLM-L6-v2` for efficient text embeddings
- **Alternative**: BioBERT or SciBERT for domain-specific embeddings

### Language Models
- **OpenAI**: GPT-3.5 Turbo, GPT-4 for high-quality generation
- **HuggingFace**: Various open-source models for local deployment

### Vector Database
- **ChromaDB**: Lightweight, efficient vector storage
- **Alternative**: FAISS, Pinecone, or Weaviate for larger scale

### Frameworks
- **LangChain**: RAG pipeline orchestration
- **Streamlit**: Web interface development
- **NLTK**: Text processing and NLP utilities

## 📊 Evaluation Metrics

### Retrieval Metrics
- **Precision@K**: Proportion of relevant documents in top K results
- **Recall@K**: Proportion of relevant documents retrieved out of all relevant
- **Mean Reciprocal Rank (MRR)**: Average of reciprocal ranks of first relevant result

### Generation Metrics
- **BLEU Score**: N-gram overlap with reference answers
- **ROUGE Score**: Recall-oriented n-gram overlap
- **Human Evaluation**: Relevance, accuracy, and helpfulness scoring

### Custom Metrics
- **Confidence Scoring**: Heuristic-based confidence estimation
- **Source Coverage**: Proportion of answer supported by retrieved sources

## 🔮 Future Enhancements

### Data Modalities
1. **Multi-modal Data**:
   - Research figures and diagrams
   - Clinical trial data
   - Genomic and proteomic datasets
   - Medical imaging data

2. **Real-time Data**:
   - Preprint server monitoring
   - Clinical trial updates
   - Patent database integration
   - Social media research discussions

3. **Structured Data**:
   - Drug databases (DrugBank, ChEMBL)
   - Protein interaction networks
   - Pathway databases (KEGG, Reactome)
   - Genetic association studies

### Implementation Strategies

1. **Multi-modal RAG**:
   ```python
   # Pseudo-code for multi-modal extension
   class MultiModalRAG:
       def __init__(self):
           self.text_processor = TextProcessor()
           self.image_processor = ImageProcessor()  # CLIP, ViT
           self.tabular_processor = TabularProcessor()  # TabNet, AutoML
   
       def process_multimodal_document(self, document):
           # Process text, images, and tables separately
           # Combine embeddings for unified retrieval
   ```

2. **Knowledge Graph Integration**:
   ```python
   # Pseudo-code for KG integration
   class KnowledgeGraphRAG:
       def __init__(self):
           self.kg = Neo4jConnection()
           self.rag_pipeline = RAGPipeline()
       
       def query_with_kg_context(self, query):
           # Retrieve KG context
           kg_context = self.kg.get_context(query)
           # Combine with RAG results
           return self.rag_pipeline.query_with_context(query, kg_context)
   ```

3. **Active Learning**:
   - User feedback integration
   - Continuous model improvement
   - Query difficulty assessment

### Advanced Features

1. **Personalization**:
   - User preference learning
   - Research history tracking
   - Custom document collections

2. **Collaboration**:
   - Team document sharing
   - Annotation and highlighting
   - Research workflow integration

3. **Explainability**:
   - Answer provenance tracking
   - Confidence calibration
   - Bias detection and mitigation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PubMed and bioRxiv for providing access to scientific literature
- LangChain team for the excellent RAG framework
- HuggingFace for open-source models and embeddings
- Streamlit team for the interactive web framework

## 📞 Contact

For questions and support, please open an issue in the repository.

---

**Note**: This is a prototype system for research purposes. Always verify information with primary sources before making research decisions.