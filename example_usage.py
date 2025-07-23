#!/usr/bin/env python3
"""
Example usage of the Agentic Commerce Market Projection tool
Demonstrates different scenarios and analysis approaches
"""

from agentic_commerce_market_projection import AgenticCommerceProjection
import pandas as pd

def run_scenario_analysis():
    """
    Run multiple scenarios with different random seeds to show market variability
    """
    print("=" * 80)
    print("SCENARIO ANALYSIS: Running 3 Different Market Projections")
    print("=" * 80)
    
    scenarios = {
        'Conservative': 42,    # Default seed
        'Moderate': 123,      # Different growth patterns
        'Optimistic': 999     # Another variation
    }
    
    results = {}
    
    for scenario_name, seed in scenarios.items():
        print(f"\n📊 Running {scenario_name} Scenario (seed={seed})...")
        
        # Create projection with specific seed
        projection = AgenticCommerceProjection(random_seed=seed)
        
        # Calculate market projections
        market_df = projection.calculate_total_market_projection()
        
        # Store results
        results[scenario_name] = {
            '2025': market_df[market_df['Year'] == 2025]['Total Market'].iloc[0],
            '2030': market_df[market_df['Year'] == 2030]['Total Market'].iloc[0],
            'CAGR': ((market_df[market_df['Year'] == 2030]['Total Market'].iloc[0] / 
                     market_df[market_df['Year'] == 2025]['Total Market'].iloc[0]) ** (1/5) - 1) * 100
        }
    
    # Display comparison
    print("\n" + "=" * 60)
    print("SCENARIO COMPARISON")
    print("=" * 60)
    print(f"{'Scenario':<15} {'2025 Market':<15} {'2030 Market':<15} {'5-Year CAGR':<15}")
    print("-" * 60)
    
    for scenario, data in results.items():
        print(f"{scenario:<15} ${data['2025']:<14.1f}B ${data['2030']:<14.1f}B {data['CAGR']:<14.1f}%")

def analyze_specific_generation():
    """
    Deep dive into a specific generation's market potential
    """
    print("\n" + "=" * 80)
    print("GENERATION-SPECIFIC ANALYSIS: Millennials Deep Dive")
    print("=" * 80)
    
    projection = AgenticCommerceProjection()
    
    # Get millennial-specific data
    print("\n📊 Millennial Market Metrics:")
    print("-" * 40)
    
    for year in range(2025, 2031):
        pop = projection.millennials['population_millions'][year]
        spending = projection.millennials['avg_annual_spending'][year]
        adoption = projection.millennials['adoption_rate'][year]
        agent_pct = projection.millennials['pct_purchases_via_agents'][year]
        
        market_size = (pop * spending * adoption * agent_pct) / 1000
        
        print(f"{year}: Population={pop}M, Spending=${spending:,}, "
              f"Adoption={adoption:.1%}, Agent%={agent_pct:.1%}, "
              f"Market=${market_size:.2f}B")

def revenue_distribution_focus():
    """
    Analyze how revenue is distributed among ecosystem participants
    """
    print("\n" + "=" * 80)
    print("REVENUE DISTRIBUTION FOCUS: Where Does the Money Go?")
    print("=" * 80)
    
    projection = AgenticCommerceProjection()
    market_df = projection.calculate_total_market_projection()
    distribution_df = projection.calculate_revenue_distribution(market_df)
    
    # Show evolution of AI platform revenue
    print("\n🤖 AI Agent Platform Revenue Evolution:")
    print("-" * 40)
    
    for _, row in distribution_df.iterrows():
        ai_pct = (row['AI Agent Platform'] / row['Total Market']) * 100
        print(f"{row['Year']}: ${row['AI Agent Platform']:.2f}B ({ai_pct:.1f}% of total market)")
    
    # Show advertising revenue growth
    print("\n📢 Advertising/Placement Revenue (Fastest Growing):")
    print("-" * 40)
    
    for i, row in distribution_df.iterrows():
        ad_pct = (row['Advertising/Placement'] / row['Total Market']) * 100
        if i > 0:
            prev_ad = distribution_df.iloc[i-1]['Advertising/Placement']
            growth = ((row['Advertising/Placement'] / prev_ad) - 1) * 100
            print(f"{row['Year']}: ${row['Advertising/Placement']:.2f}B ({ad_pct:.1f}% of market, "
                  f"{growth:.1f}% YoY growth)")
        else:
            print(f"{row['Year']}: ${row['Advertising/Placement']:.2f}B ({ad_pct:.1f}% of market)")

def main():
    """
    Run all example analyses
    """
    print("\n🚀 AGENTIC COMMERCE MARKET PROJECTION - EXAMPLE ANALYSES")
    print("=" * 80)
    
    # Run different types of analyses
    run_scenario_analysis()
    analyze_specific_generation()
    revenue_distribution_focus()
    
    print("\n✅ Example analyses complete!")
    print("\n💡 These examples demonstrate:")
    print("   • How to run scenario analyses with different seeds")
    print("   • How to extract generation-specific insights")
    print("   • How to analyze revenue distribution patterns")
    print("\n📝 Modify this script to create your own custom analyses!")

if __name__ == "__main__":
    main()