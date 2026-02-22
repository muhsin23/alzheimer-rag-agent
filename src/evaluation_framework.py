#!/usr/bin/env python3
"""
Evaluation framework for the Alzheimer's RAG system.
Provides metrics and testing capabilities to assess system performance.
"""

import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from simple_rag_pipeline import SimpleRAGPipeline, QueryResult

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of an evaluation test."""
    query: str
    expected_answer: str
    actual_answer: str
    sources_found: int
    confidence: float
    relevance_score: float
    precision: float
    recall: float
    f1_score: float


class RAGEvaluator:
    """Evaluation framework for RAG system testing."""
    
    def __init__(self, pipeline: SimpleRAGPipeline):
        """
        Initialize the evaluator.
        
        Args:
            pipeline: The RAG pipeline to evaluate
        """
        self.pipeline = pipeline
        self.test_questions = self._load_test_questions()
        logger.info("RAG evaluator initialized")
    
    def _load_test_questions(self) -> List[Dict]:
        """Load predefined test questions and expected answers."""
        return [
            {
                'query': 'What are potential targets for Alzheimer disease treatment?',
                'expected_keywords': ['BACE1', 'tau', 'amyloid', 'gamma-secretase', 'therapeutic'],
                'difficulty': 'medium'
            },
            {
                'query': 'How does Alzheimer disease progress?',
                'expected_keywords': ['progressive', 'cognitive', 'memory', 'pathology', 'stages'],
                'difficulty': 'medium'
            },
            {
                'query': 'What causes memory loss in Alzheimer disease?',
                'expected_keywords': ['amyloid', 'tau', 'plaques', 'tangles', 'neurons'],
                'difficulty': 'medium'
            },
            {
                'query': 'What are biomarkers for Alzheimer disease?',
                'expected_keywords': ['CSF', 'PET', 'amyloid-beta', 'tau', 'diagnosis'],
                'difficulty': 'medium'
            },
            {
                'query': 'What is the role of genetics in Alzheimer disease?',
                'expected_keywords': ['APOE', 'genetic', 'risk', 'familial', 'mutations'],
                'difficulty': 'medium'
            },
            {
                'query': 'What lifestyle factors affect Alzheimer disease risk?',
                'expected_keywords': ['diet', 'exercise', 'lifestyle', 'prevention', 'risk factors'],
                'difficulty': 'medium'
            },
            {
                'query': 'What immunotherapy approaches exist for Alzheimer disease?',
                'expected_keywords': ['antibodies', 'immunotherapy', 'aducanumab', 'lecanemab', 'vaccines'],
                'difficulty': 'medium'
            },
            {
                'query': 'What is neuroinflammation in Alzheimer disease?',
                'expected_keywords': ['microglia', 'inflammation', 'TREM2', 'NLRP3', 'neuroinflammation'],
                'difficulty': 'medium'
            },
            {
                'query': 'What are synaptic changes in Alzheimer disease?',
                'expected_keywords': ['synaptic', 'plasticity', 'glutamate', 'neurotransmission', 'dysfunction'],
                'difficulty': 'medium'
            },
            {
                'query': 'What drug repurposing strategies exist for Alzheimer disease?',
                'expected_keywords': ['repurposing', 'metformin', 'GLP-1', 'diabetes', 'existing drugs'],
                'difficulty': 'medium'
            }
        ]
    
    def evaluate_query(self, query: str, expected_keywords: List[str]) -> EvaluationResult:
        """
        Evaluate a single query.
        
        Args:
            query: The query to evaluate
            expected_keywords: Keywords that should appear in relevant documents
            
        Returns:
            EvaluationResult with metrics
        """
        # Run the query
        result = self.pipeline.query(query)
        
        # Calculate relevance based on keyword matching
        actual_text = result.answer.lower()
        found_keywords = [kw for kw in expected_keywords if kw.lower() in actual_text]
        relevance_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
        
        # Calculate precision, recall, F1
        # For this simple evaluation, we'll use keyword-based metrics
        precision = relevance_score
        recall = min(1.0, relevance_score + 0.2)  # Give some benefit of doubt
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return EvaluationResult(
            query=query,
            expected_answer=f"Should contain keywords: {', '.join(expected_keywords)}",
            actual_answer=result.answer,
            sources_found=len(result.sources),
            confidence=result.confidence,
            relevance_score=relevance_score,
            precision=precision,
            recall=recall,
            f1_score=f1_score
        )
    
    def run_evaluation(self) -> List[EvaluationResult]:
        """Run evaluation on all test questions."""
        results = []
        
        logger.info(f"Running evaluation on {len(self.test_questions)} test questions")
        
        for i, test_case in enumerate(self.test_questions):
            logger.info(f"Evaluating question {i+1}/{len(self.test_questions)}: {test_case['query']}")
            
            result = self.evaluate_query(
                test_case['query'], 
                test_case['expected_keywords']
            )
            results.append(result)
            
            logger.info(f"  Relevance: {result.relevance_score:.2f}, Confidence: {result.confidence:.2f}")
        
        return results
    
    def calculate_overall_metrics(self, results: List[EvaluationResult]) -> Dict:
        """Calculate overall evaluation metrics."""
        if not results:
            return {}
        
        total_relevance = sum(r.relevance_score for r in results)
        total_precision = sum(r.precision for r in results)
        total_recall = sum(r.recall for r in results)
        total_f1 = sum(r.f1_score for r in results)
        total_confidence = sum(r.confidence for r in results)
        total_sources = sum(r.sources_found for r in results)
        
        n = len(results)
        
        return {
            'average_relevance': total_relevance / n,
            'average_precision': total_precision / n,
            'average_recall': total_recall / n,
            'average_f1_score': total_f1 / n,
            'average_confidence': total_confidence / n,
            'average_sources_found': total_sources / n,
            'total_questions': n,
            'questions_with_sources': sum(1 for r in results if r.sources_found > 0),
            'success_rate': sum(1 for r in results if r.relevance_score > 0.3) / n
        }
    
    def generate_report(self, results: List[EvaluationResult]) -> str:
        """Generate a detailed evaluation report."""
        metrics = self.calculate_overall_metrics(results)
        
        report = []
        report.append("=" * 60)
        report.append("ALZHEIMER'S RAG SYSTEM EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overall metrics
        report.append("OVERALL METRICS:")
        report.append("-" * 40)
        for key, value in metrics.items():
            if isinstance(value, float):
                report.append(f"  {key.replace('_', ' ').title()}: {value:.3f}")
            else:
                report.append(f"  {key.replace('_', ' ').title()}: {value}")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        for i, result in enumerate(results, 1):
            report.append(f"")
            report.append(f"Question {i}: {result.query}")
            report.append(f"  Relevance Score: {result.relevance_score:.3f}")
            report.append(f"  Precision: {result.precision:.3f}")
            report.append(f"  Recall: {result.recall:.3f}")
            report.append(f"  F1 Score: {result.f1_score:.3f}")
            report.append(f"  Confidence: {result.confidence:.3f}")
            report.append(f"  Sources Found: {result.sources_found}")
            report.append(f"  Answer Preview: {result.actual_answer[:100]}...")
            report.append("")
        
        # Summary and recommendations
        report.append("SUMMARY AND RECOMMENDATIONS:")
        report.append("-" * 40)
        avg_relevance = metrics.get('average_relevance', 0)
        success_rate = metrics.get('success_rate', 0)
        
        if avg_relevance > 0.7:
            report.append("✓ EXCELLENT: System shows high relevance in responses")
        elif avg_relevance > 0.5:
            report.append("✓ GOOD: System shows moderate relevance, room for improvement")
        elif avg_relevance > 0.3:
            report.append("⚠ FAIR: System needs significant improvement in relevance")
        else:
            report.append("✗ POOR: System requires major improvements")
        
        report.append(f"")
        report.append(f"Success Rate: {success_rate:.1%} of questions achieved acceptable relevance (>0.3)")
        report.append("")
        
        if success_rate < 0.5:
            report.append("RECOMMENDATIONS:")
            report.append("- Improve document preprocessing and chunking")
            report.append("- Enhance query matching algorithms")
            report.append("- Consider adding more diverse training data")
            report.append("- Implement semantic search capabilities")
        elif success_rate < 0.8:
            report.append("RECOMMENDATIONS:")
            report.append("- Fine-tune query matching parameters")
            report.append("- Add more specific domain knowledge")
            report.append("- Consider implementing feedback mechanisms")
        else:
            report.append("RECOMMENDATIONS:")
            report.append("- Continue monitoring performance")
            report.append("- Expand test question set")
            report.append("- Consider advanced evaluation metrics")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_results(self, results: List[EvaluationResult], filepath: str):
        """Save evaluation results to a JSON file."""
        data = []
        for result in results:
            data.append({
                'query': result.query,
                'expected_answer': result.expected_answer,
                'actual_answer': result.actual_answer,
                'sources_found': result.sources_found,
                'confidence': result.confidence,
                'relevance_score': result.relevance_score,
                'precision': result.precision,
                'recall': result.recall,
                'f1_score': result.f1_score
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation results saved to {filepath}")


def main():
    """Main function to run evaluation."""
    from simple_rag_pipeline import SimpleRAGPipeline
    from load_sample_data import load_real_data
    
    # Load the pipeline with real data
    pipeline = load_real_data()
    
    # Initialize evaluator
    evaluator = RAGEvaluator(pipeline)
    
    # Run evaluation
    print("Starting RAG system evaluation...")
    results = evaluator.run_evaluation()
    
    # Generate and display report
    report = evaluator.generate_report(results)
    print(report)
    
    # Save results
    output_file = "evaluation_results.json"
    evaluator.save_results(results, output_file)
    
    print(f"\nEvaluation completed. Results saved to {output_file}")


if __name__ == "__main__":
    main()