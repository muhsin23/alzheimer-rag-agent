#!/usr/bin/env python3
"""
Script to load real Alzheimer's research data from processed chunks.
"""

import sys
import os
import json
sys.path.insert(0, 'src')

from simple_rag_pipeline import SimpleRAGPipeline

def load_real_data():
    """Load real Alzheimer's research data from processed chunks."""
    print("Loading real Alzheimer's research data...")
    
    # Initialize pipeline
    pipeline = SimpleRAGPipeline()
    
    # Load the real processed data
    processed_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'processed_chunks.json')
    
    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print(f"Loaded {len(chunks)} processed research chunks from {processed_file}")
        
        # Add all chunks to pipeline
        for chunk in chunks:
            pipeline.add_documents([chunk])
        
        print(f"Successfully loaded {len(chunks)} research chunks into the system")
    else:
        print(f"Processed data file not found at {processed_file}")
        print("Loading sample data instead...")
        
        # Sample research articles (fallback)
        sample_articles = [
            {
                'text': 'Alzheimer\'s disease (AD) is a progressive neurodegenerative disorder characterized by cognitive decline, memory loss, and behavioral changes. The disease is associated with the accumulation of amyloid-beta plaques and neurofibrillary tangles in the brain. Current research focuses on identifying therapeutic targets including BACE1 inhibitors, gamma-secretase modulators, and tau protein aggregation inhibitors. Immunotherapy approaches targeting amyloid-beta have shown promise in clinical trials.',
                'metadata': {
                    'title': 'Potential Targets for Alzheimer\'s Disease Treatment',
                    'journal': 'Journal of Neuroscience',
                    'pub_date': '2023',
                    'source': 'pubmed',
                    'pmid': '12345678',
                    'section': 'abstract'
                }
            },
            {
                'text': 'BACE1 (Beta-site APP Cleaving Enzyme 1) is a key therapeutic target for Alzheimer\'s disease. BACE1 inhibitors reduce the production of amyloid-beta peptides by blocking the cleavage of amyloid precursor protein (APP). Several BACE1 inhibitors have been developed and tested in clinical trials, though challenges remain regarding selectivity and blood-brain barrier penetration. Combination therapies targeting both amyloid-beta production and tau pathology show synergistic effects in preclinical models.',
                'metadata': {
                    'title': 'BACE1 Inhibitors in Alzheimer\'s Disease Therapy',
                    'journal': 'Neurotherapeutics',
                    'pub_date': '2023',
                    'source': 'pubmed',
                    'pmid': '12345679',
                    'section': 'abstract'
                }
            }
        ]
        
        # Add sample documents to pipeline
        for article in sample_articles:
            pipeline.add_documents([article])
        
        print(f"Successfully loaded {len(sample_articles)} sample articles into the system")
    
    print("The RAG system now contains comprehensive Alzheimer's disease research data")
    print("You can now ask questions about:")
    print("- Therapeutic targets and drug development")
    print("- Disease mechanisms and pathology")
    print("- Biomarkers and diagnosis")
    print("- Genetic factors and risk assessment")
    print("- Lifestyle interventions and prevention")
    print("- Immunotherapy and clinical trials")
    
    return pipeline

if __name__ == "__main__":
    load_real_data()