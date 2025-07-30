#!/usr/bin/env python3
"""
Agentic Commerce Market Size Projection (2025-2030)
Bottom-up analysis segmented by generation

This script calculates the total addressable market for Agentic Commerce
from 2025-2030, broken down by generational cohorts with specific variables
for each demographic segment.

Data sources: research-results folder insights and industry research
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from typing import Dict
import warnings
warnings.filterwarnings('ignore')

# Set up visualization style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AgenticCommerceProjection:
    def __init__(self, random_seed=42):
        """Initialize the market projection model with generation-specific data"""
        
        # Set random seed for reproducibility
        np.random.seed(random_seed)
        
        # Years for analysis
        self.years = list(range(2025, 2031))
        
        # =================================================================
        # GENERATION Z (Born 1997-2012, Ages 13-28 in 2025)
        # =================================================================
        self.gen_z_base = {
            'population_millions': {
                '2025_value': 95,  # US Gen Z population in millions
                'base_growth_rates': [1.0, 1.0, 1.0, 1.0, 1.0]  # 1% growth per year
            },
            'avg_annual_spending': {
                '2025_value': 3200,  # Average annual spending per Gen Z individual
                'base_growth_rates': [9.0, 11.0, 12.0, 11.0, 12.0]  # Higher growth as they enter workforce
            },
            'adoption_rate': {
                '2025_value': 0.25,  # 25% adoption rate (from research data)
                'base_growth_rates': [80.0, 44.0, 15.0, 9.0, 3.0]  # Rapid early, slower later (percentage point growth)
            },
            'pct_purchases_via_agents': {
                '2025_value': 0.08,  # 8% of purchases through agents
                'base_growth_rates': [87.0, 66.0, 52.0, 18.0, 11.0]  # Fast adoption curve
            }
        }
        
        # =================================================================
        # MILLENNIALS (Born 1981-1996, Ages 29-44 in 2025)
        # =================================================================
        self.millennials_base = {
            'population_millions': {
                '2025_value': 72,  # US Millennial population in millions
                'base_growth_rates': [0.0, 0.0, 0.0, -1.4, 0.0]  # Stable with slight decline
            },
            'avg_annual_spending': {
                '2025_value': 8500,  # Peak earning years, highest spending power
                'base_growth_rates': [8.0, 6.5, 6.0, 5.5, 4.5]  # Steady but slowing growth
            },
            'adoption_rate': {
                '2025_value': 0.18,  # 18% adoption (early majority)
                'base_growth_rates': [94.0, 43.0, 30.0, 11.0, 4.0]  # S-curve adoption
            },
            'pct_purchases_via_agents': {
                '2025_value': 0.05,  # 5% of purchases through agents
                'base_growth_rates': [140.0, 83.0, 45.0, 25.0, 12.0]  # Rapid practical adoption
            }
        }
        
        # =================================================================
        # GENERATION X (Born 1965-1980, Ages 45-60 in 2025)
        # =================================================================
        self.gen_x_base = {
            'population_millions': {
                '2025_value': 65,  # US Gen X population in millions
                'base_growth_rates': [0.0, 0.0, 0.0, -1.5, 0.0]  # Stable with slight decline
            },
            'avg_annual_spending': {
                '2025_value': 9800,  # High spending due to family responsibilities
                'base_growth_rates': [4.0, 3.0, 2.8, 2.0, 1.8]  # Modest growth
            },
            'adoption_rate': {
                '2025_value': 0.08,  # 8% adoption (conservative start)
                'base_growth_rates': [87.0, 66.0, 52.0, 18.0, 11.0]  # Cautious but accelerating
            },
            'pct_purchases_via_agents': {
                '2025_value': 0.03,  # 3% of purchases through agents
                'base_growth_rates': [166.0, 87.0, 53.0, 30.0, 17.0]  # Slow start, steady growth
            }
        }
        
        # =================================================================
        # BABY BOOMERS (Born 1946-1964, Ages 61-79 in 2025)
        # =================================================================
        self.baby_boomers_base = {
            'population_millions': {
                '2025_value': 71,  # US Baby Boomer population in millions
                'base_growth_rates': [-1.4, -1.4, -1.4, -1.5, -1.5]  # Gradual decline
            },
            'avg_annual_spending': {
                '2025_value': 7200,  # Fixed income but established spending
                'base_growth_rates': [2.8, 2.7, 2.6, 2.6, 2.5]  # Inflation-adjusted growth
            },
            'adoption_rate': {
                '2025_value': 0.03,  # 3% adoption (very conservative)
                'base_growth_rates': [166.0, 87.0, 47.0, 27.0, 14.0]  # Very slow but accelerating
            },
            'pct_purchases_via_agents': {
                '2025_value': 0.02,  # 2% of purchases through agents
                'base_growth_rates': [150.0, 100.0, 50.0, 33.0, 25.0]  # Gradual comfort building
            }
        }
        
        # Generate projected values with growth rate modifiers
        self.gen_z = self._generate_projections(self.gen_z_base)
        self.millennials = self._generate_projections(self.millennials_base)
        self.gen_x = self._generate_projections(self.gen_x_base)
        self.baby_boomers = self._generate_projections(self.baby_boomers_base)
        
        # =================================================================
        # REVENUE DISTRIBUTION MODEL
        # Based on agentic commerce research findings
        # =================================================================
        self.revenue_distribution_base = {
            'payment_processing': {
                '2025_value': 0.030,  # 3.0% standard rate
                'base_growth_rates': [-3.0, -3.0, -3.0, -3.0, -3.0]  # Slight compression over time
            },
            'ai_agent_platform': {
                '2025_value': 0.015,  # 1.5% of transaction value (mix of per-conv and %)
                'base_growth_rates': [20.0, 15.0, 10.0, 5.0, 0.0]  # Growth then stabilization
            },
            'advertising_placement': {
                '2025_value': 0.02,  # 2% starting (emerging category)
                'base_growth_rates': [100.0, 75.0, 50.0, 25.0, 15.0]  # Rapid growth as monetization increases
            },
            'data_analytics': {
                '2025_value': 0.003,  # 0.3% of transaction value
                'base_growth_rates': [33.0, 33.0, 25.0, 20.0, 15.0]  # Steady growth
            }
        }
        
        # Generate revenue distribution projections
        self.revenue_distribution = self._generate_projections(self.revenue_distribution_base)
    
    def _generate_growth_modifier(self):
        """
        Generate a random growth rate modifier between -100 and +100
        with a right skew (positive values more likely)
        
        Returns:
            float: Growth rate modifier as a percentage
        """
        # Use beta distribution for right skew
        # alpha=2, beta=5 gives a nice right skew when scaled
        raw_value = np.random.beta(2, 5)
        
        # Scale to -100 to +100 range with right skew
        # This maps [0,1] to [-100, +100] with more values above 0
        modifier = (raw_value * 200) - 80  # Shifts the distribution to favor positive
        
        # Ensure within bounds
        return max(-100, min(100, modifier))
    
    def _generate_projections(self, base_data: Dict) -> Dict:
        """
        Generate projections based on base values and growth rates with modifiers
        
        Args:
            base_data: Dictionary with base values and growth rates
            
        Returns:
            Dictionary with projected values for all years
        """
        projections = {}
        
        for variable, data in base_data.items():
            projections[variable] = {}
            projections[variable][2025] = data['2025_value']
            
            current_value = data['2025_value']
            
            for i, year in enumerate(self.years[1:]):  # 2026-2030
                base_growth = data['base_growth_rates'][i]
                modifier = self._generate_growth_modifier()
                
                # Apply modifier to base growth rate
                # Modifier scales the growth rate (e.g., +50% modifier on 10% growth = 15% growth)
                adjusted_growth = base_growth * (1 + modifier / 100)
                
                # Special handling for adoption rates and purchase percentages (they're already percentages)
                if variable in ['adoption_rate', 'pct_purchases_via_agents']:
                    # For these, growth represents percentage point increase
                    new_value = current_value * (1 + adjusted_growth / 100)
                    # Cap at reasonable maximums
                    if variable == 'adoption_rate':
                        new_value = min(new_value, 0.95)  # Cap at 95% adoption
                    elif variable == 'pct_purchases_via_agents':
                        new_value = min(new_value, 0.60)  # Cap at 60% of purchases
                else:
                    # For population and spending, use standard percentage growth
                    new_value = current_value * (1 + adjusted_growth / 100)
                
                projections[variable][year] = new_value
                current_value = new_value
                
        return projections
        
    def calculate_generation_market_size(self, generation_data: Dict, year: int) -> float:
        """
        Calculate market size for a specific generation and year
        
        Formula: Population × Average Spending × Adoption Rate × % Purchases via Agents
        
        Args:
            generation_data: Dictionary containing generation-specific variables
            year: Year to calculate for
            
        Returns:
            Market size in billions USD
        """
        population = generation_data['population_millions'][year]
        avg_spending = generation_data['avg_annual_spending'][year]
        adoption_rate = generation_data['adoption_rate'][year]
        pct_via_agents = generation_data['pct_purchases_via_agents'][year]
        
        # Calculate market size in billions
        market_size_billions = (population * avg_spending * adoption_rate * pct_via_agents) / 1000
        
        return market_size_billions
    
    def calculate_total_market_projection(self) -> pd.DataFrame:
        """
        Calculate total market size across all generations for all years
        
        Returns:
            DataFrame with market projections by generation and year
        """
        results = []
        
        for year in self.years:
            # Calculate each generation's market size
            gen_z_market = self.calculate_generation_market_size(self.gen_z, year)
            millennial_market = self.calculate_generation_market_size(self.millennials, year)
            gen_x_market = self.calculate_generation_market_size(self.gen_x, year)
            boomer_market = self.calculate_generation_market_size(self.baby_boomers, year)
            
            # Calculate total market size
            total_market = gen_z_market + millennial_market + gen_x_market + boomer_market
            
            results.append({
                'Year': year,
                'Gen Z': gen_z_market,
                'Millennials': millennial_market,
                'Gen X': gen_x_market,
                'Baby Boomers': boomer_market,
                'Total Market': total_market
            })
        
        return pd.DataFrame(results)
    
    def calculate_revenue_distribution(self, total_market_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate how revenue is distributed among ecosystem participants
        
        Args:
            total_market_df: DataFrame with total market projections
            
        Returns:
            DataFrame with revenue distribution by stakeholder and year
        """
        distribution_results = []
        
        for year in self.years:
            total_market = total_market_df[total_market_df['Year'] == year]['Total Market'].iloc[0]
            
            # Calculate revenue for each stakeholder
            payment_processing = total_market * self.revenue_distribution['payment_processing'][year]
            ai_platform = total_market * self.revenue_distribution['ai_agent_platform'][year]
            advertising = total_market * self.revenue_distribution['advertising_placement'][year]
            data_analytics = total_market * self.revenue_distribution['data_analytics'][year]
            
            # Calculate retailer/merchant revenue (what's left after all fees)
            total_fees = payment_processing + ai_platform + advertising + data_analytics
            retailer_revenue = total_market - total_fees
            
            distribution_results.append({
                'Year': year,
                'Total Market': total_market,
                'Retailer/Merchant': retailer_revenue,
                'Payment Processing': payment_processing,
                'AI Agent Platform': ai_platform,
                'Advertising/Placement': advertising,
                'Data & Analytics': data_analytics,
                'Total Fees': total_fees,
                'Retailer %': (retailer_revenue / total_market) * 100,
                'Fees %': (total_fees / total_market) * 100
            })
        
        return pd.DataFrame(distribution_results)
    
    def create_market_visualizations(self, df: pd.DataFrame) -> None:
        """
        Create comprehensive visualizations of market projections
        
        Args:
            df: DataFrame with market projection data
        """
        # Set up the figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Total Market Size Over Time
        ax1 = plt.subplot(2, 3, 1)
        plt.plot(df['Year'], df['Total Market'], marker='o', linewidth=3, markersize=8, color='#2E86AB')
        plt.title('Total Agentic Commerce Market Size (2025-2030)', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Market Size (Billions USD)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Annotate key milestones
        for i, row in df.iterrows():
            plt.annotate(f'${row["Total Market"]:.1f}B', 
                        (row['Year'], row['Total Market']),
                        textcoords="offset points", xytext=(0,10), ha='center',
                        fontsize=10, fontweight='bold')
        
        # 2. Market Size by Generation (Stacked Area Chart)
        ax2 = plt.subplot(2, 3, 2)
        generations = ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']
        colors = ['#A23B72', '#F18F01', '#C73E1D', '#2E86AB']
        
        plt.stackplot(df['Year'], df['Gen Z'], df['Millennials'], df['Gen X'], df['Baby Boomers'],
                     labels=generations, colors=colors, alpha=0.8)
        plt.title('Market Size by Generation (Stacked)', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Market Size (Billions USD)', fontsize=12)
        plt.legend(loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # 3. Market Share by Generation (2030)
        ax3 = plt.subplot(2, 3, 3)
        final_year_data = df[df['Year'] == 2030].iloc[0]
        market_shares = [final_year_data['Gen Z'], final_year_data['Millennials'], 
                        final_year_data['Gen X'], final_year_data['Baby Boomers']]
        
        plt.pie(market_shares, labels=generations, colors=colors, autopct='%1.1f%%',
                startangle=90, textprops={'fontsize': 11})
        plt.title('2030 Market Share by Generation', fontsize=14, fontweight='bold')
        
        # 4. Individual Generation Trends
        ax4 = plt.subplot(2, 3, 4)
        for gen, color in zip(generations, colors):
            plt.plot(df['Year'], df[gen], marker='o', label=gen, linewidth=2, color=color)
        
        plt.title('Individual Generation Market Trends', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Market Size (Billions USD)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # 5. Growth Rate Analysis
        ax5 = plt.subplot(2, 3, 5)
        growth_rates = []
        for i in range(1, len(df)):
            growth_rate = ((df.iloc[i]['Total Market'] / df.iloc[i-1]['Total Market']) - 1) * 100
            growth_rates.append(growth_rate)
        
        growth_years = df['Year'].iloc[1:].tolist()
        plt.bar(growth_years, growth_rates, color='#F18F01', alpha=0.7)
        plt.title('Year-over-Year Growth Rate', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Growth Rate (%)', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Add growth rate labels
        for i, (year, rate) in enumerate(zip(growth_years, growth_rates)):
            plt.annotate(f'{rate:.1f}%', (year, rate), textcoords="offset points", 
                        xytext=(0,5), ha='center', fontsize=10, fontweight='bold')
        
        # 6. Market Size Heatmap by Generation and Year
        ax6 = plt.subplot(2, 3, 6)
        heatmap_data = df.set_index('Year')[generations].T
        sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='YlOrRd', 
                   cbar_kws={'label': 'Market Size (Billions USD)'})
        plt.title('Market Size Heatmap by Generation', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Generation', fontsize=12)
        
        plt.tight_layout()
        plt.show()
    
    def create_revenue_distribution_visualizations(self, distribution_df: pd.DataFrame) -> None:
        """
        Create visualizations showing revenue distribution among ecosystem participants
        
        Args:
            distribution_df: DataFrame with revenue distribution data
        """
        # Set up the figure
        fig = plt.figure(figsize=(24, 20))
        
        # Define colors for each stakeholder
        stakeholder_colors = {
            'Retailer/Merchant': '#2E86AB',
            'Payment Processing': '#F71735',
            'AI Agent Platform': '#8FE402',
            'Advertising/Placement': '#F18F01',
            'Data & Analytics': '#C73E1D'
        }
        
        # 1. Revenue Distribution Overview - Stacked Bar Chart
        ax1 = plt.subplot(3, 3, 1)
        stakeholders = ['Retailer/Merchant', 'Payment Processing', 'AI Agent Platform', 
                       'Advertising/Placement', 'Data & Analytics']
        
        bottom = np.zeros(len(distribution_df))
        for stakeholder in stakeholders:
            values = distribution_df[stakeholder].values
            plt.bar(distribution_df['Year'], values, bottom=bottom, 
                   label=stakeholder, color=stakeholder_colors[stakeholder], alpha=0.8)
            bottom += values
        
        plt.title('Total Market Revenue Distribution by Year', fontsize=16, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Revenue (Billions USD)', fontsize=12)
        plt.legend(loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3, axis='y')
        
        # 2. Percentage Distribution - Stacked Area Chart
        ax2 = plt.subplot(3, 3, 2)
        
        # Calculate percentages
        percentages = {}
        for stakeholder in stakeholders:
            percentages[stakeholder] = (distribution_df[stakeholder] / distribution_df['Total Market'] * 100).values
        
        # Create stacked area chart
        plt.stackplot(distribution_df['Year'], 
                     percentages['Retailer/Merchant'],
                     percentages['Payment Processing'],
                     percentages['AI Agent Platform'],
                     percentages['Advertising/Placement'],
                     percentages['Data & Analytics'],
                     labels=stakeholders,
                     colors=[stakeholder_colors[s] for s in stakeholders],
                     alpha=0.8)
        
        plt.title('Revenue Distribution as Percentage of Total Market', fontsize=16, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Percentage of Total Market (%)', fontsize=12)
        plt.legend(loc='right', bbox_to_anchor=(1.15, 0.5), fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)
        
        # 3-8. Individual Year Pie Charts
        for i, year in enumerate(distribution_df['Year']):
            ax = plt.subplot(3, 3, i + 3)
            year_data = distribution_df[distribution_df['Year'] == year].iloc[0]
            
            sizes = [year_data[stakeholder] for stakeholder in stakeholders]
            colors = [stakeholder_colors[stakeholder] for stakeholder in stakeholders]
            
            # Create pie chart
            wedges, texts, autotexts = plt.pie(sizes, labels=stakeholders, colors=colors, 
                                               autopct='%1.1f%%', startangle=90)
            
            # Enhance text visibility
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_fontweight('bold')
                autotext.set_color('white')
            
            plt.title(f'{year} Revenue Distribution\n(Total: ${year_data["Total Market"]:.1f}B)', 
                     fontsize=12, fontweight='bold')
        
        # 9. Fee Evolution Chart
        ax9 = plt.subplot(3, 3, 9)
        
        # Plot individual fee components over time
        for stakeholder in ['Payment Processing', 'AI Agent Platform', 
                           'Advertising/Placement', 'Data & Analytics']:
            plt.plot(distribution_df['Year'], distribution_df[stakeholder], 
                    marker='o', label=stakeholder, linewidth=2.5,
                    color=stakeholder_colors[stakeholder])
        
        plt.title('Evolution of Fee Components (2025-2030)', fontsize=16, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Revenue (Billions USD)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Create a second figure for additional analyses
        fig2 = plt.figure(figsize=(20, 12))
        
        # 1. Total Fees vs Retailer Revenue
        ax1 = plt.subplot(2, 3, 1)
        plt.plot(distribution_df['Year'], distribution_df['Retailer %'], 
                marker='o', label='Retailer Share', linewidth=3, color='#2E86AB')
        plt.plot(distribution_df['Year'], distribution_df['Fees %'], 
                marker='s', label='Total Fees Share', linewidth=3, color='#F71735')
        
        plt.title('Retailer vs Total Fees Share of Market', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Percentage of Total Market (%)', fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)
        
        # 2. Fee Growth Rates
        ax2 = plt.subplot(2, 3, 2)
        fee_growth_rates = []
        fee_years = distribution_df['Year'].iloc[1:].tolist()
        
        for i in range(1, len(distribution_df)):
            prev_fees = distribution_df.iloc[i-1]['Total Fees']
            curr_fees = distribution_df.iloc[i]['Total Fees']
            growth_rate = ((curr_fees / prev_fees) - 1) * 100
            fee_growth_rates.append(growth_rate)
        
        plt.bar(fee_years, fee_growth_rates, color='#F18F01', alpha=0.7)
        plt.title('Year-over-Year Growth in Total Fees', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Growth Rate (%)', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, (year, rate) in enumerate(zip(fee_years, fee_growth_rates)):
            plt.annotate(f'{rate:.1f}%', (year, rate), textcoords="offset points", 
                        xytext=(0,5), ha='center', fontsize=10, fontweight='bold')
        
        # 3. Revenue Distribution Table
        ax3 = plt.subplot(2, 3, 3)
        ax3.axis('tight')
        ax3.axis('off')
        
        # Create table data
        table_data = []
        for _, row in distribution_df.iterrows():
            table_data.append([
                f"{row['Year']}",
                f"${row['Total Market']:.1f}B",
                f"${row['Retailer/Merchant']:.1f}B ({row['Retailer %']:.1f}%)",
                f"${row['Total Fees']:.1f}B ({row['Fees %']:.1f}%)"
            ])
        
        table = plt.table(cellText=table_data,
                         colLabels=['Year', 'Total Market', 'Retailer Revenue', 'Total Fees'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.15, 0.25, 0.35, 0.35])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Style the table
        for i in range(len(table_data) + 1):
            for j in range(4):
                cell = table[(i, j)]
                if i == 0:
                    cell.set_facecolor('#E0E0E0')
                    cell.set_text_props(weight='bold')
        
        plt.title('Revenue Distribution Summary', fontsize=14, fontweight='bold', pad=20)
        
        # 4. Advertising/Placement Fee Evolution (Emerging Category)
        ax4 = plt.subplot(2, 3, 4)
        plt.plot(distribution_df['Year'], distribution_df['Advertising/Placement'], 
                marker='o', linewidth=3, markersize=8, color='#F18F01')
        
        plt.title('Advertising/Placement Fees Growth\n(Emerging Revenue Category)', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Revenue (Billions USD)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Annotate values
        for _, row in distribution_df.iterrows():
            plt.annotate(f"${row['Advertising/Placement']:.2f}B", 
                        (row['Year'], row['Advertising/Placement']),
                        textcoords="offset points", xytext=(0,10), ha='center',
                        fontsize=10, fontweight='bold')
        
        # 5. AI Platform Revenue Analysis
        ax5 = plt.subplot(2, 3, 5)
        
        # Calculate per-transaction equivalent
        ai_rev_per_trans = []
        for _, row in distribution_df.iterrows():
            # Assume average transaction value of $75
            num_transactions = (row['Total Market'] * 1e9) / 75  # Convert billions to dollars
            ai_rev_per_trans.append((row['AI Agent Platform'] * 1e9) / num_transactions)
        
        plt.plot(distribution_df['Year'], ai_rev_per_trans, 
                marker='s', linewidth=3, markersize=8, color='#8FE402')
        
        plt.title('AI Agent Platform Revenue per Transaction\n(Assuming $75 avg transaction)', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Revenue per Transaction ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Annotate values
        for i, (year, value) in enumerate(zip(distribution_df['Year'], ai_rev_per_trans)):
            plt.annotate(f"${value:.3f}", (year, value),
                        textcoords="offset points", xytext=(0,10), ha='center',
                        fontsize=10, fontweight='bold')
        
        # 6. Market Concentration Analysis
        ax6 = plt.subplot(2, 3, 6)
        
        # Calculate HHI-like concentration for fees
        fee_categories = ['Payment Processing', 'AI Agent Platform', 
                         'Advertising/Placement', 'Data & Analytics']
        
        concentration_scores = []
        for year in distribution_df['Year']:
            year_data = distribution_df[distribution_df['Year'] == year].iloc[0]
            total_fees = year_data['Total Fees']
            
            # Calculate share of each fee within total fees
            hhi = 0
            for cat in fee_categories:
                if total_fees > 0:
                    share = (year_data[cat] / total_fees) * 100
                    hhi += share ** 2
                else:
                    hhi = 0
            
            concentration_scores.append(hhi / 10000)  # Normalize to 0-1
        
        plt.plot(distribution_df['Year'], concentration_scores, 
                marker='D', linewidth=3, markersize=8, color='#C73E1D')
        
        plt.title('Fee Market Concentration Index\n(0 = Perfect Competition, 1 = Monopoly)', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Concentration Index', fontsize=12)
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def print_detailed_analysis(self, df: pd.DataFrame) -> None:
        """
        Print detailed numerical analysis of the market projections
        
        Args:
            df: DataFrame with market projection data
        """
        print("=" * 80)
        print("AGENTIC COMMERCE MARKET SIZE PROJECTION (2025-2030)")
        print("Bottom-up Analysis by Generation")
        print("=" * 80)
        
        # Overview table
        print("\n📊 MARKET SIZE PROJECTIONS (Billions USD)")
        print("-" * 70)
        print(f"{'Year':<6} {'Gen Z':<8} {'Millennials':<12} {'Gen X':<8} {'Boomers':<9} {'Total':<8}")
        print("-" * 70)
        
        for _, row in df.iterrows():
            print(f"{row['Year']:<6} ${row['Gen Z']:<7.1f} ${row['Millennials']:<11.1f} "
                  f"${row['Gen X']:<7.1f} ${row['Baby Boomers']:<8.1f} ${row['Total Market']:<7.1f}")
        
        # Key insights
        print(f"\n🎯 KEY INSIGHTS")
        print("-" * 40)
        
        total_2025 = df[df['Year'] == 2025]['Total Market'].iloc[0]
        total_2030 = df[df['Year'] == 2030]['Total Market'].iloc[0]
        cagr = ((total_2030 / total_2025) ** (1/5) - 1) * 100
        
        print(f"• 2025 Market Size: ${total_2025:.1f} billion")
        print(f"• 2030 Market Size: ${total_2030:.1f} billion")
        print(f"• 5-Year CAGR: {cagr:.1f}%")
        print(f"• Total Growth: {((total_2030/total_2025 - 1) * 100):.1f}%")
        
        # Generation analysis
        print(f"\n👥 GENERATION BREAKDOWN (2030)")
        print("-" * 40)
        final_data = df[df['Year'] == 2030].iloc[0]
        generations = ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']
        
        for gen in generations:
            market_size = final_data[gen]
            market_share = (market_size / final_data['Total Market']) * 100
            print(f"• {gen:<12}: ${market_size:>5.1f}B ({market_share:>4.1f}%)")
        
        # Growth trajectory
        print(f"\n📈 GROWTH TRAJECTORY")
        print("-" * 40)
        
        for i in range(1, len(df)):
            current_year = df.iloc[i]['Year']
            prev_market = df.iloc[i-1]['Total Market']
            curr_market = df.iloc[i]['Total Market']
            growth = ((curr_market / prev_market) - 1) * 100
            print(f"• {current_year}: {growth:>5.1f}% growth (${curr_market:.1f}B)")
        
        # Assumptions and methodology
        print(f"\n📋 KEY ASSUMPTIONS")
        print("-" * 40)
        print("• Population data based on US Census projections")
        print("• Spending growth includes inflation and income growth")
        print("• Adoption rates based on technology adoption research")
        print("• Agent usage % reflects trust development patterns")
        print("• Each generation has independent variables")
        
        print("\n" + "=" * 80)
    
    def print_revenue_distribution_analysis(self, distribution_df: pd.DataFrame) -> None:
        """
        Print detailed analysis of revenue distribution
        
        Args:
            distribution_df: DataFrame with revenue distribution data
        """
        print("\n" + "=" * 80)
        print("REVENUE DISTRIBUTION ANALYSIS")
        print("How the Agentic Commerce Market Value is Divided")
        print("=" * 80)
        
        # Overview
        print("\n💰 REVENUE DISTRIBUTION BY STAKEHOLDER (Billions USD)")
        print("-" * 90)
        print(f"{'Year':<6} {'Total':<8} {'Retailer':<12} {'Payment':<10} {'AI Agent':<10} {'Advertising':<12} {'Data':<8}")
        print("-" * 90)
        
        for _, row in distribution_df.iterrows():
            print(f"{row['Year']:<6} ${row['Total Market']:<7.1f} "
                  f"${row['Retailer/Merchant']:<11.1f} ${row['Payment Processing']:<9.2f} "
                  f"${row['AI Agent Platform']:<9.2f} ${row['Advertising/Placement']:<11.2f} "
                  f"${row['Data & Analytics']:<7.2f}")
        
        # Percentage breakdown
        print("\n📊 PERCENTAGE DISTRIBUTION")
        print("-" * 70)
        print(f"{'Year':<6} {'Retailer %':<12} {'Payment %':<11} {'AI Agent %':<12} {'Advertising %':<14} {'Data %':<8}")
        print("-" * 70)
        
        for _, row in distribution_df.iterrows():
            retailer_pct = (row['Retailer/Merchant'] / row['Total Market']) * 100
            payment_pct = (row['Payment Processing'] / row['Total Market']) * 100
            ai_pct = (row['AI Agent Platform'] / row['Total Market']) * 100
            ad_pct = (row['Advertising/Placement'] / row['Total Market']) * 100
            data_pct = (row['Data & Analytics'] / row['Total Market']) * 100
            
            print(f"{row['Year']:<6} {retailer_pct:<11.1f}% {payment_pct:<10.1f}% "
                  f"{ai_pct:<11.1f}% {ad_pct:<13.1f}% {data_pct:<7.1f}%")
        
        # Key insights
        print("\n🎯 KEY REVENUE INSIGHTS")
        print("-" * 40)
        
        # Calculate changes
        start_retailer_pct = (distribution_df.iloc[0]['Retailer/Merchant'] / distribution_df.iloc[0]['Total Market']) * 100
        end_retailer_pct = (distribution_df.iloc[-1]['Retailer/Merchant'] / distribution_df.iloc[-1]['Total Market']) * 100
        
        start_fees = distribution_df.iloc[0]['Total Fees']
        end_fees = distribution_df.iloc[-1]['Total Fees']
        
        print(f"• Retailer share changes from {start_retailer_pct:.1f}% to {end_retailer_pct:.1f}%")
        print(f"• Total fees grow from ${start_fees:.2f}B to ${end_fees:.2f}B")
        print(f"• AI Agent Platform revenue: ${distribution_df.iloc[0]['AI Agent Platform']:.2f}B → ${distribution_df.iloc[-1]['AI Agent Platform']:.2f}B")
        print(f"• Advertising becomes major revenue stream: ${distribution_df.iloc[-1]['Advertising/Placement']:.2f}B by 2030")
        
        # Per-transaction analysis
        print("\n💳 PER-TRANSACTION BREAKDOWN (Assuming $75 avg transaction)")
        print("-" * 40)
        
        for year in [2025, 2030]:
            year_data = distribution_df[distribution_df['Year'] == year].iloc[0]
            num_trans = (year_data['Total Market'] * 1e9) / 75
            
            print(f"\n{year}:")
            print(f"  • Payment Processing: ${(year_data['Payment Processing'] * 1e9 / num_trans):.3f}")
            print(f"  • AI Agent Platform: ${(year_data['AI Agent Platform'] * 1e9 / num_trans):.3f}")
            print(f"  • Advertising/Placement: ${(year_data['Advertising/Placement'] * 1e9 / num_trans):.3f}")
            print(f"  • Data & Analytics: ${(year_data['Data & Analytics'] * 1e9 / num_trans):.3f}")
            print(f"  • Total Fees per Transaction: ${(year_data['Total Fees'] * 1e9 / num_trans):.3f}")
        
        print("\n" + "=" * 80)
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = "agentic_commerce_projections.csv") -> None:
        """
        Export projections to CSV file
        
        Args:
            df: DataFrame with market projection data  
            filename: Output filename
        """
        filepath = f"/Users/nicholaspate/Documents/agentic-commerce/{filename}"
        df.to_csv(filepath, index=False)
        print(f"\n💾 Data exported to: {filepath}")
    
    def display_growth_parameters(self) -> None:
        """
        Display the growth rate parameters used for each generation
        """
        print("\n" + "=" * 80)
        print("GROWTH RATE PARAMETERS")
        print("=" * 80)
        
        generations = [
            ('Generation Z', self.gen_z_base),
            ('Millennials', self.millennials_base),
            ('Generation X', self.gen_x_base),
            ('Baby Boomers', self.baby_boomers_base)
        ]
        
        for gen_name, gen_data in generations:
            print(f"\n📊 {gen_name.upper()}")
            print("-" * 60)
            
            for variable, data in gen_data.items():
                var_display = variable.replace('_', ' ').title()
                print(f"\n{var_display}:")
                print(f"  2025 Base Value: {data['2025_value']:,.0f}" if 'millions' in variable or 'spending' in variable 
                      else f"  2025 Base Value: {data['2025_value']:.2%}")
                print(f"  Base Growth Rates (2026-2030): {data['base_growth_rates']}")
                print(f"  Growth Modifier Range: -100% to +100% (right-skewed)")
    
    def display_actual_values(self) -> None:
        """
        Display the actual generated values after applying modifiers
        """
        print("\n" + "=" * 80)
        print("GENERATED VALUES WITH GROWTH MODIFIERS APPLIED")
        print("=" * 80)
        
        generations = [
            ('Generation Z', self.gen_z),
            ('Millennials', self.millennials),
            ('Generation X', self.gen_x),
            ('Baby Boomers', self.baby_boomers)
        ]
        
        for gen_name, gen_data in generations:
            print(f"\n📊 {gen_name.upper()} - Actual Projected Values")
            print("-" * 70)
            
            for variable, values in gen_data.items():
                var_display = variable.replace('_', ' ').title()
                print(f"\n{var_display}:")
                
                for year in self.years:
                    value = values[year]
                    if 'millions' in variable or 'spending' in variable:
                        print(f"  {year}: {value:,.0f}")
                    else:
                        print(f"  {year}: {value:.2%}")

def main():
    """
    Main execution function
    """
    # Initialize the projection model
    projection = AgenticCommerceProjection()
    
    # Display growth parameters
    projection.display_growth_parameters()
    
    # Display actual generated values
    projection.display_actual_values()
    
    # Calculate market projections
    market_df = projection.calculate_total_market_projection()
    
    # Display detailed analysis
    projection.print_detailed_analysis(market_df)
    
    # Calculate revenue distribution
    distribution_df = projection.calculate_revenue_distribution(market_df)
    
    # Display revenue distribution analysis
    projection.print_revenue_distribution_analysis(distribution_df)
    
    # Create visualizations
    projection.create_market_visualizations(market_df)
    
    # Create revenue distribution visualizations
    projection.create_revenue_distribution_visualizations(distribution_df)
    
    # Export data
    projection.export_to_csv(market_df)
    projection.export_to_csv(distribution_df, "agentic_commerce_revenue_distribution.csv")
    
    print("\n✅ Analysis complete! Review the visualizations and exported data.")
    print("\n💡 TIP: Run again with a different random seed to see alternative scenarios.")
    print("   Example: projection = AgenticCommerceProjection(random_seed=123)")
    print("\n📊 Two CSV files have been created:")
    print("   1. agentic_commerce_projections.csv - Market size by generation")
    print("   2. agentic_commerce_revenue_distribution.csv - Revenue breakdown by stakeholder")

if __name__ == "__main__":
    main()