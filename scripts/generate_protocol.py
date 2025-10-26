#!/usr/bin/env python3
"""
Example script for generating experimental protocols using the Protocol Agent.
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.protocol_agent import ProtocolAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Generate a protocol based on example literature."""
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return
    
    # Example literature about E. coli growth optimization
    example_literature = """
    Title: Optimization of E. coli Growth Media for Enhanced Biomass Production
    
    Abstract: This study investigates optimal growth conditions for E. coli BL21 
    strain with focus on nutrient supplementation. We evaluated various carbon 
    sources (glucose, glycerol), nitrogen sources (tryptone, yeast extract), 
    and mineral supplements.
    
    Methods: E. coli BL21 was grown in 96-well plates with varying media compositions.
    Base media included standard LB components with systematic variation of carbon
    and nitrogen concentrations. Mineral supplements (MgSO4, CaCl2, trace metals) 
    were added at different concentrations. Growth was monitored by OD600 
    measurements every 30 minutes for 24 hours.
    
    Results: Optimal growth was observed with:
    - Tryptone at 10-15 g/L providing peptide nitrogen source
    - Yeast extract at 5-10 g/L for vitamins and cofactors
    - Glucose (10 g/L) or glycerol (20 mL/L) as carbon source
    - MgSO4 (1 mM) essential for enzyme cofactor
    - Trace amounts of CaCl2 (0.1 mM) for membrane stability
    - Buffering with MOPS (10 mM, pH 7.0) improved growth consistency
    - Phosphate buffer (K2HPO4/KH2PO4, 10 mM each) enhanced late-phase growth
    
    Conclusion: A defined medium with tryptone (100 mg/mL), yeast extract (100 mg/mL),
    glycerol, glucose (100 mg/mL), appropriate mineral supplementation (MgSO4 1M, 
    CaCl2 1M), and buffering (MOPS 1M, phosphate 1M) provides robust E. coli growth.
    Additional trace metals solution and pH control reagents (HCl 12N, NaOH 10N) 
    are recommended for optimization experiments.
    """
    
    print("=" * 80)
    print("Protocol Agent - Reagent Recommendation System")
    print("=" * 80)
    print("\nInitializing agent...")
    
    # Initialize agent
    agent = ProtocolAgent(model="gpt-4o", temperature=0.7)
    
    print("\nAnalyzing literature and generating protocol...")
    print("\nLiterature excerpt:")
    print(example_literature[:200] + "...\n")
    
    # Generate protocol without absorbance data
    print("Generating protocol recommendations...")
    df = agent.generate_protocol(
        literature=example_literature,
        output_csv_path="data/generated_protocol.csv"
    )
    
    print("\n" + "=" * 80)
    print("GENERATED PROTOCOL:")
    print("=" * 80)
    print(df.to_string(index=False))
    
    # Example with absorbance data if available
    absorbance_path = project_root / "data" / "Exp1 Hr 2.csv"
    if absorbance_path.exists():
        print("\n\n" + "=" * 80)
        print("Regenerating protocol WITH absorbance data analysis...")
        print("=" * 80)
        
        df_with_abs = agent.generate_protocol(
            literature=example_literature,
            absorbance_csv_path=str(absorbance_path),
            output_csv_path="data/generated_protocol_with_absorbance.csv"
        )
        
        print("\n" + "=" * 80)
        print("PROTOCOL WITH ABSORBANCE DATA:")
        print("=" * 80)
        print(df_with_abs.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("Protocol generation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

