"""
Direct integration script to add AI chat button to dashboard
"""
from dash import html, dcc, Input, Output, State

def add_chat_directly(app):
    """Add chat components directly after layout is set"""
    
    # Create the chat button
    chat_button = html.Button(
        "💬 AI Assistant",
        id="ai-chat-toggle-btn",
        style={
            'position': 'fixed',
            'bottom': '20px',
            'right': '20px',
            'zIndex': '10000',
            'padding': '12px 24px',
            'backgroundColor': '#007bff',
            'color': 'white',
            'border': 'none',
            'borderRadius': '25px',
            'fontSize': '16px',
            'fontWeight': 'bold',
            'cursor': 'pointer',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.2)',
            'transition': 'all 0.3s ease'
        }
    )
    
    # Create the chat panel
    chat_panel = html.Div([
        # Header
        html.Div([
            html.H3("AI Market Assistant", style={'margin': '0', 'color': 'white', 'fontSize': '18px'}),
            html.Button("×", id="ai-chat-close-btn", style={
                'background': 'none',
                'border': 'none',
                'color': 'white',
                'fontSize': '28px',
                'cursor': 'pointer',
                'padding': '0',
                'lineHeight': '20px'
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '15px 20px',
            'backgroundColor': '#007bff',
            'borderTopLeftRadius': '10px',
            'borderTopRightRadius': '10px'
        }),
        
        # Messages area
        html.Div([
            html.Div("Hello! I'm your AI assistant for the Agentic Commerce Market Analysis Dashboard. Ask me about market projections, adoption rates, or any segment analysis.", 
                    style={
                        'backgroundColor': '#f0f0f0',
                        'padding': '12px',
                        'borderRadius': '8px',
                        'margin': '10px'
                    })
        ], id='ai-chat-messages-area', style={
            'height': '400px',
            'overflowY': 'auto',
            'padding': '10px',
            'backgroundColor': 'white'
        }),
        
        # Input area
        html.Div([
            dcc.Input(
                id='ai-chat-input-field',
                type='text',
                placeholder='Type your message...',
                style={
                    'width': 'calc(100% - 80px)',
                    'padding': '10px',
                    'border': '1px solid #ddd',
                    'borderRadius': '20px',
                    'fontSize': '14px',
                    'marginRight': '10px'
                }
            ),
            html.Button('Send', id='ai-chat-send-btn', style={
                'width': '60px',
                'padding': '10px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '20px',
                'cursor': 'pointer',
                'fontSize': '14px'
            })
        ], style={
            'display': 'flex',
            'padding': '15px',
            'borderTop': '1px solid #eee'
        })
    ], id='ai-chat-panel', style={
        'position': 'fixed',
        'bottom': '80px',
        'right': '20px',
        'width': '380px',
        'height': '550px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.2)',
        'display': 'none',
        'zIndex': '9999',
        'flexDirection': 'column'
    })
    
    # Store for messages
    messages_store = dcc.Store(id='ai-messages-data-store', data=[])
    
    # Get current layout
    current_layout = app.layout
    
    # Create new layout with chat components
    app.layout = html.Div([
        current_layout,
        chat_button,
        chat_panel,
        messages_store
    ])
    
    # Add callbacks
    @app.callback(
        [Output('ai-chat-panel', 'style'),
         Output('ai-chat-toggle-btn', 'style')],
        [Input('ai-chat-toggle-btn', 'n_clicks'),
         Input('ai-chat-close-btn', 'n_clicks')],
        [State('ai-chat-panel', 'style'),
         State('ai-chat-toggle-btn', 'style')],
        prevent_initial_call=True
    )
    def toggle_chat(open_clicks, close_clicks, panel_style, button_style):
        import dash
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return panel_style, button_style
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'ai-chat-toggle-btn':
            panel_style['display'] = 'flex'
            button_style['display'] = 'none'
        else:
            panel_style['display'] = 'none'
            button_style['display'] = 'block'
            
        return panel_style, button_style
    
    @app.callback(
        [Output('ai-messages-data-store', 'data'),
         Output('ai-chat-input-field', 'value')],
        [Input('ai-chat-send-btn', 'n_clicks')],
        [State('ai-chat-input-field', 'value'),
         State('ai-messages-data-store', 'data')],
        prevent_initial_call=True
    )
    def send_message(n_clicks, input_value, messages):
        if not input_value:
            return messages, ''
            
        # Add user message
        messages.append({
            'type': 'user',
            'text': input_value
        })
        
        # Try to get response from backend
        try:
            import requests
            response = requests.post(
                'http://localhost:8000/api/chat',
                json={'message': input_value},
                timeout=10
            )
            if response.status_code == 200:
                bot_text = response.json().get('response', 'Sorry, I encountered an error.')
            else:
                bot_text = 'Unable to connect to AI backend. Please ensure it\'s running.'
        except:
            bot_text = f'I received: "{input_value}". To get AI responses, ensure the backend is running at http://localhost:8000'
        
        messages.append({
            'type': 'bot',
            'text': bot_text
        })
        
        return messages, ''
    
    @app.callback(
        Output('ai-chat-messages-area', 'children'),
        Input('ai-messages-data-store', 'data')
    )
    def update_messages(messages):
        if not messages:
            return html.Div("Hello! I'm your AI assistant. Ask me about market projections!", 
                          style={'padding': '10px', 'color': '#666'})
        
        message_elements = []
        for msg in messages:
            if msg['type'] == 'user':
                message_elements.append(
                    html.Div(msg['text'], style={
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'padding': '10px',
                        'borderRadius': '8px',
                        'margin': '10px',
                        'marginLeft': '50px',
                        'textAlign': 'right'
                    })
                )
            else:
                message_elements.append(
                    html.Div(msg['text'], style={
                        'backgroundColor': '#f0f0f0',
                        'padding': '10px',
                        'borderRadius': '8px',
                        'margin': '10px',
                        'marginRight': '50px'
                    })
                )
        
        return message_elements
    
    print("✅ AI Chat button added successfully!")
    print("   Look for the blue '💬 AI Assistant' button in the bottom-right corner")