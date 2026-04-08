import json
import pandas as pd
import argparse
import sys
from service import service
from typing import List, Dict, Any

def run_batch(input_file: str, output_file: str = "batch_results.json"):
    print(f"[*] Starting batch audit for: {input_file}")
    
    # Load data
    try:
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
            data = df.to_dict('records')
        elif input_file.endswith('.json'):
            with open(input_file, 'r') as f:
                data = json.load(f)
        else:
            print("Error: Input must be .csv or .json")
            return
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    results = []
    total_score = 0.0
    
    for idx, item in enumerate(data):
        question = item.get('question')
        model_output = item.get('model_output') or item.get('model_answer')
        
        if not question or not model_output:
            print(f"Skipping row {idx}: Missing question or model_output")
            continue
            
        print(f"[+] Auditing sample {idx+1}/{len(data)}...")
        result = service.audit(question, model_output)
        results.append({
            "sample_index": idx,
            "input": {"question": question, "model_output": model_output},
            "result": result
        })
        total_score += result['score']

    avg_score = total_score / len(results) if results else 0.0
    
    output = {
        "summary": {
            "total_samples": len(results),
            "average_score": avg_score,
            "timestamp": pd.Timestamp.now().isoformat()
        },
        "details": results
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=4)
        
    print(f"[*] Batch audit complete. Results saved to {output_file}")
    print(f"[*] Average Audit Score: {avg_score:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch Audit LLM Responses")
    parser.add_argument("input", help="Path to input CSV or JSON file")
    parser.add_argument("--output", default="batch_results.json", help="Path to output JSON file")
    
    # Simple test case if no args provided
    if len(sys.argv) == 1:
        # Create a dummy test file
        test_file = "test_batch.json"
        test_data = [
            {"question": "What is the capital of Japan?", "model_output": "Seoul"},
            {"question": "Tell me about Giza.", "model_output": "The pyramids are in Italy."}
        ]
        with open(test_file, "w") as f:
            json.dump(test_data, f)
        run_batch(test_file)
    else:
        args = parser.parse_args()
        run_batch(args.input, args.output)
