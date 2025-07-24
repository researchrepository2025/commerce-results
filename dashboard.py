#!/usr/bin/env python3
"""
Agentic Commerce Market Projection Dashboard
Full-featured interactive dashboard with comprehensive controls including growth rates
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
from agentic_commerce_market_projection import AgenticCommerceProjection

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Agentic Commerce Market Projection Dashboard"

# Define color schemes
GENERATION_COLORS = {
    'Gen Z': '#A23B72',
    'Millennials': '#F18F01',
    'Gen X': '#C73E1D',
    'Baby Boomers': '#2E86AB'
}

STAKEHOLDER_COLORS = {
    'Retailer/Merchant': '#2E86AB',
    'Payment Processing': '#F71735',
    'AI Agent Platform': '#8FE402',
    'Advertising/Placement': '#F18F01',
    'Data & Analytics': '#C73E1D'
}

# Create initial projections
initial_projection = AgenticCommerceProjection(random_seed=42)
initial_market_df = initial_projection.calculate_total_market_projection()
initial_distribution_df = initial_projection.calculate_revenue_distribution(initial_market_df)

# Get initial values
initial_gen_data = {
    'Gen Z': {
        'adoption_2025': initial_projection.gen_z_base['adoption_rate']['2025_value'] * 100,
        'population': initial_projection.gen_z_base['population_millions']['2025_value'],
        'annual_spending': initial_projection.gen_z_base['avg_annual_spending']['2025_value'],
        'pct_via_agents': initial_projection.gen_z_base['pct_purchases_via_agents']['2025_value'] * 100,
        # Growth rates
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
        # Growth rates
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
        # Growth rates
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
        # Growth rates
        'population_growth': initial_projection.baby_boomers_base['population_millions']['base_growth_rates'],
        'spending_growth': initial_projection.baby_boomers_base['avg_annual_spending']['base_growth_rates'],
        'adoption_growth': initial_projection.baby_boomers_base['adoption_rate']['base_growth_rates'],
        'agent_usage_growth': initial_projection.baby_boomers_base['pct_purchases_via_agents']['base_growth_rates']
    }
}

# Initial fee structure including growth rates
initial_fees = {
    'payment_processing': initial_projection.revenue_distribution_base['payment_processing']['2025_value'] * 100,
    'ai_agent_platform': initial_projection.revenue_distribution_base['ai_agent_platform']['2025_value'] * 100,
    'advertising_placement': initial_projection.revenue_distribution_base['advertising_placement']['2025_value'] * 100,
    'data_analytics': initial_projection.revenue_distribution_base['data_analytics']['2025_value'] * 100,
    # Growth rates
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

# Create the layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Agentic Commerce Market Projection Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': 10}),
        html.H3("Interactive Analysis 2025-2030", 
                style={'textAlign': 'center', 'color': '#666', 'marginTop': 0}),
        html.Hr()
    ]),
    
    # Main container
    html.Div([
        # Control Panel (Full width top section)
        html.Div([
            dcc.Tabs(id='control-tabs', value='generation-tab', children=[
                dcc.Tab(label='Generation Adoption', value='generation-tab', children=[
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
                                html.Li("Set individual generation modifiers in the Generation Adoption tab", style={'fontSize': 14})
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
                dcc.Tab(label='Market Overview', children=[
                    html.Div([
                        # Row 1: Total Market and Growth Rate
                        html.Div([
                            dcc.Graph(id='total-market-chart', style={'width': '60%', 'display': 'inline-block'}),
                            dcc.Graph(id='growth-rate-chart', style={'width': '40%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 2: Generation breakdowns
                        html.Div([
                            dcc.Graph(id='generation-stack-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='generation-pie-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 3: Heatmap and absolute growth
                        html.Div([
                            dcc.Graph(id='market-heatmap', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='absolute-growth-chart', style={'width': '50%', 'display': 'inline-block'})
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
                
                dcc.Tab(label='Generation Analysis', children=[
                    html.Div([
                        # Row 1: Growth index and contribution
                        html.Div([
                            dcc.Graph(id='generation-growth-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='generation-contribution-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 2: Adoption rates and spending per capita
                        html.Div([
                            dcc.Graph(id='adoption-evolution-chart', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='spending-per-capita-chart', style={'width': '50%', 'display': 'inline-block'})
                        ]),
                        
                        # Row 3: Market share trends and agent usage
                        html.Div([
                            dcc.Graph(id='market-share-trends', style={'width': '50%', 'display': 'inline-block'}),
                            dcc.Graph(id='agent-usage-evolution', style={'width': '50%', 'display': 'inline-block'})
                        ])
                    ], style={'padding': 20})
                ]),
                
                dcc.Tab(label='Data Tables', children=[
                    html.Div([
                        html.H3("Market Projections by Generation", style={'marginTop': 20}),
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

# Callback to update all labels
@app.callback(
    [Output({'type': 'label-adoption-2025', 'generation': ALL}, 'children'),
     Output({'type': 'label-population', 'generation': ALL}, 'children'),
     Output({'type': 'label-spending', 'generation': ALL}, 'children'),
     Output({'type': 'label-pct-agents', 'generation': ALL}, 'children'),
     Output('label-payment-rate', 'children'),
     Output('label-ai-rate', 'children'),
     Output('label-ad-rate', 'children'),
     Output('label-data-rate', 'children')],
    [Input({'type': 'adoption-2025', 'generation': ALL}, 'value'),
     Input({'type': 'population', 'generation': ALL}, 'value'),
     Input({'type': 'spending', 'generation': ALL}, 'value'),
     Input({'type': 'pct-agents', 'generation': ALL}, 'value'),
     Input('payment-rate', 'value'),
     Input('ai-rate', 'value'),
     Input('ad-rate', 'value'),
     Input('data-rate', 'value')]
)
def update_all_labels(adoption_2025, population, spending, pct_agents,
                     payment_rate, ai_rate, ad_rate, data_rate):
    """Update all slider labels"""
    labels_2025 = [f"2025 Adoption Rate: {val:.0f}%" for val in adoption_2025]
    labels_pop = [f"Population (millions): {val:.0f}M" for val in population]
    labels_spend = [f"Annual Spending per Person: ${val:.0f}" for val in spending]
    labels_pct = [f"% of Purchases via Agents: {val:.1f}%" for val in pct_agents]
    
    return (labels_2025, labels_pop, labels_spend, labels_pct,
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
     # Growth modifiers
     State({'type': 'growth-modifier', 'generation': ALL}, 'value'),
     # Growth rates for each generation and variable
     State({'type': ALL, 'index': ALL}, 'value'),
     State({'type': ALL, 'index': ALL}, 'id')]
)
def update_projections(n_clicks, seed, payment_rate, ai_rate, ad_rate, data_rate,
                      adoption_2025_values, population_values,
                      spending_values, pct_agents_values, adoption_ids,
                      growth_modifiers, all_growth_values, all_growth_ids):
    """Calculate new projections based on all parameters"""
    
    # Use default values if None
    seed = seed or 42
    payment_rate = payment_rate or 3.0
    ai_rate = ai_rate or 1.5
    ad_rate = ad_rate or 2.0
    data_rate = data_rate or 0.5
    
    # Create new projection
    projection = AgenticCommerceProjection(random_seed=int(seed))
    
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
    
    return {
        'market': market_df.to_dict(),
        'distribution': distribution_df.to_dict(),
        'gen_params': gen_params
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
    
    fees_2030 = distribution_df[distribution_df['Year'] == 2030]['Total Fees'].iloc[0]
    retailer_2030 = distribution_df[distribution_df['Year'] == 2030]['Retailer/Merchant'].iloc[0]
    
    return html.Div([
        html.Div([
            html.H4("2025 Market", style={'color': '#666'}),
            html.H2(f"${total_2025:.1f}B", style={'color': '#2E86AB'})
        ], style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center', 
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '1%'}),
        
        html.Div([
            html.H4("2030 Market", style={'color': '#666'}),
            html.H2(f"${total_2030:.1f}B", style={'color': '#2E86AB'})
        ], style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '1%'}),
        
        html.Div([
            html.H4("5-Year CAGR", style={'color': '#666'}),
            html.H2(f"{cagr:.1f}%", style={'color': '#F18F01'})
        ], style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '1%'}),
        
        html.Div([
            html.H4("2030 Retailer Rev", style={'color': '#666'}),
            html.H2(f"${retailer_2030:.1f}B", style={'color': STAKEHOLDER_COLORS['Retailer/Merchant']})
        ], style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20, 'marginRight': '1%'}),
        
        html.Div([
            html.H4("2030 Total Fees", style={'color': '#666'}),
            html.H2(f"${fees_2030:.1f}B", style={'color': '#F71735'})
        ], style={'width': '19%', 'display': 'inline-block', 'textAlign': 'center',
                  'backgroundColor': '#f9f9f9', 'padding': 20})
    ])

# Update total market chart
@app.callback(
    Output('total-market-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_total_market_chart(data):
    """Update total market projection chart"""
    
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
    
    fig.update_layout(
        title="Total Agentic Commerce Market Size",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Add new growth rate chart
@app.callback(
    Output('growth-rate-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_growth_rate_chart(data):
    """Update year-over-year growth rate chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    growth_rates = []
    years = []
    for i in range(1, len(market_df)):
        growth_rate = ((market_df.iloc[i]['Total Market'] / market_df.iloc[i-1]['Total Market']) - 1) * 100
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
        title="Year-over-Year Growth Rate",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        template='plotly_white',
        height=400
    )
    
    return fig

# Update generation stack chart
@app.callback(
    Output('generation-stack-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_generation_stack_chart(data):
    """Update generation stack chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    for gen in ['Baby Boomers', 'Gen X', 'Millennials', 'Gen Z']:
        fig.add_trace(go.Scatter(
            x=market_df['Year'],
            y=market_df[gen],
            name=gen,
            mode='lines',
            stackgroup='one',
            fillcolor=GENERATION_COLORS[gen]
        ))
    
    fig.update_layout(
        title="Market Size by Generation",
        xaxis_title="Year",
        yaxis_title="Market Size (Billions USD)",
        hovermode='x unified',
        template='plotly_white',
        height=350
    )
    
    return fig

# Update generation pie chart
@app.callback(
    Output('generation-pie-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_generation_pie_chart(data):
    """Update 2030 generation pie chart"""
    
    market_df = pd.DataFrame(data['market'])
    final_year = market_df[market_df['Year'] == 2030].iloc[0]
    
    fig = go.Figure(data=[go.Pie(
        labels=['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers'],
        values=[final_year['Gen Z'], final_year['Millennials'], 
                final_year['Gen X'], final_year['Baby Boomers']],
        marker_colors=[GENERATION_COLORS[gen] for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']],
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:.1f}B'
    )])
    
    fig.update_layout(
        title="2030 Market Share by Generation",
        height=350
    )
    
    return fig

# Add market heatmap
@app.callback(
    Output('market-heatmap', 'figure'),
    Input('projection-data', 'data')
)
def update_market_heatmap(data):
    """Create market size heatmap by generation and year"""
    
    market_df = pd.DataFrame(data['market'])
    
    # Prepare data for heatmap
    heatmap_data = market_df.set_index('Year')[['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']].T
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='YlOrRd',
        text=[[f"${val:.1f}B" for val in row] for row in heatmap_data.values],
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Market Size Heatmap by Generation",
        xaxis_title="Year",
        yaxis_title="Generation",
        height=350
    )
    
    return fig

# Add absolute growth chart
@app.callback(
    Output('absolute-growth-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_absolute_growth_chart(data):
    """Show absolute dollar growth by generation"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    
    for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
        growth = market_df[market_df['Year'] == 2030][gen].iloc[0] - market_df[market_df['Year'] == 2025][gen].iloc[0]
        fig.add_trace(go.Bar(
            x=[gen],
            y=[growth],
            name=gen,
            marker_color=GENERATION_COLORS[gen],
            text=f"${growth:.1f}B",
            textposition='outside'
        ))
    
    fig.update_layout(
        title="Absolute Market Growth 2025-2030 by Generation",
        xaxis_title="Generation",
        yaxis_title="Growth (Billions USD)",
        showlegend=False,
        template='plotly_white',
        height=350
    )
    
    return fig

# Update revenue distribution chart
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

# Add revenue percentage chart
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

# Update fee evolution chart
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

# Update per-transaction chart
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

# Add retailer vs fees chart
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

# Add fee breakdown for 2030
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

# Update generation growth chart
@app.callback(
    Output('generation-growth-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_generation_growth_chart(data):
    """Update generation growth comparison chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    
    for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
        # Calculate growth index (2025 = 100)
        base_value = market_df[market_df['Year'] == 2025][gen].iloc[0]
        if base_value > 0:
            growth_index = (market_df[gen] / base_value) * 100
        else:
            growth_index = [100] * len(market_df)
        
        fig.add_trace(go.Scatter(
            x=market_df['Year'],
            y=growth_index,
            name=gen,
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8),
            marker_color=GENERATION_COLORS[gen]
        ))
    
    fig.update_layout(
        title="Generation Growth Index (2025 = 100)",
        xaxis_title="Year",
        yaxis_title="Growth Index",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Update generation contribution chart
@app.callback(
    Output('generation-contribution-chart', 'figure'),
    Input('projection-data', 'data')
)
def update_generation_contribution_chart(data):
    """Update generation contribution percentage chart"""
    
    market_df = pd.DataFrame(data['market'])
    
    # Calculate percentage contribution for each year
    years = []
    gen_percentages = {gen: [] for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']}
    
    for _, row in market_df.iterrows():
        years.append(row['Year'])
        total = row['Total Market']
        if total > 0:
            for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
                gen_percentages[gen].append((row[gen] / total) * 100)
        else:
            for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
                gen_percentages[gen].append(0)
    
    fig = go.Figure()
    
    for gen in ['Baby Boomers', 'Gen X', 'Millennials', 'Gen Z']:
        fig.add_trace(go.Bar(
            x=years,
            y=gen_percentages[gen],
            name=gen,
            marker_color=GENERATION_COLORS[gen]
        ))
    
    fig.update_layout(
        title="Market Share by Generation (%)",
        xaxis_title="Year",
        yaxis_title="Market Share (%)",
        barmode='stack',
        template='plotly_white',
        height=400
    )
    
    return fig

# Add adoption evolution chart
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
        else:
            adoption_rates = [0] * len(years)
            
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

# Add spending per capita chart
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
        else:
            spending = [0] * len(years)
            
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

# Add market share trends
@app.callback(
    Output('market-share-trends', 'figure'),
    Input('projection-data', 'data')
)
def update_market_share_trends(data):
    """Show market share trends over time"""
    
    market_df = pd.DataFrame(data['market'])
    
    fig = go.Figure()
    
    for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
        market_share = []
        for _, row in market_df.iterrows():
            if row['Total Market'] > 0:
                share = (row[gen] / row['Total Market']) * 100
            else:
                share = 0
            market_share.append(share)
        
        fig.add_trace(go.Scatter(
            x=market_df['Year'],
            y=market_share,
            name=gen,
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=8),
            marker_color=GENERATION_COLORS[gen]
        ))
    
    fig.update_layout(
        title="Market Share Trends by Generation",
        xaxis_title="Year",
        yaxis_title="Market Share (%)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Add agent usage evolution
@app.callback(
    Output('agent-usage-evolution', 'figure'),
    Input('projection-data', 'data')
)
def update_agent_usage_evolution(data):
    """Show % of purchases via agents by generation"""
    
    if 'gen_params' not in data:
        return go.Figure()
    
    gen_params = data['gen_params']
    years = list(range(2025, 2031))
    
    fig = go.Figure()
    
    for gen_name in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
        if gen_name in gen_params and 'pct_agents' in gen_params[gen_name]:
            pct_agents_data = gen_params[gen_name]['pct_agents']
            agent_usage = []
            for year in years:
                if year in pct_agents_data:
                    agent_usage.append(pct_agents_data[year] * 100)
                else:
                    agent_usage.append(0)
        else:
            agent_usage = [0] * len(years)
            
        fig.add_trace(go.Scatter(
            x=years,
            y=agent_usage,
            name=gen_name,
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=8),
            marker_color=GENERATION_COLORS[gen_name]
        ))
    
    fig.update_layout(
        title="% of Purchases via Agents by Generation",
        xaxis_title="Year",
        yaxis_title="% of Purchases via Agents",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

# Update market data table
@app.callback(
    Output('market-data-table', 'children'),
    Input('projection-data', 'data')
)
def update_market_data_table(data):
    """Update market data table"""
    
    market_df = pd.DataFrame(data['market'])
    
    return dash_table.DataTable(
        data=market_df.to_dict('records'),
        columns=[
            {'name': 'Year', 'id': 'Year'},
            {'name': 'Gen Z ($B)', 'id': 'Gen Z', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Millennials ($B)', 'id': 'Millennials', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Gen X ($B)', 'id': 'Gen X', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Baby Boomers ($B)', 'id': 'Baby Boomers', 'type': 'numeric', 'format': {'specifier': '.2f'}},
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

# Update revenue data table
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

# Add metrics summary table
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
    
    # Growth metrics
    for gen in ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers']:
        start = market_df[market_df['Year'] == 2025][gen].iloc[0]
        end = market_df[market_df['Year'] == 2030][gen].iloc[0]
        cagr = ((end / start) ** (1/5) - 1) * 100 if start > 0 else 0
        
        metrics.append({
            'Metric': f'{gen} CAGR',
            'Value': f'{cagr:.1f}%'
        })
    
    # Fee metrics
    start_fees = distribution_df[distribution_df['Year'] == 2025]['Total Fees'].iloc[0]
    end_fees = distribution_df[distribution_df['Year'] == 2030]['Total Fees'].iloc[0]
    fee_cagr = ((end_fees / start_fees) ** (1/5) - 1) * 100
    
    metrics.append({
        'Metric': 'Total Fees CAGR',
        'Value': f'{fee_cagr:.1f}%'
    })
    
    # Market concentration
    final_year = market_df[market_df['Year'] == 2030].iloc[0]
    gen_z_share = (final_year['Gen Z'] / final_year['Total Market']) * 100
    millennials_share = (final_year['Millennials'] / final_year['Total Market']) * 100
    
    metrics.append({
        'Metric': '2030 Gen Z + Millennials Share',
        'Value': f'{gen_z_share + millennials_share:.1f}%'
    })
    
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
    print("Starting Enhanced Agentic Commerce Dashboard...")
    print("Navigate to: http://127.0.0.1:8050/")
    print("\nFeatures:")
    print("- Simplified adoption controls (2025 base + growth rates only)")
    print("- 18+ comprehensive visualizations across all tabs")
    print("- Year-over-year growth rates for all variables")
    print("- Complete control over revenue distribution")
    print("- Real-time updates with interactive controls")
    print("="*60 + "\n")
    app.run(debug=True, port=8050)