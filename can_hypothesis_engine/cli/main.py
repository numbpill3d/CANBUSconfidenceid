#!/usr/bin/env python3
"""
CLI Interface for CAN Hypothesis Engine
"""

import argparse
import sys
import json
from pathlib import Path
from can_hypothesis_engine.parser.can_parser import parse_can_log
from can_hypothesis_engine.engine import CANHypothesisEngine


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='CAN Rolling Counter + Checksum Hypothesis Engine')
    parser.add_argument('log_file', help='Path to the CAN log file')
    parser.add_argument('-o', '--output', help='Output file path (JSON format)')
    parser.add_argument('-r', '--report', action='store_true', help='Generate human-readable report')
    parser.add_argument('--min-frames', type=int, default=20, help='Minimum frames per ID (default: 20)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.log_file).exists():
        print(f"Error: Log file '{args.log_file}' does not exist.")
        sys.exit(1)
    
    try:
        # Parse the CAN log file
        print(f"Parsing CAN log file: {args.log_file}")
        id_to_frames = parse_can_log(args.log_file, min_frames_per_id=args.min_frames)
        
        if not id_to_frames:
            print("No valid CAN frames found (insufficient frames per ID).")
            sys.exit(0)
        
        # Initialize the engine
        engine = CANHypothesisEngine()
        
        # Analyze all IDs
        print(f"Analyzing {len(id_to_frames)} arbitration IDs...")
        results = engine.analyze_grouped_frames(id_to_frames)
        
        # Output results
        if args.output:
            # Save to JSON file
            with open(args.output, 'w') as f:
                json.dump({
                    arb_id: result.to_dict() 
                    for arb_id, result in results.items()
                }, f, indent=2)
            print(f"Results saved to {args.output}")
        
        # Print human-readable report if requested
        if args.report:
            print("\n" + "="*80)
            print("CAN HYPOTHESIS ENGINE RESULTS")
            print("="*80)
            for arb_id, result in results.items():
                print(result.to_human_readable())
                print("\n" + "-"*60 + "\n")
        
        # Print summary to stdout if no output file specified
        if not args.output and not args.report:
            print(json.dumps({
                arb_id: result.to_dict() 
                for arb_id, result in results.items()
            }, indent=2))
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()