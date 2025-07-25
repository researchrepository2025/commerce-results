#!/usr/bin/env python3
"""
Enhanced Agentic Commerce Market Projection Dashboard
Includes Consumer, Business, and Government spending segments
"""

import dash
from dash import dcc, html, Input, Output, State, dash_table, ALL, MATCH
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentic_commerce_market_projection_extended import ExtendedAgenticCommerceProjection

# Add AI chatbot integration
sys.path.append(os.path.join(os.path.dirname(__file__), 'agentic-commerce-chatbot'))
try:
    from frontend.final_integration import integrate_ai_with_enhanced_dashboard
    AI_CHAT_AVAILABLE = True
except ImportError as e:
    print(f"AI Chat not available - {e}")
    AI_CHAT_AVAILABLE = False

# Initialize the Dash app with better styling
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Enhanced Agentic Commerce Market Projection Dashboard"

# Add custom CSS for better text contrast
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Fix tab styling for better contrast */
            .tab {
                background-color: #f8f9fa !important;
                color: #212529 !important;
                border: 1px solid #dee2e6 !important;
                font-weight: 500;
                padding: 10px 20px;
            }
            
            .tab--selected {
                background-color: #007bff !important;
                color: white !important;
                border-color: #007bff !important;
                font-weight: 600;
            }
            
            /* Tab hover effect */
            .tab:hover:not(.tab--selected) {
                background-color: #e9ecef !important;
                color: #212529 !important;
            }
            
            /* Ensure all text has proper contrast */
            body {
                color: #212529 !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            
            /* Fix header text colors */
            h1, h2, h3, h4, h5, h6 {
                color: inherit !important;
            }
            
            /* Input fields should have dark text */
            input[type="text"], input[type="number"], select, textarea {
                color: #212529 !important;
                background-color: white !important;
                border: 1px solid #ced4da !important;
            }
            
            /* Dropdown menus */
            .Select-control, .Select-value-label {
                color: #212529 !important;
            }
            
            /* Tab container background */
            .dash-tabs {
                background-color: transparent !important;
            }
            
            /* Tab content area */
            .tab-content {
                background-color: #f8f9fa !important;
                color: #212529 !important;
            }
            
            /* Slider labels */
            .rc-slider-mark-text {
                color: #666 !important;
            }
            
            /* Graph backgrounds */
            .dash-graph {
                background-color: white !important;
            }
            
            /* Table headers - keep these with good contrast */
            .dash-table-container .dash-header {
                color: white !important;
            }
            
            /* Details/Summary elements */
            details summary {
                color: #212529 !important;
            }
            
            /* Labels and paragraphs */
            label, p {
                color: #212529 !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define color schemes
GENERATION_COLORS = {
    'Gen Z': '#A23B72',
    'Millennials': '#F18F01',
    'Gen X': '#C73E1D',
    'Baby Boomers': '#2E86AB'
}

INDUSTRY_COLORS = {
    'Financial Services': '#1f77b4',
    'Manufacturing': '#ff7f0e',
    'Healthcare (Business)': '#2ca02c',
    'Retail': '#d62728',
    'Technology': '#9467bd',
    'Transportation': '#8c564b',
    'Energy': '#e377c2',
    'Real Estate': '#7f7f7f'
}

GOVERNMENT_COLORS = {
    'Federal': '#393b79',
    'State & Local': '#5254a3',
    'Defense': '#6b6ecf',
    'Healthcare (Gov)': '#9c9ede'
}

STAKEHOLDER_COLORS = {
    'Retailer/Merchant': '#2E86AB',
    'Payment Processing': '#F71735',
    'AI Agent Platform': '#8FE402',
    'Advertising/Placement': '#F18F01',
    'Data & Analytics': '#C73E1D'
}

# Create initial projections
initial_projection = ExtendedAgenticCommerceProjection(random_seed=42)
initial_market_df = initial_projection.calculate_total_market_projection()
initial_distribution_df = initial_projection.calculate_revenue_distribution(initial_market_df)

# Get initial values for generations
initial_gen_data = {
    'Gen Z': {
        'adoption_2025': initial_projection.gen_z_base['adoption_rate']['2025_value'] * 100,
        'population': initial_projection.gen_z_base['population_millions']['2025_value'],
        'annual_spending': initial_projection.gen_z_base['avg_annual_spending']['2025_value'],
        'pct_via_agents': initial_projection.gen_z_base['pct_purchases_via_agents']['2025_value'] * 100,
        'population_growth': initial_projection.gen_z_base['population_millions']['base_growth_rates'],
        'spending_growth': initial_projection.gen_z_base['avg_annual_spending']['base_growth_rates'],
        'adoption_growth': initial_projection.gen_z_base['adoption_rate']['base_growth_rates'],
        'agent_usage_growth': initial_projection.gen_z_base['pct_purchases_via_agents']['base_growth_rates']
    },
    'Millennials': {
        'adoption_2025': initial_projection.millennials_base['adoption_rate']['2025_value'] * 100,
        'population': initial_projection.millennials_base['population_millions']['2025_value'],
        'annual_spending': initial_projection.millennials_base['avg_annual_spending']['2025_value'],
        'pct_via_agents': initial_projection.millennials_base['pct_purchases_via_agents']['2025_value'] * 100,
        'population_growth': initial_projection.millennials_base['population_millions']['base_growth_rates'],
        'spending_growth': initial_projection.millennials_base['avg_annual_spending']['base_growth_rates'],
        'adoption_growth': initial_projection.millennials_base['adoption_rate']['base_growth_rates'],
        'agent_usage_growth': initial_projection.millennials_base['pct_purchases_via_agents']['base_growth_rates']
    },
    'Gen X': {
        'adoption_2025': initial_projection.gen_x_base['adoption_rate']['2025_value'] * 100,
        'population': initial_projection.gen_x_base['population_millions']['2025_value'],
        'annual_spending': initial_projection.gen_x_base['avg_annual_spending']['2025_value'],
        'pct_via_agents': initial_projection.gen_x_base['pct_purchases_via_agents']['2025_value'] * 100,
        'population_growth': initial_projection.gen_x_base['population_millions']['base_growth_rates'],
        'spending_growth': initial_projection.gen_x_base['avg_annual_spending']['base_growth_rates'],
        'adoption_growth': initial_projection.gen_x_base['adoption_rate']['base_growth_rates'],
        'agent_usage_growth': initial_projection.gen_x_base['pct_purchases_via_agents']['base_growth_rates']
    },
    'Baby Boomers': {
        'adoption_2025': initial_projection.baby_boomers_base['adoption_rate']['2025_value'] * 100,
        'population': initial_projection.baby_boomers_base['population_millions']['2025_value'],
        'annual_spending': initial_projection.baby_boomers_base['avg_annual_spending']['2025_value'],
        'pct_via_agents': initial_projection.baby_boomers_base['pct_purchases_via_agents']['2025_value'] * 100,
        'population_growth': initial_projection.baby_boomers_base['population_millions']['base_growth_rates'],
        'spending_growth': initial_projection.baby_boomers_base['avg_annual_spending']['base_growth_rates'],
        'adoption_growth': initial_projection.baby_boomers_base['adoption_rate']['base_growth_rates'],
        'agent_usage_growth': initial_projection.baby_boomers_base['pct_purchases_via_agents']['base_growth_rates']
    }
}

# Get initial values for industries
initial_industry_data = {
    'Financial Services': {
        'spending_2025': initial_projection.financial_services_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.financial_services_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.financial_services_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.financial_services_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.financial_services_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.financial_services_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.financial_services_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Manufacturing': {
        'spending_2025': initial_projection.manufacturing_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.manufacturing_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.manufacturing_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.manufacturing_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.manufacturing_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.manufacturing_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.manufacturing_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Healthcare': {
        'spending_2025': initial_projection.healthcare_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.healthcare_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.healthcare_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.healthcare_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.healthcare_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.healthcare_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.healthcare_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Retail': {
        'spending_2025': initial_projection.retail_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.retail_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.retail_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.retail_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.retail_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.retail_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.retail_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Technology': {
        'spending_2025': initial_projection.technology_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.technology_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.technology_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.technology_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.technology_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.technology_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.technology_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Transportation': {
        'spending_2025': initial_projection.transportation_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.transportation_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.transportation_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.transportation_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.transportation_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.transportation_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.transportation_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Energy': {
        'spending_2025': initial_projection.energy_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.energy_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.energy_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.energy_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.energy_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.energy_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.energy_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Real Estate': {
        'spending_2025': initial_projection.real_estate_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.real_estate_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.real_estate_base['pct_suitable_for_agents']['2025_value'] * 100,
        'risk_tolerance': initial_projection.real_estate_base['risk_tolerance'] * 100,
        'spending_growth': initial_projection.real_estate_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.real_estate_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.real_estate_base['pct_suitable_for_agents']['base_growth_rates']
    }
}

# Get initial values for government
initial_gov_data = {
    'Federal': {
        'spending_2025': initial_projection.federal_gov_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.federal_gov_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.federal_gov_base['pct_suitable_for_agents']['2025_value'] * 100,
        'regulatory_readiness': initial_projection.federal_gov_base['regulatory_readiness'] * 100,
        'spending_growth': initial_projection.federal_gov_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.federal_gov_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.federal_gov_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'State & Local': {
        'spending_2025': initial_projection.state_local_gov_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.state_local_gov_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.state_local_gov_base['pct_suitable_for_agents']['2025_value'] * 100,
        'regulatory_readiness': initial_projection.state_local_gov_base['regulatory_readiness'] * 100,
        'spending_growth': initial_projection.state_local_gov_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.state_local_gov_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.state_local_gov_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Defense': {
        'spending_2025': initial_projection.defense_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.defense_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.defense_base['pct_suitable_for_agents']['2025_value'] * 100,
        'regulatory_readiness': initial_projection.defense_base['regulatory_readiness'] * 100,
        'spending_growth': initial_projection.defense_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.defense_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.defense_base['pct_suitable_for_agents']['base_growth_rates']
    },
    'Healthcare (Gov)': {
        'spending_2025': initial_projection.gov_healthcare_base['spending_billions']['2025_value'],
        'adoption_2025': initial_projection.gov_healthcare_base['adoption_rate']['2025_value'] * 100,
        'pct_suitable': initial_projection.gov_healthcare_base['pct_suitable_for_agents']['2025_value'] * 100,
        'regulatory_readiness': initial_projection.gov_healthcare_base['regulatory_readiness'] * 100,
        'spending_growth': initial_projection.gov_healthcare_base['spending_billions']['base_growth_rates'],
        'adoption_growth': initial_projection.gov_healthcare_base['adoption_rate']['base_growth_rates'],
        'suitability_growth': initial_projection.gov_healthcare_base['pct_suitable_for_agents']['base_growth_rates']
    }
}

# Initial fee structure
initial_fees = {
    'payment_processing': initial_projection.revenue_distribution_base['payment_processing']['2025_value'] * 100,
    'ai_agent_platform': initial_projection.revenue_distribution_base['ai_agent_platform']['2025_value'] * 100,
    'advertising_placement': initial_projection.revenue_distribution_base['advertising_placement']['2025_value'] * 100,
    'data_analytics': initial_projection.revenue_distribution_base['data_analytics']['2025_value'] * 100,
    'payment_growth': initial_projection.revenue_distribution_base['payment_processing']['base_growth_rates'],
    'ai_growth': initial_projection.revenue_distribution_base['ai_agent_platform']['base_growth_rates'],
    'advertising_growth': initial_projection.revenue_distribution_base['advertising_placement']['base_growth_rates'],
    'data_growth': initial_projection.revenue_distribution_base['data_analytics']['base_growth_rates']
}

def create_growth_rate_inputs(year_labels, initial_values, id_prefix):
    """Create input fields for growth rates"""
    inputs = []
    for i, (year, value) in enumerate(zip(year_labels, initial_values)):
        inputs.append(
            html.Div([
                html.Label(f"{year}:", style={
                    'width': '50px', 
                    'display': 'inline-block', 
                    'fontSize': 14,
                    'color': '#555',
                    'fontWeight': '500'
                }),
                dcc.Input(
                    id={'type': id_prefix, 'index': i},
                    type='number',
                    value=value,
                    step=0.1,
                    style={
                        'width': '70px', 
                        'fontSize': 14,
                        'padding': '5px 8px',
                        'border': '1px solid #ced4da',
                        'borderRadius': 4,
                        'backgroundColor': 'white'
                    }
                ),
                html.Span("%", style={'marginLeft': 5, 'fontSize': 14, 'color': '#666'})
            ], style={'display': 'inline-block', 'marginRight': 20})
        )
    return html.Div(inputs, style={'marginTop': 5})

def create_generation_controls():
    """Create comprehensive controls for each generation"""
    controls = []
    year_labels = ['2026', '2027', '2028', '2029', '2030']
    
    for gen_name, data in initial_gen_data.items():
        controls.append(
            html.Div([
                html.Div([
                    html.H3(gen_name, style={
                        'color': GENERATION_COLORS[gen_name], 
                        'marginBottom': 25,
                        'fontSize': 28,
                        'fontWeight': 'bold'
                    })
                ], style={'borderBottom': f'3px solid {GENERATION_COLORS[gen_name]}', 'marginBottom': 30}),
                
                # Main parameters section
                html.Div([
                    # Left column - Adoption Rates
                    html.Div([
                        html.Div([
                            html.H5("Adoption Rate", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"2025 Adoption Rate: {data['adoption_2025']:.0f}%", 
                                          id={'type': 'label-adoption-2025', 'generation': gen_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'adoption-2025', 'generation': gen_name},
                                    min=0, max=100, value=data['adoption_2025'],
                                    step=1,
                                    marks={i: {'label': f'{i}%', 'style': {'fontSize': 12}} for i in range(0, 101, 20)},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Middle column - Demographics
                    html.Div([
                        html.Div([
                            html.H5("Demographics", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"Population (millions): {data['population']:.0f}M", 
                                          id={'type': 'label-population', 'generation': gen_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'population', 'generation': gen_name},
                                    min=25, max=200, value=data['population'],
                                    step=1,
                                    marks={i: {'label': f'{i}M', 'style': {'fontSize': 12}} for i in [25, 50, 75, 100, 125, 150, 175, 200]},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 25}),
                            
                            html.Div([
                                html.Label(f"Annual Spending per Person: ${data['annual_spending']:.0f}", 
                                          id={'type': 'label-spending', 'generation': gen_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'spending', 'generation': gen_name},
                                    min=500, max=100000, value=data['annual_spending'],
                                    step=100,
                                    marks={i: {'label': f'${i/1000:.0f}k', 'style': {'fontSize': 12}} for i in [500, 10000, 25000, 50000, 75000, 100000]},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Right column - Behavior
                    html.Div([
                        html.Div([
                            html.H5("Agent Usage Behavior", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"% of Purchases via Agents: {data['pct_via_agents']:.1f}%", 
                                          id={'type': 'label-pct-agents', 'generation': gen_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'pct-agents', 'generation': gen_name},
                                    min=0, max=100, value=data['pct_via_agents'],
                                    step=0.5,
                                    marks={i: {'label': f'{i}%', 'style': {'fontSize': 12}} for i in range(0, 101, 20)},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Growth rate modifier control
                    html.Div([
                        html.Div([
                            html.H5("Growth Variability", style={
                                'marginBottom': 10,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            html.P("Controls randomness in projections", style={
                                'fontSize': 14, 
                                'color': '#666',
                                'marginBottom': 15
                            }),
                            html.Div([
                                html.Label("Growth Rate Modifier:", style={
                                    'fontSize': 16, 
                                    'fontWeight': '500',
                                    'color': '#555',
                                    'marginBottom': 10
                                }),
                                html.Div([
                                    html.Div([
                                        html.Span("Conservative", style={'fontSize': 12, 'color': '#666'}),
                                        html.Span("Aggressive", style={'fontSize': 12, 'float': 'right', 'color': '#666'})
                                    ], style={'marginBottom': 5}),
                                    dcc.Slider(
                                        id={'type': 'growth-modifier', 'generation': gen_name},
                                        min=-75, max=100, value=0,
                                        step=5,
                                        marks={-75: {'label': '-75%', 'style': {'fontSize': 12}},
                                               -50: {'label': '-50%', 'style': {'fontSize': 12}}, 
                                               -25: {'label': '-25%', 'style': {'fontSize': 12}},
                                               0: {'label': '0%', 'style': {'fontSize': 12}}, 
                                               25: {'label': '+25%', 'style': {'fontSize': 12}},
                                               50: {'label': '+50%', 'style': {'fontSize': 12}},
                                               75: {'label': '+75%', 'style': {'fontSize': 12}},
                                               100: {'label': '+100%', 'style': {'fontSize': 12}}},
                                        tooltip={"placement": "bottom", "always_visible": False}
                                    )
                                ])
                            ])
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top'})
                ]),
                
                # Expandable growth rates section
                html.Details([
                    html.Summary("📈 Advanced: Year-over-Year Growth Rates", 
                                style={
                                    'cursor': 'pointer', 
                                    'fontSize': 16, 
                                    'fontWeight': 'bold', 
                                    'marginTop': 30, 
                                    'marginBottom': 15, 
                                    'color': '#555',
                                    'padding': '10px 15px',
                                    'backgroundColor': '#e9ecef',
                                    'borderRadius': 5
                                }),
                    
                    html.Div([
                        html.Div([
                            # Population growth
                            html.Div([
                                html.Label("Population Growth Rates (%):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['population_growth'], 
                                                        f'pop-growth-{gen_name}')
                            ], style={'marginBottom': 20}),
                            
                            # Spending growth
                            html.Div([
                                html.Label("Annual Spending Growth Rates (%):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['spending_growth'], 
                                                        f'spend-growth-{gen_name}')
                            ], style={'marginBottom': 20}),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '4%'}),
                        
                        html.Div([
                            # Adoption growth
                            html.Div([
                                html.Label("Adoption Rate Growth (percentage points):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['adoption_growth'], 
                                                        f'adopt-growth-{gen_name}')
                            ], style={'marginBottom': 20}),
                            
                            # Agent usage growth
                            html.Div([
                                html.Label("Agent Usage Growth (percentage points):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['agent_usage_growth'], 
                                                        f'agent-growth-{gen_name}')
                            ], style={'marginBottom': 20}),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
                    ], style={
                        'backgroundColor': '#f8f9fa', 
                        'padding': 25, 
                        'borderRadius': 8,
                        'border': '1px solid #dee2e6',
                        'marginTop': 10
                    })
                ]),
                
                html.Hr(style={
                    'marginTop': 40, 
                    'marginBottom': 40,
                    'border': 'none',
                    'borderTop': '2px solid #e9ecef'
                })
            ], style={
                'marginBottom': 30,
                'padding': '30px',
                'backgroundColor': 'white',
                'borderRadius': 10,
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
            })
        )
    
    return html.Div(controls)

def create_industry_controls():
    """Create comprehensive controls for each industry"""
    controls = []
    year_labels = ['2026', '2027', '2028', '2029', '2030']
    
    for industry_name, data in initial_industry_data.items():
        controls.append(
            html.Div([
                html.Div([
                    html.H3(industry_name, style={
                        'color': INDUSTRY_COLORS.get(industry_name if industry_name != 'Healthcare' else 'Healthcare (Business)', '#666'), 
                        'marginBottom': 25,
                        'fontSize': 28,
                        'fontWeight': 'bold'
                    })
                ], style={'borderBottom': f'3px solid {INDUSTRY_COLORS.get(industry_name if industry_name != "Healthcare" else "Healthcare (Business)", "#666")}', 'marginBottom': 30}),
                
                # Main parameters section
                html.Div([
                    # Left column - Spending
                    html.Div([
                        html.Div([
                            html.H5("Total Business Spending", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"2025 Total Spending: ${data['spending_2025']:.0f}B", 
                                          id={'type': 'label-industry-spending', 'industry': industry_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'industry-spending', 'industry': industry_name},
                                    min=0, max=20000, value=data['spending_2025'],
                                    step=100,
                                    marks={i: {'label': f'${i/1000:.0f}T' if i >= 1000 else f'${i}B', 'style': {'fontSize': 11}} 
                                          for i in [0, 5000, 10000, 15000, 20000]},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Middle left column - Adoption
                    html.Div([
                        html.Div([
                            html.H5("Adoption Rate", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"2025 Adoption Rate: {data['adoption_2025']:.0f}%", 
                                          id={'type': 'label-industry-adoption', 'industry': industry_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'industry-adoption', 'industry': industry_name},
                                    min=0, max=50, value=data['adoption_2025'],
                                    step=1,
                                    marks={i: {'label': f'{i}%', 'style': {'fontSize': 12}} 
                                          for i in range(0, 51, 10)},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Middle right column - Suitability
                    html.Div([
                        html.Div([
                            html.H5("Agentic Commerce Suitability", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"% Suitable for Agents: {data['pct_suitable']:.0f}%", 
                                          id={'type': 'label-industry-suitable', 'industry': industry_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'industry-suitable', 'industry': industry_name},
                                    min=0, max=60, value=data['pct_suitable'],
                                    step=1,
                                    marks={i: {'label': f'{i}%', 'style': {'fontSize': 12}} 
                                          for i in range(0, 61, 10)},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Right column - Risk Tolerance
                    html.Div([
                        html.Div([
                            html.H5("Risk Tolerance", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"Risk Tolerance: {data['risk_tolerance']:.0f}%", 
                                          id={'type': 'label-industry-risk', 'industry': industry_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'industry-risk', 'industry': industry_name},
                                    min=0, max=100, value=data['risk_tolerance'],
                                    step=5,
                                    marks={0: 'Conservative', 50: 'Moderate', 100: 'Innovative'},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top'})
                ]),
                
                # Expandable growth rates section
                html.Details([
                    html.Summary("📈 Advanced: Year-over-Year Growth Rates", 
                                style={
                                    'cursor': 'pointer', 
                                    'fontSize': 16, 
                                    'fontWeight': 'bold', 
                                    'marginTop': 30, 
                                    'marginBottom': 15, 
                                    'color': '#555',
                                    'padding': '10px 15px',
                                    'backgroundColor': '#e9ecef',
                                    'borderRadius': 5
                                }),
                    
                    html.Div([
                        html.Div([
                            # Spending growth
                            html.Div([
                                html.Label("Total Business Spending Growth Rates (%):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['spending_growth'], 
                                                        f'ind-spend-growth-{industry_name}')
                            ], style={'marginBottom': 20}),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '4%'}),
                        
                        html.Div([
                            # Adoption growth
                            html.Div([
                                html.Label("Adoption Rate Growth (percentage points):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['adoption_growth'], 
                                                        f'ind-adopt-growth-{industry_name}')
                            ], style={'marginBottom': 20}),
                            
                            # Suitability growth
                            html.Div([
                                html.Label("Suitability Growth (percentage points):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['suitability_growth'], 
                                                        f'ind-suit-growth-{industry_name}')
                            ], style={'marginBottom': 20}),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
                    ], style={
                        'backgroundColor': '#f8f9fa', 
                        'padding': 25, 
                        'borderRadius': 8,
                        'border': '1px solid #dee2e6',
                        'marginTop': 10
                    })
                ]),
                
                html.Hr(style={
                    'marginTop': 40, 
                    'marginBottom': 40,
                    'border': 'none',
                    'borderTop': '2px solid #e9ecef'
                })
            ], style={
                'marginBottom': 30,
                'padding': '30px',
                'backgroundColor': 'white',
                'borderRadius': 10,
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
            })
        )
    
    return html.Div(controls)

def create_government_controls():
    """Create comprehensive controls for government segments"""
    controls = []
    year_labels = ['2026', '2027', '2028', '2029', '2030']
    
    for gov_name, data in initial_gov_data.items():
        controls.append(
            html.Div([
                html.Div([
                    html.H3(gov_name, style={
                        'color': GOVERNMENT_COLORS.get(gov_name, '#666'), 
                        'marginBottom': 25,
                        'fontSize': 28,
                        'fontWeight': 'bold'
                    })
                ], style={'borderBottom': f'3px solid {GOVERNMENT_COLORS[gov_name]}', 'marginBottom': 30}),
                
                # Main parameters section
                html.Div([
                    # Left column - Spending
                    html.Div([
                        html.Div([
                            html.H5("Total Government Spending", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"2025 Total Spending: ${data['spending_2025']:.0f}B", 
                                          id={'type': 'label-gov-spending', 'government': gov_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'gov-spending', 'government': gov_name},
                                    min=0, max=10000, value=data['spending_2025'],
                                    step=100,
                                    marks={i: {'label': f'${i/1000:.0f}T' if i >= 1000 else f'${i}B', 'style': {'fontSize': 11}} 
                                          for i in [0, 2000, 4000, 6000, 8000, 10000]},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Middle left column - Adoption
                    html.Div([
                        html.Div([
                            html.H5("Adoption Rate", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"2025 Adoption Rate: {data['adoption_2025']:.1f}%", 
                                          id={'type': 'label-gov-adoption', 'government': gov_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'gov-adoption', 'government': gov_name},
                                    min=0, max=20, value=data['adoption_2025'],
                                    step=0.5,
                                    marks={i: {'label': f'{i}%', 'style': {'fontSize': 12}} 
                                          for i in range(0, 21, 5)},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Middle right column - Suitability
                    html.Div([
                        html.Div([
                            html.H5("Agentic Commerce Suitability", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"% Suitable for Agents: {data['pct_suitable']:.0f}%", 
                                          id={'type': 'label-gov-suitable', 'government': gov_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'gov-suitable', 'government': gov_name},
                                    min=0, max=30, value=data['pct_suitable'],
                                    step=1,
                                    marks={i: {'label': f'{i}%', 'style': {'fontSize': 12}} 
                                          for i in range(0, 31, 5)},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),
                    
                    # Right column - Regulatory Readiness
                    html.Div([
                        html.Div([
                            html.H5("Regulatory Readiness", style={
                                'marginBottom': 15,
                                'fontSize': 18,
                                'fontWeight': 'bold',
                                'color': '#333'
                            }),
                            
                            html.Div([
                                html.Label(f"Regulatory Readiness: {data['regulatory_readiness']:.0f}%", 
                                          id={'type': 'label-gov-regulatory', 'government': gov_name},
                                          style={
                                              'fontSize': 16, 
                                              'fontWeight': '500',
                                              'color': '#555',
                                              'marginBottom': 10
                                          }),
                                dcc.Slider(
                                    id={'type': 'gov-regulatory', 'government': gov_name},
                                    min=0, max=100, value=data['regulatory_readiness'],
                                    step=5,
                                    marks={0: 'Low', 50: 'Medium', 100: 'High'},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], style={'marginBottom': 20}),
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': 20,
                            'borderRadius': 8,
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                        })
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top'})
                ]),
                
                # Expandable growth rates section
                html.Details([
                    html.Summary("📈 Advanced: Year-over-Year Growth Rates", 
                                style={
                                    'cursor': 'pointer', 
                                    'fontSize': 16, 
                                    'fontWeight': 'bold', 
                                    'marginTop': 30, 
                                    'marginBottom': 15, 
                                    'color': '#555',
                                    'padding': '10px 15px',
                                    'backgroundColor': '#e9ecef',
                                    'borderRadius': 5
                                }),
                    
                    html.Div([
                        html.Div([
                            # Spending growth
                            html.Div([
                                html.Label("Spending Growth Rates (%):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['spending_growth'], 
                                                        f'gov-spend-growth-{gov_name}')
                            ], style={'marginBottom': 20}),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '4%'}),
                        
                        html.Div([
                            # Adoption growth
                            html.Div([
                                html.Label("Adoption Rate Growth (percentage points):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['adoption_growth'], 
                                                        f'gov-adopt-growth-{gov_name}')
                            ], style={'marginBottom': 20}),
                            
                            # Suitability growth
                            html.Div([
                                html.Label("Suitability Growth (percentage points):", style={
                                    'fontSize': 15, 
                                    'fontWeight': 'bold',
                                    'color': '#444',
                                    'marginBottom': 10
                                }),
                                create_growth_rate_inputs(year_labels, data['suitability_growth'], 
                                                        f'gov-suit-growth-{gov_name}')
                            ], style={'marginBottom': 20}),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
                    ], style={
                        'backgroundColor': '#f8f9fa', 
                        'padding': 25, 
                        'borderRadius': 8,
                        'border': '1px solid #dee2e6',
                        'marginTop': 10
                    })
                ]),
                
                html.Hr(style={
                    'marginTop': 40, 
                    'marginBottom': 40,
                    'border': 'none',
                    'borderTop': '2px solid #e9ecef'
                })
            ], style={
                'marginBottom': 30,
                'padding': '30px',
                'backgroundColor': 'white',
                'borderRadius': 10,
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
            })
        )
    
    return html.Div(controls)

def create_fee_structure_controls():
    """Create controls for fee structure including growth rates"""
    year_labels = ['2026', '2027', '2028', '2029', '2030']
    
    return html.Div([
        html.H3("💰 Revenue Distribution Settings", style={'color': '#2E86AB', 'marginBottom': 30}),
        html.P("Adjust the percentage fees charged by each stakeholder in the agentic commerce ecosystem.", 
               style={'fontSize': 16, 'marginBottom': 30}),
        
        html.Div([
            # Retailer/Merchant control (inverse of total fees)
            html.Div([
                html.H4("Retailer/Merchant Share", style={'color': STAKEHOLDER_COLORS['Retailer/Merchant'], 'marginBottom': 15}),
                html.P("The percentage of revenue retained by retailers after all fees", style={'fontSize': 14, 'color': '#666'}),
                html.Div([
                    html.Label("This is automatically calculated as: 100% - Total Fees", 
                              style={'fontSize': 14, 'fontStyle': 'italic', 'color': '#888'}),
                    html.Div(id='retailer-share-display', style={'fontSize': 20, 'fontWeight': 'bold', 'color': STAKEHOLDER_COLORS['Retailer/Merchant']})
                ])
            ], style={'marginBottom': 40, 'padding': 20, 'backgroundColor': '#f0f8ff', 'borderRadius': 5}),
            
            html.Hr(),
            
            # Payment Processing
            html.Div([
                html.H4("Payment Processing", style={'color': STAKEHOLDER_COLORS['Payment Processing'], 'marginBottom': 15}),
                html.P("Transaction processing fees charged by payment providers", style={'fontSize': 14, 'color': '#666'}),
                html.Label(f"Fee Rate: {initial_fees['payment_processing']:.1f}%", 
                          id='label-payment-rate',
                          style={'fontSize': 14, 'fontWeight': 'bold'}),
                dcc.Slider(
                    id='payment-rate',
                    min=0, max=10, value=initial_fees['payment_processing'],
                    step=0.1,
                    marks={i: f'{i}%' for i in range(0, 11, 2)},
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
                html.Details([
                    html.Summary("Growth Rates", style={'cursor': 'pointer', 'fontSize': 12}),
                    create_growth_rate_inputs(year_labels, initial_fees['payment_growth'], 'payment-fee-growth')
                ], style={'marginTop': 10})
            ], style={'marginBottom': 40}),
            
            # AI Agent Platform
            html.Div([
                html.H4("AI Agent Platform", style={'color': STAKEHOLDER_COLORS['AI Agent Platform'], 'marginBottom': 15}),
                html.P("Platform fees for AI agent services and infrastructure", style={'fontSize': 14, 'color': '#666'}),
                html.Label(f"Fee Rate: {initial_fees['ai_agent_platform']:.1f}%", 
                          id='label-ai-rate',
                          style={'fontSize': 14, 'fontWeight': 'bold'}),
                dcc.Slider(
                    id='ai-rate',
                    min=0, max=10, value=initial_fees['ai_agent_platform'],
                    step=0.1,
                    marks={i: f'{i}%' for i in range(0, 11, 2)},
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
                html.Details([
                    html.Summary("Growth Rates", style={'cursor': 'pointer', 'fontSize': 12}),
                    create_growth_rate_inputs(year_labels, initial_fees['ai_growth'], 'ai-fee-growth')
                ], style={'marginTop': 10})
            ], style={'marginBottom': 40}),
            
            # Advertising/Placement
            html.Div([
                html.H4("Advertising & Placement", style={'color': STAKEHOLDER_COLORS['Advertising/Placement'], 'marginBottom': 15}),
                html.P("Fees for product placement and advertising in agent recommendations", style={'fontSize': 14, 'color': '#666'}),
                html.Label(f"Fee Rate: {initial_fees['advertising_placement']:.1f}%", 
                          id='label-ad-rate',
                          style={'fontSize': 14, 'fontWeight': 'bold'}),
                dcc.Slider(
                    id='ad-rate',
                    min=0, max=10, value=initial_fees['advertising_placement'],
                    step=0.1,
                    marks={i: f'{i}%' for i in range(0, 11, 2)},
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
                html.Details([
                    html.Summary("Growth Rates", style={'cursor': 'pointer', 'fontSize': 12}),
                    create_growth_rate_inputs(year_labels, initial_fees['advertising_growth'], 'ad-fee-growth')
                ], style={'marginTop': 10})
            ], style={'marginBottom': 40}),
            
            # Data & Analytics
            html.Div([
                html.H4("Data & Analytics", style={'color': STAKEHOLDER_COLORS['Data & Analytics'], 'marginBottom': 15}),
                html.P("Fees for data insights and analytics services", style={'fontSize': 14, 'color': '#666'}),
                html.Label(f"Fee Rate: {initial_fees['data_analytics']:.1f}%", 
                          id='label-data-rate',
                          style={'fontSize': 14, 'fontWeight': 'bold'}),
                dcc.Slider(
                    id='data-rate',
                    min=0, max=5, value=initial_fees['data_analytics'],
                    step=0.1,
                    marks={i: f'{i}%' for i in range(0, 6)},
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
                html.Details([
                    html.Summary("Growth Rates", style={'cursor': 'pointer', 'fontSize': 12}),
                    create_growth_rate_inputs(year_labels, initial_fees['data_growth'], 'data-fee-growth')
                ], style={'marginTop': 10})
            ], style={'marginBottom': 40}),
            
            # Total fees summary
            html.Div([
                html.H4("Total Fees Summary", style={'color': '#333', 'marginBottom': 15}),
                html.Div(id='total-fees-display', style={'fontSize': 18, 'fontWeight': 'bold'})
            ], style={'padding': 20, 'backgroundColor': '#f9f9f9', 'borderRadius': 5})
        ])
    ])

# Create the original layout
original_layout = html.Div([
    # Header
    html.Div([
        html.H1("Enhanced Agentic Commerce Market Projection Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': 10}),
        html.H3("Consumer + Business + Government Analysis 2025-2030", 
                style={'textAlign': 'center', 'color': '#666', 'marginTop': 0}),
        html.Hr()
    ]),
    
    # Main container
    html.Div([
        # Control Panel (Full width top section)
        html.Div([
            dcc.Tabs(id='control-tabs', value='generation-tab', children=[
                dcc.Tab(label='Consumer Spending', value='generation-tab', children=[
                    html.Div([
                        html.Div([
                            html.H2("👥 Generation-Specific Parameters", style={
                                'color': '#2E86AB', 
                                'fontSize': 32,
                                'fontWeight': 'bold',
                                'marginBottom': 15
                            }),
                            html.P("Adjust adoption rates, demographics, behavior patterns, and growth rates for each generation.", 
                                   style={
                                       'fontSize': 18, 
                                       'color': '#555',
                                       'lineHeight': 1.6,
                                       'maxWidth': '800px'
                                   })
                        ], style={
                            'textAlign': 'left',
                            'marginBottom': 40,
                            'paddingBottom': 30,
                            'borderBottom': '3px solid #e9ecef'
                        }),
                        create_generation_controls()
                    ], style={
                        'padding': 40,
                        'backgroundColor': '#f8f9fa',
                        'minHeight': '100vh'
                    })
                ]),
                
                dcc.Tab(label='Business Spending', value='business-tab', children=[
                    html.Div([
                        html.Div([
                            html.H2("🏢 Industry-Specific Parameters", style={
                                'color': '#1f77b4', 
                                'fontSize': 32,
                                'fontWeight': 'bold',
                                'marginBottom': 15
                            }),
                            html.P("Adjust total business spending, adoption rates, suitability, and risk tolerance for each industry sector.", 
                                   style={
                                       'fontSize': 18, 
                                       'color': '#555',
                                       'lineHeight': 1.6,
                                       'maxWidth': '800px'
                                   })
                        ], style={
                            'textAlign': 'left',
                            'marginBottom': 40,
                            'paddingBottom': 30,
                            'borderBottom': '3px solid #e9ecef'
                        }),
                        create_industry_controls()
                    ], style={
                        'padding': 40,
                        'backgroundColor': '#f8f9fa',
                        'minHeight': '100vh'
                    })
                ]),
                
                dcc.Tab(label='Government Spending', value='government-tab', children=[
                    html.Div([
                        html.Div([
                            html.H2("🏛️ Government Segment Parameters", style={
                                'color': '#393b79', 
                                'fontSize': 32,
                                'fontWeight': 'bold',
                                'marginBottom': 15
                            }),
                            html.P("Adjust IT spending, adoption rates, suitability, and regulatory readiness for government segments.", 
                                   style={
                                       'fontSize': 18, 
                                       'color': '#555',
                                       'lineHeight': 1.6,
                                       'maxWidth': '800px'
                                   })
                        ], style={
                            'textAlign': 'left',
                            'marginBottom': 40,
                            'paddingBottom': 30,
                            'borderBottom': '3px solid #e9ecef'
                        }),
                        create_government_controls()
                    ], style={
                        'padding': 40,
                        'backgroundColor': '#f8f9fa',
                        'minHeight': '100vh'
                    })
                ]),
                
                dcc.Tab(label='Fee Structure', value='fee-tab', children=[
                    html.Div([
                        create_fee_structure_controls()
                    ], style={'padding': 30})
                ]),
                
                dcc.Tab(label='Model Settings', value='model-tab', children=[
                    html.Div([
                        html.H3("🎲 Model Configuration", style={'color': '#2E86AB', 'marginTop': 30}),
                        
                        html.Div([
                            html.Label("Random Seed (for scenario variations):", style={'fontWeight': 'bold', 'fontSize': 16}),
                            html.P("Change this value to generate different market scenarios", style={'fontSize': 14, 'color': '#666'}),
                            dcc.Input(id='random-seed', type='number', value=42, min=1, max=9999,
                                     style={'marginLeft': 10, 'width': 150, 'fontSize': 16, 'padding': 10})
                        ], style={'marginBottom': 30}),
                        
                        html.Div([
                            html.H4("Growth Rate Modifier Settings", style={'color': '#F18F01', 'marginTop': 40}),
                            html.P("The growth rate modifier adds variability to projections. It uses a beta distribution with right skew:", 
                                   style={'fontSize': 14}),
                            html.Ul([
                                html.Li("Range: -100% to +100% of base growth rate", style={'fontSize': 14}),
                                html.Li("Distribution: Right-skewed (positive values more likely)", style={'fontSize': 14}),
                                html.Li("Example: +50% modifier on 10% growth = 15% actual growth", style={'fontSize': 14}),
                                html.Li("Set individual modifiers in each segment tab", style={'fontSize': 14})
                            ])
                        ])
                    ], style={'padding': 30})
                ])
            ], style={'backgroundColor': '#f5f5f5'}),
            
            # Update Button
            html.Div([
                html.Button('Update Projections', id='update-button', n_clicks=0,
                           style={'backgroundColor': '#2E86AB', 'color': 'white', 
                                 'fontSize': 18, 'padding': '15px 40px', 'border': 'none',
                                 'borderRadius': 5, 'cursor': 'pointer', 'display': 'block',
                                 'margin': '30px auto'})
            ])
        ], style={'backgroundColor': '#f5f5f5', 'marginBottom': 30}),
        
        # Visualization Area
        html.Div([
            # Summary Cards
            html.Div(id='summary-cards', style={'marginBottom': 30}),
            
            # Main Charts
            dcc.Tabs([
                dcc.Tab(label='Total Economy', children=[
                    html.Div([
                        # Row 1: Total Market and Sector Breakdown
                        html.Div([
                            dcc.Graph(id='total-economy-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='sector-breakdown-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 2: Sector growth and contribution
                        html.Div([
                            dcc.Graph(id='sector-growth-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='sector-contribution-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 3: Consumer vs Business vs Government trends
                        html.Div([
                            dcc.Graph(id='segment-trends-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='adoption-comparison-chart', style={'width': '50%', 'display': 'inline-block'})
                        ])
                    ], style={'padding': 20})
                ]),
                
                dcc.Tab(label='Consumer Analysis', children=[
                    html.Div([
                        # Row 1: Total Market and Growth Rate
                        html.Div([
                            dcc.Graph(id='consumer-market-chart', style={'width': '60%', 'display': 'inline-block'}),
                            dcc.Graph(id='consumer-growth-rate-chart', style={'width': '40%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 2: Generation breakdowns
                        html.Div([
                            dcc.Graph(id='generation-stack-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='generation-pie-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 3: Adoption and spending patterns
                        html.Div([
                            dcc.Graph(id='adoption-evolution-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='spending-per-capita-chart', style={'width': '50%', 'display': 'inline-block'})
                        ])
                    ], style={'padding': 20})
                ]),
                
                dcc.Tab(label='Business Analysis', children=[
                    html.Div([
                        # Row 1: Industry market sizes
                        html.Div([
                            dcc.Graph(id='industry-market-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='industry-growth-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 2: Industry breakdown and adoption
                        html.Div([
                            dcc.Graph(id='industry-breakdown-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='industry-adoption-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 3: Risk vs adoption and suitability
                        html.Div([
                            dcc.Graph(id='risk-adoption-scatter', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='industry-suitability-chart', style={'width': '50%', 'display': 'inline-block'})
                        ])
                    ], style={'padding': 20})
                ]),
                
                dcc.Tab(label='Government Analysis', children=[
                    html.Div([
                        # Row 1: Government segment sizes
                        html.Div([
                            dcc.Graph(id='government-market-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='government-growth-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 2: Segment breakdown and regulatory readiness
                        html.Div([
                            dcc.Graph(id='government-breakdown-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='regulatory-readiness-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 3: Adoption patterns and procurement cycles
                        html.Div([
                            dcc.Graph(id='gov-adoption-evolution', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='gov-suitability-chart', style={'width': '50%', 'display': 'inline-block'})
                        ])
                    ], style={'padding': 20})
                ]),
                
                dcc.Tab(label='Revenue Distribution', children=[
                    html.Div([
                        # Row 1: Revenue distribution and percentage
                        html.Div([
                            dcc.Graph(id='revenue-distribution-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='revenue-percentage-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 2: Fee evolution and per-transaction
                        html.Div([
                            dcc.Graph(id='fee-evolution-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='per-transaction-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 3: Retailer vs fees and fee breakdown
                        html.Div([
                            dcc.Graph(id='retailer-vs-fees-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='fee-breakdown-2030', style={'width': '50%', 'display': 'inline-block'})
                        ])
                    ], style={'padding': 20})
                ]),
                
                dcc.Tab(label='Data Tables', children=[
                    html.Div([
                        html.H3("Market Projections by Segment", style={'marginTop': 20}),
                        html.Div(id='market-data-table'),
                        
                        html.H3("Revenue Distribution Details", style={'marginTop': 40}),
                        html.Div(id='revenue-data-table'),
                        
                        html.H3("Key Metrics Summary", style={'marginTop': 40}),
                        html.Div(id='metrics-summary-table')
                    ], style={'padding': 20})
                ])
            ])
        ])
    ]),
    
    # Store for data
    dcc.Store(id='projection-data', data={
        'market': initial_market_df.to_dict(),
        'distribution': initial_distribution_df.to_dict()
    })
])

# Set the layout first
app.layout = original_layout

# Add AI chat with immediate user feedback and streaming responses
try:
    from add_chat_optimized import add_chat_optimized
    add_chat_optimized(app)
except Exception as e:
    print(f"⚠️  Could not add AI chat button: {e}")

# Callback to update retailer share and total fees display
@app.callback(
    [Output('retailer-share-display', 'children'),
     Output('total-fees-display', 'children')],
    [Input('payment-rate', 'value'),
     Input('ai-rate', 'value'),
     Input('ad-rate', 'value'),
     Input('data-rate', 'value')]
)
def update_fee_displays(payment_rate, ai_rate, ad_rate, data_rate):
    """Update the retailer share and total fees displays"""
    total_fees = payment_rate + ai_rate + ad_rate + data_rate
    retailer_share = 100 - total_fees
    
    return (
        f"Retailer Share: {retailer_share:.1f}%",
        f"Total Fees: {total_fees:.1f}% (Retailer gets {retailer_share:.1f}%)"
    )

# Update all labels callback
@app.callback(
    [Output({'type': 'label-adoption-2025', 'generation': ALL}, 'children'),
     Output({'type': 'label-population', 'generation': ALL}, 'children'),
     Output({'type': 'label-spending', 'generation': ALL}, 'children'),
     Output({'type': 'label-pct-agents', 'generation': ALL}, 'children'),
     Output({'type': 'label-industry-spending', 'industry': ALL}, 'children'),
     Output({'type': 'label-industry-adoption', 'industry': ALL}, 'children'),
     Output({'type': 'label-industry-suitable', 'industry': ALL}, 'children'),
     Output({'type': 'label-industry-risk', 'industry': ALL}, 'children'),
     Output({'type': 'label-gov-spending', 'government': ALL}, 'children'),
     Output({'type': 'label-gov-adoption', 'government': ALL}, 'children'),
     Output({'type': 'label-gov-suitable', 'government': ALL}, 'children'),
     Output({'type': 'label-gov-regulatory', 'government': ALL}, 'children'),
     Output('label-payment-rate', 'children'),
     Output('label-ai-rate', 'children'),
     Output('label-ad-rate', 'children'),
     Output('label-data-rate', 'children')],
    [Input({'type': 'adoption-2025', 'generation': ALL}, 'value'),
     Input({'type': 'population', 'generation': ALL}, 'value'),
     Input({'type': 'spending', 'generation': ALL}, 'value'),
     Input({'type': 'pct-agents', 'generation': ALL}, 'value'),
     Input({'type': 'industry-spending', 'industry': ALL}, 'value'),
     Input({'type': 'industry-adoption', 'industry': ALL}, 'value'),
     Input({'type': 'industry-suitable', 'industry': ALL}, 'value'),
     Input({'type': 'industry-risk', 'industry': ALL}, 'value'),
     Input({'type': 'gov-spending', 'government': ALL}, 'value'),
     Input({'type': 'gov-adoption', 'government': ALL}, 'value'),
     Input({'type': 'gov-suitable', 'government': ALL}, 'value'),
     Input({'type': 'gov-regulatory', 'government': ALL}, 'value'),
     Input('payment-rate', 'value'),
     Input('ai-rate', 'value'),
     Input('ad-rate', 'value'),
     Input('data-rate', 'value')]
)
def update_all_labels(adoption_2025, population, spending, pct_agents,
                     ind_spending, ind_adoption, ind_suitable, ind_risk,
                     gov_spending, gov_adoption, gov_suitable, gov_regulatory,
                     payment_rate, ai_rate, ad_rate, data_rate):
    """Update all slider labels"""
    # Generation labels
    labels_2025 = [f"2025 Adoption Rate: {val:.0f}%" for val in adoption_2025]
    labels_pop = [f"Population (millions): {val:.0f}M" for val in population]
    labels_spend = [f"Annual Spending per Person: ${val:.0f}" for val in spending]
    labels_pct = [f"% of Purchases via Agents: {val:.1f}%" for val in pct_agents]
    
    # Industry labels
    labels_ind_spend = [f"2025 Total Spending: ${val:.0f}B" for val in ind_spending]
    labels_ind_adopt = [f"2025 Adoption Rate: {val:.0f}%" for val in ind_adoption]
    labels_ind_suit = [f"% Suitable for Agents: {val:.0f}%" for val in ind_suitable]
    labels_ind_risk = [f"Risk Tolerance: {val:.0f}%" for val in ind_risk]
    
    # Government labels
    labels_gov_spend = [f"2025 Total Spending: ${val:.0f}B" for val in gov_spending]
    labels_gov_adopt = [f"2025 Adoption Rate: {val:.1f}%" for val in gov_adoption]
    labels_gov_suit = [f"% Suitable for Agents: {val:.0f}%" for val in gov_suitable]
    labels_gov_reg = [f"Regulatory Readiness: {val:.0f}%" for val in gov_regulatory]
    
    return (labels_2025, labels_pop, labels_spend, labels_pct,
            labels_ind_spend, labels_ind_adopt, labels_ind_suit, labels_ind_risk,
            labels_gov_spend, labels_gov_adopt, labels_gov_suit, labels_gov_reg,
            f"Fee Rate: {payment_rate:.1f}%",
            f"Fee Rate: {ai_rate:.1f}%",
            f"Fee Rate: {ad_rate:.1f}%",
            f"Fee Rate: {data_rate:.1f}%")

# Main update projections callback
@app.callback(
    Output('projection-data', 'data'),
    [Input('update-button', 'n_clicks')],
    [State('random-seed', 'value'),
     # Fee rates
     State('payment-rate', 'value'),
     State('ai-rate', 'value'),
     State('ad-rate', 'value'),
     State('data-rate', 'value'),
     # Generation base values
     State({'type': 'adoption-2025', 'generation': ALL}, 'value'),
     State({'type': 'population', 'generation': ALL}, 'value'),
     State({'type': 'spending', 'generation': ALL}, 'value'),
     State({'type': 'pct-agents', 'generation': ALL}, 'value'),
     State({'type': 'adoption-2025', 'generation': ALL}, 'id'),
     # Industry base values
     State({'type': 'industry-spending', 'industry': ALL}, 'value'),
     State({'type': 'industry-adoption', 'industry': ALL}, 'value'),
     State({'type': 'industry-suitable', 'industry': ALL}, 'value'),
     State({'type': 'industry-risk', 'industry': ALL}, 'value'),
     State({'type': 'industry-spending', 'industry': ALL}, 'id'),
     # Government base values
     State({'type': 'gov-spending', 'government': ALL}, 'value'),
     State({'type': 'gov-adoption', 'government': ALL}, 'value'),
     State({'type': 'gov-suitable', 'government': ALL}, 'value'),
     State({'type': 'gov-regulatory', 'government': ALL}, 'value'),
     State({'type': 'gov-spending', 'government': ALL}, 'id'),
     # Growth modifiers
     State({'type': 'growth-modifier', 'generation': ALL}, 'value'),
     # Growth rates for all segments
     State({'type': ALL, 'index': ALL}, 'value'),
     State({'type': ALL, 'index': ALL}, 'id')]
)
def update_projections(n_clicks, seed, payment_rate, ai_rate, ad_rate, data_rate,
                      adoption_2025_values, population_values,
                      spending_values, pct_agents_values, adoption_ids,
                      ind_spending_values, ind_adoption_values,
                      ind_suitable_values, ind_risk_values, ind_ids,
                      gov_spending_values, gov_adoption_values,
                      gov_suitable_values, gov_regulatory_values, gov_ids,
                      growth_modifiers, all_growth_values, all_growth_ids):
    """Calculate new projections based on all parameters"""
    
    # Use default values if None
    seed = seed or 42
    payment_rate = payment_rate or 3.0
    ai_rate = ai_rate or 1.5
    ad_rate = ad_rate or 2.0
    data_rate = data_rate or 0.5
    
    # Create new projection
    projection = ExtendedAgenticCommerceProjection(random_seed=int(seed))
    
    # Parse growth rates from the ALL pattern matching
    growth_rates = {}
    for value, id_dict in zip(all_growth_values, all_growth_ids):
        if 'type' in id_dict and 'index' in id_dict:
            rate_type = id_dict['type']
            index = id_dict['index']
            
            if rate_type not in growth_rates:
                growth_rates[rate_type] = {}
            growth_rates[rate_type][index] = value
    
    # Update generation parameters
    gen_map = {'Gen Z': 'gen_z', 'Millennials': 'millennials', 'Gen X': 'gen_x', 'Baby Boomers': 'baby_boomers'}
    
    for i, gen_id in enumerate(adoption_ids):
        gen_name = gen_id['generation']
        gen_key = gen_map[gen_name]
        
        # Update base data
        base_attr = f"{gen_key}_base"
        if hasattr(projection, base_attr):
            base_data = getattr(projection, base_attr)
            
            # Update all base parameters
            base_data['adoption_rate']['2025_value'] = adoption_2025_values[i] / 100
            base_data['population_millions']['2025_value'] = population_values[i]
            base_data['avg_annual_spending']['2025_value'] = spending_values[i]
            base_data['pct_purchases_via_agents']['2025_value'] = pct_agents_values[i] / 100
            
            # Update growth rates if provided
            if f'pop-growth-{gen_name}' in growth_rates:
                rates = [growth_rates[f'pop-growth-{gen_name}'].get(j, 0) for j in range(5)]
                base_data['population_millions']['base_growth_rates'] = rates
            
            if f'spend-growth-{gen_name}' in growth_rates:
                rates = [growth_rates[f'spend-growth-{gen_name}'].get(j, 0) for j in range(5)]
                base_data['avg_annual_spending']['base_growth_rates'] = rates
            
            if f'adopt-growth-{gen_name}' in growth_rates:
                rates = [growth_rates[f'adopt-growth-{gen_name}'].get(j, 0) for j in range(5)]
                base_data['adoption_rate']['base_growth_rates'] = rates
            
            if f'agent-growth-{gen_name}' in growth_rates:
                rates = [growth_rates[f'agent-growth-{gen_name}'].get(j, 0) for j in range(5)]
                base_data['pct_purchases_via_agents']['base_growth_rates'] = rates
            
            # Apply growth modifier if specified
            if i < len(growth_modifiers) and growth_modifiers[i] != 0:
                # Modify the growth rates based on the modifier
                for var in ['population_millions', 'avg_annual_spending', 'adoption_rate', 'pct_purchases_via_agents']:
                    original_rates = base_data[var]['base_growth_rates']
                    modified_rates = [rate * (1 + growth_modifiers[i] / 100) for rate in original_rates]
                    base_data[var]['base_growth_rates'] = modified_rates
            
            # Regenerate projections for this generation
            setattr(projection, gen_key, projection._generate_projections(base_data))
    
    # Update industry parameters
    ind_map = {
        'Financial Services': 'financial_services',
        'Manufacturing': 'manufacturing',
        'Healthcare': 'healthcare',
        'Retail': 'retail',
        'Technology': 'technology',
        'Transportation': 'transportation',
        'Energy': 'energy',
        'Real Estate': 'real_estate'
    }
    
    for i, ind_id in enumerate(ind_ids):
        ind_name = ind_id['industry']
        ind_key = ind_map[ind_name]
        
        # Update base data
        base_attr = f"{ind_key}_base"
        if hasattr(projection, base_attr):
            base_data = getattr(projection, base_attr)
            
            # Update all base parameters
            base_data['spending_billions']['2025_value'] = ind_spending_values[i]
            base_data['adoption_rate']['2025_value'] = ind_adoption_values[i] / 100
            base_data['pct_suitable_for_agents']['2025_value'] = ind_suitable_values[i] / 100
            base_data['risk_tolerance'] = ind_risk_values[i] / 100
            
            # Update growth rates if provided
            if f'ind-spend-growth-{ind_name}' in growth_rates:
                rates = [growth_rates[f'ind-spend-growth-{ind_name}'].get(j, 0) for j in range(5)]
                base_data['spending_billions']['base_growth_rates'] = rates
            
            if f'ind-adopt-growth-{ind_name}' in growth_rates:
                rates = [growth_rates[f'ind-adopt-growth-{ind_name}'].get(j, 0) for j in range(5)]
                base_data['adoption_rate']['base_growth_rates'] = rates
            
            if f'ind-suit-growth-{ind_name}' in growth_rates:
                rates = [growth_rates[f'ind-suit-growth-{ind_name}'].get(j, 0) for j in range(5)]
                base_data['pct_suitable_for_agents']['base_growth_rates'] = rates
            
            # Regenerate projections for this industry
            setattr(projection, ind_key, projection._generate_projections(base_data))
    
    # Update government parameters
    gov_map = {
        'Federal': 'federal_gov',
        'State & Local': 'state_local_gov',
        'Defense': 'defense',
        'Healthcare (Gov)': 'gov_healthcare'
    }
    
    for i, gov_id in enumerate(gov_ids):
        gov_name = gov_id['government']
        gov_key = gov_map[gov_name]
        
        # Update base data
        base_attr = f"{gov_key}_base"
        if hasattr(projection, base_attr):
            base_data = getattr(projection, base_attr)
            
            # Update all base parameters
            base_data['spending_billions']['2025_value'] = gov_spending_values[i]
            base_data['adoption_rate']['2025_value'] = gov_adoption_values[i] / 100
            base_data['pct_suitable_for_agents']['2025_value'] = gov_suitable_values[i] / 100
            base_data['regulatory_readiness'] = gov_regulatory_values[i] / 100
            
            # Update growth rates if provided
            if f'gov-spend-growth-{gov_name}' in growth_rates:
                rates = [growth_rates[f'gov-spend-growth-{gov_name}'].get(j, 0) for j in range(5)]
                base_data['spending_billions']['base_growth_rates'] = rates
            
            if f'gov-adopt-growth-{gov_name}' in growth_rates:
                rates = [growth_rates[f'gov-adopt-growth-{gov_name}'].get(j, 0) for j in range(5)]
                base_data['adoption_rate']['base_growth_rates'] = rates
            
            if f'gov-suit-growth-{gov_name}' in growth_rates:
                rates = [growth_rates[f'gov-suit-growth-{gov_name}'].get(j, 0) for j in range(5)]
                base_data['pct_suitable_for_agents']['base_growth_rates'] = rates
            
            # Regenerate projections for this government segment
            setattr(projection, gov_key, projection._generate_projections(base_data))
    
    # Update revenue distribution
    projection.revenue_distribution_base['payment_processing']['2025_value'] = payment_rate / 100
    projection.revenue_distribution_base['ai_agent_platform']['2025_value'] = ai_rate / 100
    projection.revenue_distribution_base['advertising_placement']['2025_value'] = ad_rate / 100
    projection.revenue_distribution_base['data_analytics']['2025_value'] = data_rate / 100
    
    # Update revenue growth rates if provided
    if 'payment-fee-growth' in growth_rates:
        rates = [growth_rates['payment-fee-growth'].get(j, 0) for j in range(5)]
        projection.revenue_distribution_base['payment_processing']['base_growth_rates'] = rates
    
    if 'ai-fee-growth' in growth_rates:
        rates = [growth_rates['ai-fee-growth'].get(j, 0) for j in range(5)]
        projection.revenue_distribution_base['ai_agent_platform']['base_growth_rates'] = rates
    
    if 'ad-fee-growth' in growth_rates:
        rates = [growth_rates['ad-fee-growth'].get(j, 0) for j in range(5)]
        projection.revenue_distribution_base['advertising_placement']['base_growth_rates'] = rates
    
    if 'data-fee-growth' in growth_rates:
        rates = [growth_rates['data-fee-growth'].get(j, 0) for j in range(5)]
        projection.revenue_distribution_base['data_analytics']['base_growth_rates'] = rates
    
    # Regenerate revenue projections
    projection.revenue_distribution = projection._generate_projections(projection.revenue_distribution_base)
    
    # Calculate projections
    market_df = projection.calculate_total_market_projection()
    distribution_df = projection.calculate_revenue_distribution(market_df)
    
    # Store generation parameters for additional analysis
    gen_params = {}
    for gen_name, gen_key in gen_map.items():
        gen_data = getattr(projection, gen_key)
        gen_params[gen_name] = {
            'adoption': gen_data['adoption_rate'],
            'spending': gen_data['avg_annual_spending'],
            'pct_agents': gen_data['pct_purchases_via_agents'],
            'population': gen_data['population_millions']
        }
    
    # Store industry parameters
    ind_params = {}
    for ind_name, ind_key in ind_map.items():
        ind_data = getattr(projection, ind_key)
        ind_params[ind_name] = {
            'spending': ind_data['spending_billions'],
            'adoption': ind_data['adoption_rate'],
            'suitable': ind_data['pct_suitable_for_agents'],
            'risk_tolerance': ind_data.get('risk_tolerance', 0.5)
        }
    
    # Store government parameters
    gov_params = {}
    for gov_name, gov_key in gov_map.items():
        gov_data = getattr(projection, gov_key)
        gov_params[gov_name] = {
            'spending': gov_data['spending_billions'],
            'adoption': gov_data['adoption_rate'],
            'suitable': gov_data['pct_suitable_for_agents'],
            'regulatory_readiness': gov_data.get('regulatory_readiness', 0.5)
        }
    
    return {
        'market': market_df.to_dict(),
        'distribution': distribution_df.to_dict(),
        'gen_params': gen_params,
        'ind_params': ind_params,
        'gov_params': gov_params
    }

# Update summary cards
@app.callback(
    Output('summary-cards', 'children'),
    Input('projection-data', 'data')
)
def update_summary_cards(data):
    """Update summary statistics cards"""
    
    market_df = pd.DataFrame(data['market'])
    distribution_df = pd.DataFrame(data['distribution'])
    
    total_2025 = market_df[market_df['Year'] == 2025]['Total Market'].iloc[0]
    total_2030 = market_df[market_df['Year'] == 2030]['Total Market'].iloc[0]
    cagr = ((total_2030 / total_2025) ** (1/5) - 1) * 100
    
    consumer_2030 = market_df[market_df['Year'] == 2030]['Total Consumer'].iloc[0]
    business_2030 = market_df[market_df['Year'] == 2030]['Total Business'].iloc[0]
    government_2030 = market_df[market_df['Year'] == 2030]['Total Government'].iloc[0]
    
    return html.Div([
        html.Div([
            html.H4("2025 Total Market", style={'color': '#666'}),
            html.H2(f"${total_2025:.1f}B", style={'color': '#2E86AB'})
        ], style={'width': '16%', 'display': 'inline-block', 'textAlign': 'center', 
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '0.5%'}),
        
        html.Div([
            html.H4("2030 Total Market", style={'color': '#666'}),
            html.H2(f"${total_2030:.1f}B", style={'color': '#2E86AB'})
        ], style={'width': '16%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '0.5%'}),
        
        html.Div([
            html.H4("5-Year CAGR", style={'color': '#666'}),
            html.H2(f"{cagr:.1f}%", style={'color': '#F18F01'})
        ], style={'width': '16%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '0.5%'}),
        
        html.Div([
            html.H4("2030 Consumer", style={'color': '#666'}),
            html.H2(f"${consumer_2030:.1f}B", style={'color': '#A23B72'})
        ], style={'width': '16%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '0.5%'}),
        
        html.Div([
            html.H4("2030 Business", style={'color': '#666'}),
            html.H2(f"${business_2030:.1f}B", style={'color': '#1f77b4'})
        ], style={'width': '16%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '0.5%'}),
        
        html.Div([
            html.H4("2030 Government", style={'color': '#666'}),
            html.H2(f"${government_2030:.1f}B", style={'color': '#393b79'})
        ], style={'width': '16%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20})
    ])

# Total Economy Charts
@app.callback(
    Output('total-economy-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_total_economy_chart(data):
    """Update total economy market projection chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Market'],
        mode='lines+markers',
        name='Total Market',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=10),
        text=[f"${val:.1f}B" for val in market_df['Total Market']],
        textposition='top center'
    ))
    
    # Add individual sector lines
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Consumer'],
        mode='lines',
        name='Consumer',
        line=dict(color='#A23B72', width=2, dash='dot')
    ))
    
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Business'],
        mode='lines',
        name='Business',
        line=dict(color='#1f77b4', width=2, dash='dot')
    ))
    
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Government'],
        mode='lines',
        name='Government',
        line=dict(color='#393b79', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title="Total Agentic Commerce Market (Consumer + Business + Government)",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('sector-breakdown-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_sector_breakdown_chart(data):
    """Update sector breakdown stacked area chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Government'],
        name='Government',
        mode='lines',
        stackgroup='one',
        fillcolor='#393b79'
    ))
    
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Business'],
        name='Business',
        mode='lines',
        stackgroup='one',
        fillcolor='#1f77b4'
    ))
    
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Consumer'],
        name='Consumer',
        mode='lines',
        stackgroup='one',
        fillcolor='#A23B72'
    ))
    
    fig.update_layout(
        title="Market Size by Sector (Stacked)",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('sector-growth-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_sector_growth_chart(data):
    """Update sector-wise growth rate comparison"""
    
    market_df = pd.DataFrame(data['market'])
    
    # Calculate CAGRs
    consumer_start = market_df[market_df['Year'] == 2025]['Total Consumer'].iloc[0]
    consumer_end = market_df[market_df['Year'] == 2030]['Total Consumer'].iloc[0]
    consumer_cagr = ((consumer_end / consumer_start) ** (1/5) - 1) * 100
    
    business_start = market_df[market_df['Year'] == 2025]['Total Business'].iloc[0]
    business_end = market_df[market_df['Year'] == 2030]['Total Business'].iloc[0]
    business_cagr = ((business_end / business_start) ** (1/5) - 1) * 100
    
    gov_start = market_df[market_df['Year'] == 2025]['Total Government'].iloc[0]
    gov_end = market_df[market_df['Year'] == 2030]['Total Government'].iloc[0]
    gov_cagr = ((gov_end / gov_start) ** (1/5) - 1) * 100
    
    fig = go.Figure()
    
    sectors = ['Consumer', 'Business', 'Government']
    cagrs = [consumer_cagr, business_cagr, gov_cagr]
    colors = ['#A23B72', '#1f77b4', '#393b79']
    
    fig.add_trace(go.Bar(
        x=sectors,
        y=cagrs,
        marker_color=colors,
        text=[f"{cagr:.1f}%" for cagr in cagrs],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="5-Year CAGR by Sector (2025-2030)",
        xaxis_title="Sector",
        yaxis_title="CAGR (%)",
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('sector-contribution-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_sector_contribution_chart(data):
    """Update sector contribution to total market growth"""
    
    market_df = pd.DataFrame(data['market'])
    
    # Calculate absolute growth contributions
    consumer_growth = market_df[market_df['Year'] == 2030]['Total Consumer'].iloc[0] - market_df[market_df['Year'] == 2025]['Total Consumer'].iloc[0]
    business_growth = market_df[market_df['Year'] == 2030]['Total Business'].iloc[0] - market_df[market_df['Year'] == 2025]['Total Business'].iloc[0]
    gov_growth = market_df[market_df['Year'] == 2030]['Total Government'].iloc[0] - market_df[market_df['Year'] == 2025]['Total Government'].iloc[0]
    
    fig = go.Figure()
    
    sectors = ['Consumer', 'Business', 'Government']
    growth_values = [consumer_growth, business_growth, gov_growth]
    colors = ['#A23B72', '#1f77b4', '#393b79']
    
    fig.add_trace(go.Bar(
        x=sectors,
        y=growth_values,
        marker_color=colors,
        text=[f"${val:.1f}B" for val in growth_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Absolute Market Growth by Sector (2025-2030)",
        xaxis_title="Sector",
        yaxis_title="Growth (Billions USD)",
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('segment-trends-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_segment_trends_chart(data):
    """Update segment market share trends over time"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    
    # Calculate market shares
    years = market_df['Year'].tolist()
    consumer_share = (market_df['Total Consumer'] / market_df['Total Market'] * 100).tolist()
    business_share = (market_df['Total Business'] / market_df['Total Market'] * 100).tolist()
    gov_share = (market_df['Total Government'] / market_df['Total Market'] * 100).tolist()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=consumer_share,
        name='Consumer',
        mode='lines+markers',
        line=dict(color='#A23B72', width=2),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=business_share,
        name='Business',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=gov_share,
        name='Government',
        mode='lines+markers',
        line=dict(color='#393b79', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Market Share Trends by Sector",
        xaxis_title="Year",
        yaxis_title="Market Share (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        yaxis=dict(range=[0, 100])
    )
    
    return fig

@app.callback(
    Output('adoption-comparison-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_adoption_comparison_chart(data):
    """Update adoption rate comparison across sectors"""
    
    if not all(key in data for key in ['gen_params', 'ind_params', 'gov_params']):
        return go.Figure()
    
    years = list(range(2025, 2031))
    
    fig = go.Figure()
    
    # Calculate weighted average adoption rates for each sector
    # Consumer - weighted by market size
    consumer_adoption = []
    for year in years:
        total_adoption = 0
        total_weight = 0
        for gen_name, gen_data in data['gen_params'].items():
            if year in gen_data['adoption']:
                adoption = gen_data['adoption'][year] * 100
                # Weight by spending * population * pct_agents
                weight = (gen_data['spending'].get(year, 0) * 
                         gen_data['population'].get(year, 0) * 
                         gen_data['pct_agents'].get(year, 0))
                total_adoption += adoption * weight
                total_weight += weight
        consumer_adoption.append(total_adoption / total_weight if total_weight > 0 else 0)
    
    # Business - weighted by spending
    business_adoption = []
    for year in years:
        total_adoption = 0
        total_weight = 0
        for ind_name, ind_data in data['ind_params'].items():
            if year in ind_data['adoption']:
                adoption = ind_data['adoption'][year] * 100
                weight = ind_data['spending'].get(year, 0)
                total_adoption += adoption * weight
                total_weight += weight
        business_adoption.append(total_adoption / total_weight if total_weight > 0 else 0)
    
    # Government - weighted by spending
    gov_adoption = []
    for year in years:
        total_adoption = 0
        total_weight = 0
        for gov_name, gov_data in data['gov_params'].items():
            if year in gov_data['adoption']:
                adoption = gov_data['adoption'][year] * 100
                weight = gov_data['spending'].get(year, 0)
                total_adoption += adoption * weight
                total_weight += weight
        gov_adoption.append(total_adoption / total_weight if total_weight > 0 else 0)
    
    fig.add_trace(go.Scatter(
        x=years,
        y=consumer_adoption,
        name='Consumer (weighted avg)',
        mode='lines+markers',
        line=dict(color='#A23B72', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=business_adoption,
        name='Business (weighted avg)',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=gov_adoption,
        name='Government (weighted avg)',
        mode='lines+markers',
        line=dict(color='#393b79', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Weighted Average Adoption Rates by Sector",
        xaxis_title="Year",
        yaxis_title="Adoption Rate (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Consumer Analysis Charts
@app.callback(
    Output('consumer-market-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_consumer_market_chart(data):
    """Update consumer market projection chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=market_df['Year'],
        y=market_df['Total Consumer'],
        mode='lines+markers',
        name='Total Consumer Market',
        line=dict(color='#A23B72', width=3),
        marker=dict(size=10),
        text=[f"${val:.1f}B" for val in market_df['Total Consumer']],
        textposition='top center'
    ))
    
    fig.update_layout(
        title="Total Consumer Agentic Commerce Market",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('consumer-growth-rate-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_consumer_growth_rate_chart(data):
    """Update consumer year-over-year growth rate chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    growth_rates = []
    years = []
    for i in range(1, len(market_df)):
        growth_rate = ((market_df.iloc[i]['Total Consumer'] / market_df.iloc[i-1]['Total Consumer']) - 1) * 100
        growth_rates.append(growth_rate)
        years.append(market_df.iloc[i]['Year'])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=growth_rates,
        marker_color='#F18F01',
        text=[f"{rate:.1f}%" for rate in growth_rates],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Consumer Market Year-over-Year Growth Rate",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        template='plotly_white',
        height=400
    )
    
    return fig

# Business Analysis Charts
@app.callback(
    Output('industry-market-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_industry_market_chart(data):
    """Update industry market sizes chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    
    industries = ['Financial Services', 'Manufacturing', 'Healthcare (Business)', 'Retail', 
                 'Technology', 'Transportation', 'Energy', 'Real Estate']
    
    for industry in industries:
        if industry in market_df.columns:
            fig.add_trace(go.Scatter(
                x=market_df['Year'],
                y=market_df[industry],
                name=industry.replace(' (Business)', ''),
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Agentic Commerce Market by Industry",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('industry-growth-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_industry_growth_chart(data):
    """Update industry growth rate chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    industries = ['Financial Services', 'Manufacturing', 'Healthcare (Business)', 'Retail', 
                 'Technology', 'Transportation', 'Energy', 'Real Estate']
    
    fig = go.Figure()
    
    industry_cagrs = []
    industry_names = []
    
    for industry in industries:
        if industry in market_df.columns:
            start = market_df[market_df['Year'] == 2025][industry].iloc[0]
            end = market_df[market_df['Year'] == 2030][industry].iloc[0]
            if start > 0:
                cagr = ((end / start) ** (1/5) - 1) * 100
                industry_cagrs.append(cagr)
                industry_names.append(industry.replace(' (Business)', ''))
    
    fig.add_trace(go.Bar(
        x=industry_names,
        y=industry_cagrs,
        marker_color=[INDUSTRY_COLORS.get(ind if ind != 'Healthcare' else 'Healthcare (Business)', '#666') 
                     for ind in industry_names],
        text=[f"{cagr:.1f}%" for cagr in industry_cagrs],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Industry 5-Year CAGR (2025-2030)",
        xaxis_title="Industry",
        yaxis_title="CAGR (%)",
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig

@app.callback(
    Output('industry-breakdown-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_industry_breakdown_chart(data):
    """Update industry breakdown pie chart for 2030"""
    
    market_df = pd.DataFrame(data['market'])
    final_year = market_df[market_df['Year'] == 2030].iloc[0]
    
    industries = ['Financial Services', 'Manufacturing', 'Healthcare (Business)', 'Retail', 
                 'Technology', 'Transportation', 'Energy', 'Real Estate']
    
    values = []
    labels = []
    colors = []
    
    for industry in industries:
        if industry in final_year and final_year[industry] > 0:
            values.append(final_year[industry])
            labels.append(industry.replace(' (Business)', ''))
            colors.append(INDUSTRY_COLORS.get(industry, '#666'))
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:.1f}B',
        hole=0.3
    )])
    
    fig.update_layout(
        title="2030 Business Market Share by Industry",
        height=400
    )
    
    return fig

@app.callback(
    Output('industry-adoption-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_industry_adoption_chart(data):
    """Update industry adoption rate evolution"""
    
    if 'ind_params' not in data:
        return go.Figure()
    
    years = list(range(2025, 2031))
    fig = go.Figure()
    
    for ind_name, ind_data in data['ind_params'].items():
        if 'adoption' in ind_data:
            adoption_rates = []
            for year in years:
                if year in ind_data['adoption']:
                    adoption_rates.append(ind_data['adoption'][year] * 100)
                else:
                    adoption_rates.append(0)
            
            fig.add_trace(go.Scatter(
                x=years,
                y=adoption_rates,
                name=ind_name.replace(' (Business)', ''),
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Adoption Rate Evolution by Industry",
        xaxis_title="Year",
        yaxis_title="Adoption Rate (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('risk-adoption-scatter', 'figure'),
    Input('projection-data', 'data')
)
def update_risk_adoption_scatter(data):
    """Update risk tolerance vs adoption rate scatter plot"""
    
    if 'ind_params' not in data:
        return go.Figure()
    
    fig = go.Figure()
    
    for ind_name, ind_data in data['ind_params'].items():
        if 'adoption' in ind_data and 'risk_tolerance' in ind_data:
            # Get 2030 adoption rate
            adoption_2030 = ind_data['adoption'].get(2030, 0) * 100
            risk_tolerance = ind_data['risk_tolerance'] * 100
            
            fig.add_trace(go.Scatter(
                x=[risk_tolerance],
                y=[adoption_2030],
                mode='markers+text',
                name=ind_name.replace(' (Business)', ''),
                text=[ind_name.replace(' (Business)', '')],
                textposition='top center',
                marker=dict(
                    size=15,
                    color=INDUSTRY_COLORS.get(ind_name, '#666')
                )
            ))
    
    fig.update_layout(
        title="Risk Tolerance vs 2030 Adoption Rate by Industry",
        xaxis_title="Risk Tolerance (%)",
        yaxis_title="2030 Adoption Rate (%)",
        template='plotly_white',
        height=400,
        xaxis=dict(range=[0, 100]),
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('industry-suitability-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_industry_suitability_chart(data):
    """Update industry suitability evolution chart"""
    
    if 'ind_params' not in data:
        return go.Figure()
    
    years = list(range(2025, 2031))
    fig = go.Figure()
    
    for ind_name, ind_data in data['ind_params'].items():
        if 'suitable' in ind_data:
            suitability_rates = []
            for year in years:
                if year in ind_data['suitable']:
                    suitability_rates.append(ind_data['suitable'][year] * 100)
                else:
                    suitability_rates.append(0)
            
            fig.add_trace(go.Scatter(
                x=years,
                y=suitability_rates,
                name=ind_name.replace(' (Business)', ''),
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="% of Spending Suitable for Agentic Commerce by Industry",
        xaxis_title="Year",
        yaxis_title="Suitability (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Government Analysis Charts
@app.callback(
    Output('government-market-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_government_market_chart(data):
    """Update government market sizes chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    
    gov_segments = ['Federal', 'State & Local', 'Defense', 'Healthcare (Gov)']
    
    for segment in gov_segments:
        if segment in market_df.columns:
            fig.add_trace(go.Scatter(
                x=market_df['Year'],
                y=market_df[segment],
                name=segment,
                mode='lines+markers',
                line=dict(width=2, color=GOVERNMENT_COLORS.get(segment, '#666')),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Agentic Commerce Market by Government Segment",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('government-growth-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_government_growth_chart(data):
    """Update government segment growth rates"""
    
    market_df = pd.DataFrame(data['market'])
    
    gov_segments = ['Federal', 'State & Local', 'Defense', 'Healthcare (Gov)']
    
    fig = go.Figure()
    
    segment_cagrs = []
    segment_names = []
    colors = []
    
    for segment in gov_segments:
        if segment in market_df.columns:
            start = market_df[market_df['Year'] == 2025][segment].iloc[0]
            end = market_df[market_df['Year'] == 2030][segment].iloc[0]
            if start > 0:
                cagr = ((end / start) ** (1/5) - 1) * 100
                segment_cagrs.append(cagr)
                segment_names.append(segment)
                colors.append(GOVERNMENT_COLORS.get(segment, '#666'))
    
    fig.add_trace(go.Bar(
        x=segment_names,
        y=segment_cagrs,
        marker_color=colors,
        text=[f"{cagr:.1f}%" for cagr in segment_cagrs],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Government Segment 5-Year CAGR (2025-2030)",
        xaxis_title="Government Segment",
        yaxis_title="CAGR (%)",
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('government-breakdown-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_government_breakdown_chart(data):
    """Update government segment breakdown for 2030"""
    
    market_df = pd.DataFrame(data['market'])
    final_year = market_df[market_df['Year'] == 2030].iloc[0]
    
    gov_segments = ['Federal', 'State & Local', 'Defense', 'Healthcare (Gov)']
    
    values = []
    labels = []
    colors = []
    
    for segment in gov_segments:
        if segment in final_year and final_year[segment] > 0:
            values.append(final_year[segment])
            labels.append(segment)
            colors.append(GOVERNMENT_COLORS.get(segment, '#666'))
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:.1f}B'
    )])
    
    fig.update_layout(
        title="2030 Government Market Share by Segment",
        height=400
    )
    
    return fig

@app.callback(
    Output('regulatory-readiness-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_regulatory_readiness_chart(data):
    """Update regulatory readiness comparison"""
    
    if 'gov_params' not in data:
        return go.Figure()
    
    fig = go.Figure()
    
    segments = []
    readiness_values = []
    adoption_2030 = []
    colors = []
    
    for gov_name, gov_data in data['gov_params'].items():
        if 'regulatory_readiness' in gov_data and 'adoption' in gov_data:
            segments.append(gov_name)
            readiness_values.append(gov_data['regulatory_readiness'] * 100)
            adoption_2030.append(gov_data['adoption'].get(2030, 0) * 100)
            colors.append(GOVERNMENT_COLORS.get(gov_name, '#666'))
    
    # Create grouped bar chart
    fig.add_trace(go.Bar(
        name='Regulatory Readiness',
        x=segments,
        y=readiness_values,
        marker_color='lightblue',
        text=[f"{val:.0f}%" for val in readiness_values],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='2030 Adoption Rate',
        x=segments,
        y=adoption_2030,
        marker_color='darkblue',
        text=[f"{val:.1f}%" for val in adoption_2030],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Regulatory Readiness vs 2030 Adoption Rate",
        xaxis_title="Government Segment",
        yaxis_title="Percentage (%)",
        template='plotly_white',
        height=400,
        barmode='group'
    )
    
    return fig

@app.callback(
    Output('gov-adoption-evolution', 'figure'),
    Input('projection-data', 'data')
)
def update_gov_adoption_evolution(data):
    """Update government adoption evolution chart"""
    
    if 'gov_params' not in data:
        return go.Figure()
    
    years = list(range(2025, 2031))
    fig = go.Figure()
    
    for gov_name, gov_data in data['gov_params'].items():
        if 'adoption' in gov_data:
            adoption_rates = []
            for year in years:
                if year in gov_data['adoption']:
                    adoption_rates.append(gov_data['adoption'][year] * 100)
                else:
                    adoption_rates.append(0)
            
            fig.add_trace(go.Scatter(
                x=years,
                y=adoption_rates,
                name=gov_name,
                mode='lines+markers',
                line=dict(width=2, color=GOVERNMENT_COLORS.get(gov_name, '#666')),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Government Adoption Rate Evolution",
        xaxis_title="Year",
        yaxis_title="Adoption Rate (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('gov-suitability-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_gov_suitability_chart(data):
    """Update government suitability evolution"""
    
    if 'gov_params' not in data:
        return go.Figure()
    
    years = list(range(2025, 2031))
    fig = go.Figure()
    
    for gov_name, gov_data in data['gov_params'].items():
        if 'suitable' in gov_data:
            suitability_rates = []
            for year in years:
                if year in gov_data['suitable']:
                    suitability_rates.append(gov_data['suitable'][year] * 100)
                else:
                    suitability_rates.append(0)
            
            fig.add_trace(go.Scatter(
                x=years,
                y=suitability_rates,
                name=gov_name,
                mode='lines+markers',
                line=dict(width=2, color=GOVERNMENT_COLORS.get(gov_name, '#666')),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="% of Government Spending Suitable for Agentic Commerce",
        xaxis_title="Year",
        yaxis_title="Suitability (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Existing visualization callbacks (keep all the original ones)
@app.callback(
    Output('generation-stack-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_generation_stack_chart(data):
    """Update generation stack chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    for gen in ['Baby Boomers', 'Gen X', 'Millennials', 'Gen Z']:
        if gen in market_df.columns:
            fig.add_trace(go.Scatter(
                x=market_df['Year'],
                y=market_df[gen],
                name=gen,
                mode='lines',
                stackgroup='one',
                fillcolor=GENERATION_COLORS[gen]
            ))
    
    fig.update_layout(
        title="Consumer Market Size by Generation",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=350
    )
    
    return fig

@app.callback(
    Output('generation-pie-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_generation_pie_chart(data):
    """Update 2030 generation pie chart"""
    
    market_df = pd.DataFrame(data['market'])
    final_year = market_df[market_df['Year'] == 2030].iloc[0]
    
    generations = ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']
    values = []
    
    for gen in generations:
        if gen in final_year:
            values.append(final_year[gen])
        else:
            values.append(0)
    
    fig = go.Figure(data=[go.Pie(
        labels=generations,
        values=values,
        marker_colors=[GENERATION_COLORS[gen] for gen in generations],
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:.1f}B'
    )])
    
    fig.update_layout(
        title="2030 Consumer Market Share by Generation",
        height=350
    )
    
    return fig

@app.callback(
    Output('adoption-evolution-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_adoption_evolution_chart(data):
    """Show adoption rate evolution by generation"""
    
    if 'gen_params' not in data:
        return go.Figure()
    
    gen_params = data['gen_params']
    years = list(range(2025, 2031))
    
    fig = go.Figure()
    
    for gen_name in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
        if gen_name in gen_params and 'adoption' in gen_params[gen_name]:
            adoption_data = gen_params[gen_name]['adoption']
            adoption_rates = []
            for year in years:
                if year in adoption_data:
                    adoption_rates.append(adoption_data[year] * 100)
                else:
                    adoption_rates.append(0)
                    
            fig.add_trace(go.Scatter(
                x=years,
                y=adoption_rates,
                name=gen_name,
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=8),
                marker_color=GENERATION_COLORS[gen_name]
            ))
    
    fig.update_layout(
        title="Adoption Rate Evolution by Generation",
        xaxis_title="Year",
        yaxis_title="Adoption Rate (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('spending-per-capita-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_spending_per_capita_chart(data):
    """Show average annual spending per person by generation"""
    
    if 'gen_params' not in data:
        return go.Figure()
    
    gen_params = data['gen_params']
    years = list(range(2025, 2031))
    
    fig = go.Figure()
    
    for gen_name in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
        if gen_name in gen_params and 'spending' in gen_params[gen_name]:
            spending_data = gen_params[gen_name]['spending']
            spending = []
            for year in years:
                if year in spending_data:
                    spending.append(spending_data[year])
                else:
                    spending.append(0)
                    
            fig.add_trace(go.Scatter(
                x=years,
                y=spending,
                name=gen_name,
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=8),
                marker_color=GENERATION_COLORS[gen_name]
            ))
    
    fig.update_layout(
        title="Annual Spending per Person by Generation",
        xaxis_title="Year",
        yaxis_title="Annual Spending ($)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Revenue Distribution Charts (keep existing)
@app.callback(
    Output('revenue-distribution-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_revenue_distribution_chart(data):
    """Update revenue distribution chart"""
    
    distribution_df = pd.DataFrame(data['distribution'])
    
    fig = go.Figure()
    stakeholders = ['Retailer/Merchant', 'Payment Processing', 'AI Agent Platform', 
                   'Advertising/Placement', 'Data & Analytics']
    
    for stakeholder in stakeholders[::-1]:
        fig.add_trace(go.Bar(
            x=distribution_df['Year'],
            y=distribution_df[stakeholder],
            name=stakeholder,
            marker_color=STAKEHOLDER_COLORS[stakeholder]
        ))
    
    fig.update_layout(
        title="Revenue Distribution by Stakeholder",
        xaxis_title="Year",
        yaxis_title="Revenue (Billions USD)",
        barmode='stack',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('revenue-percentage-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_revenue_percentage_chart(data):
    """Show revenue distribution as percentages"""
    
    distribution_df = pd.DataFrame(data['distribution'])
    
    fig = go.Figure()
    
    stakeholders = ['Retailer/Merchant', 'Payment Processing', 'AI Agent Platform', 
                   'Advertising/Placement', 'Data & Analytics']
    
    for stakeholder in stakeholders[::-1]:
        percentages = (distribution_df[stakeholder] / distribution_df['Total Market'] * 100).tolist()
        fig.add_trace(go.Scatter(
            x=distribution_df['Year'],
            y=percentages,
            name=stakeholder,
            mode='lines',
            stackgroup='one',
            fillcolor=STAKEHOLDER_COLORS[stakeholder]
        ))
    
    fig.update_layout(
        title="Revenue Distribution as % of Total Market",
        xaxis_title="Year",
        yaxis_title="Percentage (%)",
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

@app.callback(
    Output('fee-evolution-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_fee_evolution_chart(data):
    """Update fee evolution chart"""
    
    distribution_df = pd.DataFrame(data['distribution'])
    
    fig = go.Figure()
    for fee_type in ['Payment Processing', 'AI Agent Platform', 'Advertising/Placement', 'Data & Analytics']:
        fig.add_trace(go.Scatter(
            x=distribution_df['Year'],
            y=distribution_df[fee_type],
            name=fee_type,
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Fee Component Evolution",
        xaxis_title="Year",
        yaxis_title="Revenue (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=350
    )
    
    return fig

@app.callback(
    Output('per-transaction-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_per_transaction_chart(data):
    """Update per-transaction fees chart"""
    
    distribution_df = pd.DataFrame(data['distribution'])
    
    per_trans_data = []
    for _, row in distribution_df.iterrows():
        num_trans = (row['Total Market'] * 1e9) / 75  # Assuming $75 avg transaction
        per_trans_data.append({
            'Year': row['Year'],
            'Total Fees': (row['Total Fees'] * 1e9 / num_trans)
        })
    
    per_trans_df = pd.DataFrame(per_trans_data)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=per_trans_df['Year'],
        y=per_trans_df['Total Fees'],
        name='Total Fees per Transaction',
        marker_color='#F71735',
        text=[f"${val:.2f}" for val in per_trans_df['Total Fees']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Per-Transaction Fees (Assuming $75 avg transaction)",
        xaxis_title="Year",
        yaxis_title="Fee per Transaction ($)",
        template='plotly_white',
        height=350
    )
    
    return fig

@app.callback(
    Output('retailer-vs-fees-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_retailer_vs_fees_chart(data):
    """Show retailer revenue vs total fees over time"""
    
    distribution_df = pd.DataFrame(data['distribution'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distribution_df['Year'],
        y=distribution_df['Retailer %'],
        name='Retailer Share',
        mode='lines+markers',
        line=dict(color=STAKEHOLDER_COLORS['Retailer/Merchant'], width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=distribution_df['Year'],
        y=distribution_df['Fees %'],
        name='Total Fees Share',
        mode='lines+markers',
        line=dict(color='#F71735', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Retailer vs Total Fees Share of Market",
        xaxis_title="Year",
        yaxis_title="Percentage of Total Market (%)",
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        template='plotly_white',
        height=350
    )
    
    return fig

@app.callback(
    Output('fee-breakdown-2030', 'figure'),
    Input('projection-data', 'data')
)
def update_fee_breakdown_2030(data):
    """Show detailed fee breakdown for 2030"""
    
    distribution_df = pd.DataFrame(data['distribution'])
    final_year = distribution_df[distribution_df['Year'] == 2030].iloc[0]
    
    labels = ['Payment Processing', 'AI Agent Platform', 'Advertising/Placement', 'Data & Analytics']
    values = [final_year[label] for label in labels]
    colors = [STAKEHOLDER_COLORS[label] for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:.2f}B',
        hole=0.3
    )])
    
    fig.update_layout(
        title=f"2030 Fee Breakdown (Total: ${final_year['Total Fees']:.2f}B)",
        height=350
    )
    
    return fig

# Data Tables
@app.callback(
    Output('market-data-table', 'children'),
    Input('projection-data', 'data')
)
def update_market_data_table(data):
    """Update market data table"""
    
    market_df = pd.DataFrame(data['market'])
    
    # Select key columns for display
    display_columns = ['Year', 'Total Consumer', 'Total Business', 'Total Government', 'Total Market']
    display_df = market_df[display_columns].copy()
    
    return dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=[
            {'name': 'Year', 'id': 'Year'},
            {'name': 'Consumer ($B)', 'id': 'Total Consumer', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Business ($B)', 'id': 'Total Business', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Government ($B)', 'id': 'Total Government', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Total Market ($B)', 'id': 'Total Market', 'type': 'numeric', 'format': {'specifier': '.2f'}}
        ],
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9f9f9'
            }
        ]
    )

@app.callback(
    Output('revenue-data-table', 'children'),
    Input('projection-data', 'data')
)
def update_revenue_data_table(data):
    """Update revenue distribution data table"""
    
    distribution_df = pd.DataFrame(data['distribution'])
    
    # Format data for display
    revenue_table_data = []
    for _, row in distribution_df.iterrows():
        revenue_table_data.append({
            'Year': row['Year'],
            'Total Market': f"${row['Total Market']:.2f}B",
            'Retailer': f"${row['Retailer/Merchant']:.2f}B ({row['Retailer %']:.1f}%)",
            'Payment': f"${row['Payment Processing']:.2f}B",
            'AI Platform': f"${row['AI Agent Platform']:.2f}B",
            'Advertising': f"${row['Advertising/Placement']:.2f}B",
            'Data': f"${row['Data & Analytics']:.2f}B",
            'Total Fees': f"${row['Total Fees']:.2f}B ({row['Fees %']:.1f}%)"
        })
    
    return dash_table.DataTable(
        data=revenue_table_data,
        columns=[
            {'name': 'Year', 'id': 'Year'},
            {'name': 'Total Market', 'id': 'Total Market'},
            {'name': 'Retailer/Merchant', 'id': 'Retailer'},
            {'name': 'Payment Processing', 'id': 'Payment'},
            {'name': 'AI Platform', 'id': 'AI Platform'},
            {'name': 'Advertising', 'id': 'Advertising'},
            {'name': 'Data & Analytics', 'id': 'Data'},
            {'name': 'Total Fees', 'id': 'Total Fees'}
        ],
        style_cell={'textAlign': 'center', 'fontSize': 12},
        style_header={'backgroundColor': '#F18F01', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9f9f9'
            }
        ]
    )

@app.callback(
    Output('metrics-summary-table', 'children'),
    Input('projection-data', 'data')
)
def update_metrics_summary_table(data):
    """Create a summary table of key metrics"""
    
    market_df = pd.DataFrame(data['market'])
    distribution_df = pd.DataFrame(data['distribution'])
    
    # Calculate metrics
    metrics = []
    
    # Overall metrics
    total_start = market_df[market_df['Year'] == 2025]['Total Market'].iloc[0]
    total_end = market_df[market_df['Year'] == 2030]['Total Market'].iloc[0]
    total_cagr = ((total_end / total_start) ** (1/5) - 1) * 100
    
    metrics.append({'Metric': 'Total Market CAGR', 'Value': f'{total_cagr:.1f}%'})
    
    # Sector CAGRs
    consumer_start = market_df[market_df['Year'] == 2025]['Total Consumer'].iloc[0]
    consumer_end = market_df[market_df['Year'] == 2030]['Total Consumer'].iloc[0]
    consumer_cagr = ((consumer_end / consumer_start) ** (1/5) - 1) * 100 if consumer_start > 0 else 0
    
    business_start = market_df[market_df['Year'] == 2025]['Total Business'].iloc[0]
    business_end = market_df[market_df['Year'] == 2030]['Total Business'].iloc[0]
    business_cagr = ((business_end / business_start) ** (1/5) - 1) * 100 if business_start > 0 else 0
    
    gov_start = market_df[market_df['Year'] == 2025]['Total Government'].iloc[0]
    gov_end = market_df[market_df['Year'] == 2030]['Total Government'].iloc[0]
    gov_cagr = ((gov_end / gov_start) ** (1/5) - 1) * 100 if gov_start > 0 else 0
    
    metrics.append({'Metric': 'Consumer CAGR', 'Value': f'{consumer_cagr:.1f}%'})
    metrics.append({'Metric': 'Business CAGR', 'Value': f'{business_cagr:.1f}%'})
    metrics.append({'Metric': 'Government CAGR', 'Value': f'{gov_cagr:.1f}%'})
    
    # Market shares in 2030
    consumer_share_2030 = (consumer_end / total_end) * 100
    business_share_2030 = (business_end / total_end) * 100
    gov_share_2030 = (gov_end / total_end) * 100
    
    metrics.append({'Metric': '2030 Consumer Share', 'Value': f'{consumer_share_2030:.1f}%'})
    metrics.append({'Metric': '2030 Business Share', 'Value': f'{business_share_2030:.1f}%'})
    metrics.append({'Metric': '2030 Government Share', 'Value': f'{gov_share_2030:.1f}%'})
    
    # Fee metrics
    start_fees = distribution_df[distribution_df['Year'] == 2025]['Total Fees'].iloc[0]
    end_fees = distribution_df[distribution_df['Year'] == 2030]['Total Fees'].iloc[0]
    fee_cagr = ((end_fees / start_fees) ** (1/5) - 1) * 100 if start_fees > 0 else 0
    
    metrics.append({'Metric': 'Total Fees CAGR', 'Value': f'{fee_cagr:.1f}%'})
    
    return dash_table.DataTable(
        data=metrics,
        columns=[
            {'name': 'Key Metric', 'id': 'Metric'},
            {'name': 'Value', 'id': 'Value'}
        ],
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': '#A23B72', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9f9f9'
            }
        ]
    )

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Enhanced Agentic Commerce Dashboard")
    print("Including Consumer, Business, and Government Segments")
    print("Navigate to: http://127.0.0.1:8050/")
    print("\nFeatures:")
    print("- Consumer spending by generation")
    print("- Business spending by industry with risk tolerance")
    print("- Government spending by segment with regulatory readiness")
    print("- Unified economy visualizations")
    print("- Comprehensive revenue distribution analysis")
    print("- 30+ interactive visualizations")
    if AI_CHAT_AVAILABLE:
        print("- AI Assistant integrated (look for chat button)")
        print("\n⚠️  Make sure the AI backend is running:")
        print("   cd agentic-commerce-chatbot && ./launch.sh")
    print("="*60 + "\n")
    app.run(debug=True, port=8050)