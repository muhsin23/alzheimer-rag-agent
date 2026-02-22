"""
Streamlit web application for Alzheimer's RAG research assistant.
Provides an interactive interface for querying the RAG system.
"""

import streamlit as st
import os
import json
import logging
from typing import List, Dict, Optional
from simple_rag_pipeline import SimpleRAGPipeline, QueryResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Alzheimer's Research Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        margin-bottom: 1rem;
    }
    .confidence-high { color: #2ecc71; font-weight: bold; }
    .confidence-medium { color: #f1c40f; font-weight: bold; }
    .confidence-low { color: #e74c3c; font-weight: bold; }
    .source-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .metadata-info {
        font-size: 0.9rem;
        color: #666;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_pipeline():
    """Initialize the RAG pipeline with real data."""
    try:
        # Import the data loading function
        from load_sample_data import load_real_data
        
        # Load the real Alzheimer's research data
        pipeline = load_real_data()
        return pipeline
    except Exception as e:
        st.error(f"Error initializing pipeline: {e}")
        return None

def get_confidence_color(confidence: float) -> str:
    """Get CSS class for confidence level."""
    if confidence >= 0.8:
        return "confidence-high"
    elif confidence >= 0.6:
        return "confidence-medium"
    else:
        return "confidence-low"

def display_sources(sources: List[Dict]):
    """Display source documents in a formatted way."""
    if not sources:
        st.info("No sources found for this query.")
        return
    
    for i, source in enumerate(sources, 1):
        with st.container():
            st.markdown(f"### Source {i}")
            
            # Source metadata
            metadata = source.get('metadata', {})
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Title:** {metadata.get('title', 'N/A')}")
                st.markdown(f"**Journal:** {metadata.get('journal', 'N/A')}")
                st.markdown(f"**Publication Date:** {metadata.get('pub_date', 'N/A')}")
            
            with col2:
                st.markdown(f"**Authors:** {', '.join(metadata.get('authors', [])) if metadata.get('authors') else 'N/A'}")
                st.markdown(f"**Source:** {metadata.get('source', 'N/A').upper()}")
            
            with col3:
                st.markdown(f"**PMID:** {metadata.get('pmid', 'N/A')}")
                st.markdown(f"**DOI:** {metadata.get('doi', 'N/A')}")
                st.markdown(f"**Section:** {metadata.get('section', 'N/A')}")
            
            # Source text
            with st.expander("View Source Text"):
                st.markdown(source.get('text', 'No text available'))
            
            st.markdown("---")

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">🧬 Alzheimer\'s Research Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered RAG system for drug target discovery</div>', unsafe_allow_html=True)
    
    # Initialize pipeline
    pipeline = initialize_pipeline()
    
    if not pipeline:
        st.error("Failed to initialize the RAG pipeline. Please check the configuration.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Model selection
        model_option = st.selectbox(
            "Select LLM Model",
            ["GPT-3.5 Turbo", "GPT-4", "Local HuggingFace Model"],
            help="Choose the language model for generating responses"
        )
        
        # API Key input (if needed)
        api_key = None
        if model_option in ["GPT-3.5 Turbo", "GPT-4"]:
            api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
        
        # Chunk settings
        chunk_size = st.slider("Chunk Size", min_value=200, max_value=1000, value=500, step=100)
        chunk_overlap = st.slider("Chunk Overlap", min_value=0, max_value=200, value=50, step=10)
        
        # Number of sources
        top_k = st.slider("Number of Sources", min_value=1, max_value=10, value=3)
        
        # Actions
        st.divider()
        
        if st.button("Initialize QA Chain"):
            try:
                use_openai = model_option in ["GPT-3.5 Turbo", "GPT-4"]
                model_name = "gpt-3.5-turbo" if model_option == "GPT-3.5 Turbo" else "gpt-4"
                
                pipeline.setup_qa_chain(use_openai=use_openai, openai_api_key=api_key)
                st.success("QA Chain initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing QA chain: {e}")
        
        # Upload documents
        st.divider()
        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF/Text files", 
            type=["pdf", "txt", "docx"], 
            accept_multiple_files=True,
            help="Upload research articles to add to the knowledge base"
        )
        
        if st.button("Process Documents") and uploaded_files:
            st.info("Document processing functionality would be implemented here.")
            st.info("This would extract text, clean it, and add it to the vector store.")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Ask a Question")
        
        # Example questions
        example_questions = [
            "What are potential targets for Alzheimer's disease treatment?",
            "Are the targets druggable with small molecules, biologics, or other modalities?",
            "What additional studies are needed to advance these targets?",
            "What is the role of amyloid-beta in Alzheimer's disease?",
            "How do tau protein tangles contribute to neurodegeneration?"
        ]
        
        selected_question = st.selectbox("Or select an example question:", [""] + example_questions)
        
        # User input
        user_question = st.text_area(
            "Enter your question:",
            value=selected_question,
            height=150,
            placeholder="Type your research question here..."
        )
        
        # Query button
        if st.button("🔍 Search and Generate Answer", type="primary"):
            if not user_question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Searching knowledge base and generating response..."):
                    try:
                        # Query the RAG system
                        result = pipeline.query(user_question, top_k=top_k)
                        
                        # Display results
                        st.success("Query completed successfully!")
                        
                        # Answer section
                        st.header("Generated Answer")
                        st.markdown(result.answer)
                        
                        # Confidence score
                        confidence_class = get_confidence_color(result.confidence)
                        st.markdown(f'<p class="{confidence_class}">Confidence Score: {result.confidence:.2f}</p>', unsafe_allow_html=True)
                        
                        # Sources section
                        st.header("Sources")
                        display_sources(result.sources)
                        
                    except Exception as e:
                        st.error(f"Error processing query: {e}")
                        st.info("Make sure the QA chain is initialized and you have a valid API key if using OpenAI models.")
    
    with col2:
        st.header("System Information")
        
        # Pipeline status
        st.info(f"**Vector Store Path:** {pipeline.vector_store_path}")
        st.info(f"**Chunk Size:** {chunk_size}")
        st.info(f"**Chunk Overlap:** {chunk_overlap}")
        st.info("**Embedding Model:** Simple keyword matching (demo)")
        
        # Statistics (real data)
        st.header("Statistics")
        total_docs = len(pipeline.documents) if hasattr(pipeline, 'documents') else 0
        total_chunks = total_docs
        avg_chunk_size = f"{chunk_size} chars" if chunk_size else "N/A"
        
        st.metric("Total Documents", total_docs, help="Number of documents in the knowledge base")
        st.metric("Total Chunks", total_chunks, help="Number of text chunks in the vector store")
        st.metric("Average Chunk Size", avg_chunk_size)
        
        # Evaluation metrics (placeholder)
        st.header("Evaluation Metrics")
        st.info("Retrieval and generation metrics would be displayed here.")
        
        # Help section
        st.header("Help")
        st.markdown("""
        **How to use:**
        1. Select a model and configure settings in the sidebar
        2. Initialize the QA chain
        3. Enter your research question or select an example
        4. Click "Search and Generate Answer"
        5. Review the generated answer and sources
        
        **Tips:**
        - Be specific with your questions
        - Check the sources for more detailed information
        - The confidence score indicates answer reliability
        """)
        
        # About section
        st.header("About")
        st.markdown("""
        This RAG system helps researchers find potential drug targets for Alzheimer's disease by:
        
        - **Retrieving** relevant scientific literature
        - **Generating** comprehensive answers with citations
        - **Providing** source documents for further reading
        
        Built with LangChain, HuggingFace, and Streamlit.
        """)

if __name__ == "__main__":
    main()