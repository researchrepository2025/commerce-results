#!/usr/bin/env python3
"""
Test minimal Dash app
"""
import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Test Dashboard"),
    html.P("If you see this, Dash is working!")
])

if __name__ == '__main__':
    print("Starting minimal Dash test...")
    app.run(debug=True, port=8051)