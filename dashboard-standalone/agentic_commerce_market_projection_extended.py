#!/usr/bin/env python3
"""
Extended Agentic Commerce Market Size Projection (2025-2030)
Includes Consumer, Business, and Government spending segments

This enhanced script calculates the total addressable market for Agentic Commerce
from 2025-2030, including consumer (by generation), business (by industry), 
and government (by level and category) segments.

Data sources: 
- Consumer: research-results folder insights and industry research
- Business: industry_spending_data_2025.json and research reports
- Government: government-spending-segmentation-analysis.md
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

class ExtendedAgenticCommerceProjection:
    def __init__(self, random_seed=42):
        """Initialize the extended market projection model with consumer, business, and government data"""
        
        # Set random seed for reproducibility
        np.random.seed(random_seed)
        
        # Years for analysis
        self.years = list(range(2025, 2031))
        
        # =================================================================
        # CONSUMER SEGMENTS (Generations)
        # =================================================================
        
        # GENERATION Z (Born 1997-2012, Ages 13-28 in 2025)
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
        
        # MILLENNIALS (Born 1981-1996, Ages 29-44 in 2025)
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
        
        # GENERATION X (Born 1965-1980, Ages 45-60 in 2025)
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
        
        # BABY BOOMERS (Born 1946-1964, Ages 61-79 in 2025)
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
        
        # =================================================================
        # BUSINESS SEGMENTS (Industries)
        # Based on research from industry_spending_data_2025.json
        # =================================================================
        
        # FINANCIAL SERVICES
        self.financial_services_base = {
            'spending_billions': {
                '2025_value': 15000,  # Total financial services industry spending/revenue
                'base_growth_rates': [5.5, 5.2, 5.0, 4.8, 4.5]  # Moderate growth
            },
            'adoption_rate': {
                '2025_value': 0.10,  # 10% starting adoption (innovative sector)
                'base_growth_rates': [100.0, 75.0, 50.0, 25.0, 15.0]  # Rapid adoption
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.20,  # 20% of spending suitable for agentic commerce
                'base_growth_rates': [50.0, 40.0, 30.0, 20.0, 15.0]  # Growing suitability
            },
            'risk_tolerance': 0.7  # 0-1 scale, 0.7 = high tolerance
        }
        
        # MANUFACTURING
        self.manufacturing_base = {
            'spending_billions': {
                '2025_value': 7500,  # Total manufacturing industry spending/output
                'base_growth_rates': [4.0, 3.8, 3.5, 3.2, 3.0]  # Industrial growth rates
            },
            'adoption_rate': {
                '2025_value': 0.08,  # 8% starting adoption
                'base_growth_rates': [87.0, 66.0, 45.0, 25.0, 15.0]  # Moderate adoption
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.15,  # 15% suitable (supply chain, procurement)
                'base_growth_rates': [40.0, 33.0, 27.0, 20.0, 13.0]
            },
            'risk_tolerance': 0.5  # Moderate risk tolerance
        }
        
        # HEALTHCARE
        self.healthcare_base = {
            'spending_billions': {
                '2025_value': 4800,  # Total healthcare industry spending
                'base_growth_rates': [6.5, 6.2, 5.8, 5.5, 5.2]  # Healthcare spending growth
            },
            'adoption_rate': {
                '2025_value': 0.04,  # 4% starting (conservative due to regulations)
                'base_growth_rates': [125.0, 87.0, 66.0, 40.0, 25.0]  # Accelerating from low base
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.10,  # 10% suitable (administrative, procurement)
                'base_growth_rates': [50.0, 40.0, 30.0, 20.0, 15.0]
            },
            'risk_tolerance': 0.3  # Low risk tolerance due to regulatory requirements
        }
        
        # RETAIL
        self.retail_base = {
            'spending_billions': {
                '2025_value': 5200,  # Total retail industry revenue/spending
                'base_growth_rates': [4.5, 4.2, 4.0, 3.8, 3.5]  # Retail growth rates
            },
            'adoption_rate': {
                '2025_value': 0.12,  # 12% starting (naturally aligned with commerce)
                'base_growth_rates': [83.0, 58.0, 40.0, 25.0, 17.0]
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.30,  # 30% suitable (inventory, supplier management)
                'base_growth_rates': [33.0, 27.0, 20.0, 13.0, 10.0]
            },
            'risk_tolerance': 0.6  # Moderate-high tolerance
        }
        
        # TECHNOLOGY
        self.technology_base = {
            'spending_billions': {
                '2025_value': 6000,  # Total technology sector revenue/spending
                'base_growth_rates': [8.5, 8.0, 7.5, 7.0, 6.5]  # Tech sector growth
            },
            'adoption_rate': {
                '2025_value': 0.15,  # 15% highest starting adoption
                'base_growth_rates': [80.0, 60.0, 40.0, 20.0, 13.0]
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.25,  # 25% suitable
                'base_growth_rates': [40.0, 32.0, 24.0, 16.0, 12.0]
            },
            'risk_tolerance': 0.9  # Highest risk tolerance
        }
        
        # TRANSPORTATION
        self.transportation_base = {
            'spending_billions': {
                '2025_value': 2100,  # Total transportation & logistics industry spending
                'base_growth_rates': [5.0, 4.8, 4.5, 4.2, 4.0]  # Transport sector growth
            },
            'adoption_rate': {
                '2025_value': 0.06,  # 6% starting adoption
                'base_growth_rates': [100.0, 75.0, 50.0, 33.0, 20.0]
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.20,  # 20% suitable (fleet management, routing)
                'base_growth_rates': [40.0, 35.0, 25.0, 20.0, 15.0]
            },
            'risk_tolerance': 0.5  # Moderate tolerance
        }
        
        # ENERGY
        self.energy_base = {
            'spending_billions': {
                '2025_value': 1800,  # Total energy sector spending/revenue
                'base_growth_rates': [4.5, 4.2, 4.0, 3.8, 3.5]  # Energy sector growth
            },
            'adoption_rate': {
                '2025_value': 0.05,  # 5% starting adoption
                'base_growth_rates': [120.0, 80.0, 60.0, 40.0, 25.0]
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.18,  # 18% suitable (procurement, maintenance)
                'base_growth_rates': [44.0, 33.0, 28.0, 17.0, 11.0]
            },
            'risk_tolerance': 0.4  # Lower tolerance due to critical infrastructure
        }
        
        # REAL ESTATE
        self.real_estate_base = {
            'spending_billions': {
                '2025_value': 4000,  # Total real estate industry transactions/spending
                'base_growth_rates': [3.5, 3.2, 3.0, 2.8, 2.5]  # Real estate growth
            },
            'adoption_rate': {
                '2025_value': 0.03,  # 3% starting (conservative industry)
                'base_growth_rates': [133.0, 100.0, 70.0, 50.0, 30.0]
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.12,  # 12% suitable (property management, leasing)
                'base_growth_rates': [50.0, 42.0, 33.0, 25.0, 17.0]
            },
            'risk_tolerance': 0.3  # Conservative industry
        }
        
        # =================================================================
        # GOVERNMENT SEGMENTS
        # Based on government-spending-segmentation-analysis.md
        # =================================================================
        
        # FEDERAL GOVERNMENT
        self.federal_gov_base = {
            'spending_billions': {
                '2025_value': 7000,  # Total federal spending FY2025 ($7 trillion)
                'base_growth_rates': [5.0, 4.8, 4.5, 4.2, 4.0]  # Moderate growth
            },
            'adoption_rate': {
                '2025_value': 0.02,  # 2% starting (very conservative)
                'base_growth_rates': [150.0, 100.0, 75.0, 50.0, 35.0]  # Slow but accelerating
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.08,  # 8% suitable (procurement, administrative)
                'base_growth_rates': [50.0, 37.0, 25.0, 25.0, 12.0]
            },
            'regulatory_readiness': 0.4  # Lower due to procurement regulations
        }
        
        # STATE & LOCAL GOVERNMENT
        self.state_local_gov_base = {
            'spending_billions': {
                '2025_value': 3800,  # Total state & local spending (estimated)
                'base_growth_rates': [4.5, 4.2, 4.0, 3.8, 3.5]  # Slower growth
            },
            'adoption_rate': {
                '2025_value': 0.01,  # 1% starting (lagging federal)
                'base_growth_rates': [200.0, 150.0, 100.0, 60.0, 40.0]  # Very slow start
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.06,  # 6% suitable
                'base_growth_rates': [67.0, 50.0, 33.0, 25.0, 20.0]
            },
            'regulatory_readiness': 0.3  # Lowest readiness
        }
        
        # DEFENSE SPENDING
        self.defense_base = {
            'spending_billions': {
                '2025_value': 900,  # Total defense spending (estimated from $872B in 2024)
                'base_growth_rates': [3.0, 3.0, 2.8, 2.5, 2.5]  # Conservative growth
            },
            'adoption_rate': {
                '2025_value': 0.015,  # 1.5% starting
                'base_growth_rates': [167.0, 120.0, 80.0, 60.0, 40.0]
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.10,  # 10% suitable (supply chain, logistics)
                'base_growth_rates': [50.0, 40.0, 30.0, 20.0, 15.0]
            },
            'regulatory_readiness': 0.5  # Higher for certain applications
        }
        
        # HEALTHCARE (MEDICARE/MEDICAID)
        self.gov_healthcare_base = {
            'spending_billions': {
                '2025_value': 1900,  # Total government healthcare spending (Medicare + Medicaid)
                'base_growth_rates': [6.0, 5.5, 5.0, 4.5, 4.0]  # Growing with aging population
            },
            'adoption_rate': {
                '2025_value': 0.025,  # 2.5% starting
                'base_growth_rates': [140.0, 100.0, 70.0, 40.0, 28.0]
            },
            'pct_suitable_for_agents': {
                '2025_value': 0.15,  # 15% suitable (claims processing, eligibility)
                'base_growth_rates': [47.0, 33.0, 27.0, 20.0, 13.0]
            },
            'regulatory_readiness': 0.6  # High potential for automation
        }
        
        # Generate projected values with growth rate modifiers
        self.gen_z = self._generate_projections(self.gen_z_base)
        self.millennials = self._generate_projections(self.millennials_base)
        self.gen_x = self._generate_projections(self.gen_x_base)
        self.baby_boomers = self._generate_projections(self.baby_boomers_base)
        
        # Business segments
        self.financial_services = self._generate_projections(self.financial_services_base)
        self.manufacturing = self._generate_projections(self.manufacturing_base)
        self.healthcare = self._generate_projections(self.healthcare_base)
        self.retail = self._generate_projections(self.retail_base)
        self.technology = self._generate_projections(self.technology_base)
        self.transportation = self._generate_projections(self.transportation_base)
        self.energy = self._generate_projections(self.energy_base)
        self.real_estate = self._generate_projections(self.real_estate_base)
        
        # Government segments
        self.federal_gov = self._generate_projections(self.federal_gov_base)
        self.state_local_gov = self._generate_projections(self.state_local_gov_base)
        self.defense = self._generate_projections(self.defense_base)
        self.gov_healthcare = self._generate_projections(self.gov_healthcare_base)
        
        # REVENUE DISTRIBUTION MODEL
        self.revenue_distribution_base = {
            'payment_processing': {
                '2025_value': 0.030,  # 3.0% standard rate
                'base_growth_rates': [-3.0, -3.0, -3.0, -3.0, -3.0]  # Slight compression over time
            },
            'ai_agent_platform': {
                '2025_value': 0.015,  # 1.5% of transaction value
                'base_growth_rates': [20.0, 15.0, 10.0, 5.0, 0.0]  # Growth then stabilization
            },
            'advertising_placement': {
                '2025_value': 0.02,  # 2% starting (emerging category)
                'base_growth_rates': [100.0, 75.0, 50.0, 25.0, 15.0]  # Rapid growth
            },
            'data_analytics': {
                '2025_value': 0.003,  # 0.3% of transaction value
                'base_growth_rates': [33.0, 33.0, 25.0, 20.0, 15.0]  # Steady growth
            }
        }
        
        # Generate revenue distribution projections
        self.revenue_distribution = self._generate_projections(self.revenue_distribution_base)
    
    def _generate_growth_modifier(self):
        """Generate a random growth rate modifier between -100 and +100 with right skew"""
        # Use beta distribution for right skew
        raw_value = np.random.beta(2, 5)
        # Scale to -100 to +100 range with right skew
        modifier = (raw_value * 200) - 80  # Shifts the distribution to favor positive
        # Ensure within bounds
        return max(-100, min(100, modifier))
    
    def _generate_projections(self, base_data: Dict) -> Dict:
        """Generate projections based on base values and growth rates with modifiers"""
        projections = {}
        
        for variable, data in base_data.items():
            if variable in ['risk_tolerance', 'regulatory_readiness']:
                # These are constants, not time-series
                projections[variable] = data
                continue
                
            projections[variable] = {}
            projections[variable][2025] = data['2025_value']
            
            current_value = data['2025_value']
            
            for i, year in enumerate(self.years[1:]):  # 2026-2030
                base_growth = data['base_growth_rates'][i]
                modifier = self._generate_growth_modifier()
                
                # Apply modifier to base growth rate
                adjusted_growth = base_growth * (1 + modifier / 100)
                
                # Special handling for adoption rates and percentages
                if variable in ['adoption_rate', 'pct_purchases_via_agents', 'pct_suitable_for_agents']:
                    # For these, growth represents percentage point increase
                    new_value = current_value * (1 + adjusted_growth / 100)
                    # Cap at reasonable maximums
                    if variable == 'adoption_rate':
                        new_value = min(new_value, 0.95)  # Cap at 95% adoption
                    elif variable in ['pct_purchases_via_agents', 'pct_suitable_for_agents']:
                        new_value = min(new_value, 0.60)  # Cap at 60%
                else:
                    # For spending and population, use standard percentage growth
                    new_value = current_value * (1 + adjusted_growth / 100)
                
                projections[variable][year] = new_value
                current_value = new_value
                
        return projections
    
    def calculate_generation_market_size(self, generation_data: Dict, year: int) -> float:
        """Calculate market size for a specific generation and year"""
        population = generation_data['population_millions'][year]
        avg_spending = generation_data['avg_annual_spending'][year]
        adoption_rate = generation_data['adoption_rate'][year]
        pct_via_agents = generation_data['pct_purchases_via_agents'][year]
        
        # Calculate market size in billions
        market_size_billions = (population * avg_spending * adoption_rate * pct_via_agents) / 1000
        
        return market_size_billions
    
    def calculate_business_market_size(self, business_data: Dict, year: int, 
                                     risk_tolerance: float = None) -> float:
        """Calculate market size for a specific business segment and year"""
        spending = business_data['spending_billions'][year]
        adoption_rate = business_data['adoption_rate'][year]
        pct_suitable = business_data['pct_suitable_for_agents'][year]
        
        # Apply risk tolerance modifier if available
        if risk_tolerance is None and 'risk_tolerance' in business_data:
            risk_tolerance = business_data['risk_tolerance']
        
        if risk_tolerance:
            # Risk tolerance affects adoption speed
            adoption_rate = adoption_rate * (0.5 + 0.5 * risk_tolerance)
        
        # Calculate market size in billions
        market_size_billions = spending * adoption_rate * pct_suitable
        
        return market_size_billions
    
    def calculate_government_market_size(self, gov_data: Dict, year: int, 
                                       regulatory_readiness: float = None) -> float:
        """Calculate market size for a specific government segment and year"""
        spending = gov_data['spending_billions'][year]
        adoption_rate = gov_data['adoption_rate'][year]
        pct_suitable = gov_data['pct_suitable_for_agents'][year]
        
        # Apply regulatory readiness modifier if available
        if regulatory_readiness is None and 'regulatory_readiness' in gov_data:
            regulatory_readiness = gov_data['regulatory_readiness']
        
        if regulatory_readiness:
            # Regulatory readiness affects adoption speed
            adoption_rate = adoption_rate * (0.3 + 0.7 * regulatory_readiness)
        
        # Calculate market size in billions
        market_size_billions = spending * adoption_rate * pct_suitable
        
        return market_size_billions
    
    def calculate_total_market_projection(self) -> pd.DataFrame:
        """Calculate total market size across all segments for all years"""
        results = []
        
        for year in self.years:
            # Consumer market
            gen_z_market = self.calculate_generation_market_size(self.gen_z, year)
            millennial_market = self.calculate_generation_market_size(self.millennials, year)
            gen_x_market = self.calculate_generation_market_size(self.gen_x, year)
            boomer_market = self.calculate_generation_market_size(self.baby_boomers, year)
            total_consumer = gen_z_market + millennial_market + gen_x_market + boomer_market
            
            # Business market
            financial_market = self.calculate_business_market_size(self.financial_services, year)
            manufacturing_market = self.calculate_business_market_size(self.manufacturing, year)
            healthcare_market = self.calculate_business_market_size(self.healthcare, year)
            retail_market = self.calculate_business_market_size(self.retail, year)
            tech_market = self.calculate_business_market_size(self.technology, year)
            transport_market = self.calculate_business_market_size(self.transportation, year)
            energy_market = self.calculate_business_market_size(self.energy, year)
            realestate_market = self.calculate_business_market_size(self.real_estate, year)
            total_business = (financial_market + manufacturing_market + healthcare_market + 
                            retail_market + tech_market + transport_market + 
                            energy_market + realestate_market)
            
            # Government market
            federal_market = self.calculate_government_market_size(self.federal_gov, year)
            state_local_market = self.calculate_government_market_size(self.state_local_gov, year)
            defense_market = self.calculate_government_market_size(self.defense, year)
            gov_health_market = self.calculate_government_market_size(self.gov_healthcare, year)
            total_government = federal_market + state_local_market + defense_market + gov_health_market
            
            # Total market
            total_market = total_consumer + total_business + total_government
            
            results.append({
                'Year': year,
                # Consumer breakdown
                'Gen Z': gen_z_market,
                'Millennials': millennial_market,
                'Gen X': gen_x_market,
                'Baby Boomers': boomer_market,
                'Total Consumer': total_consumer,
                # Business breakdown
                'Financial Services': financial_market,
                'Manufacturing': manufacturing_market,
                'Healthcare (Business)': healthcare_market,
                'Retail': retail_market,
                'Technology': tech_market,
                'Transportation': transport_market,
                'Energy': energy_market,
                'Real Estate': realestate_market,
                'Total Business': total_business,
                # Government breakdown
                'Federal': federal_market,
                'State & Local': state_local_market,
                'Defense': defense_market,
                'Healthcare (Gov)': gov_health_market,
                'Total Government': total_government,
                # Grand total
                'Total Market': total_market
            })
        
        return pd.DataFrame(results)
    
    def calculate_revenue_distribution(self, total_market_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate how revenue is distributed among ecosystem participants"""
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