"""
Simplified integration for AI chat without external dependencies
"""
from dash import html, dcc, Input, Output, State, callback, ClientsideFunction
import json


def add_simple_chat_to_dashboard(app, layout):
    """Add a simple chat interface to existing dashboard"""
    
    # Create chat UI components
    chat_button = html.Button(
        "💬 AI Assistant",
        id="chat-toggle-button",
        style={
            'position': 'fixed',
            'bottom': '20px',
            'right': '20px',
            'zIndex': '9999',
            'padding': '10px 20px',
            'backgroundColor': '#007bff',
            'color': 'white',
            'border': 'none',
            'borderRadius': '25px',
            'fontSize': '16px',
            'cursor': 'pointer',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }
    )
    
    chat_container = html.Div([
        # Header
        html.Div([
            html.H4("AI Market Assistant", style={'margin': '0', 'color': 'white'}),
            html.Button("×", id="chat-close-button", style={
                'background': 'none',
                'border': 'none',
                'color': 'white',
                'fontSize': '24px',
                'cursor': 'pointer',
                'padding': '0',
                'marginLeft': 'auto'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': '15px',
            'backgroundColor': '#007bff',
            'borderTopLeftRadius': '10px',
            'borderTopRightRadius': '10px'
        }),
        
        # Messages area
        html.Div(id='chat-messages', style={
            'height': '400px',
            'overflowY': 'auto',
            'padding': '15px',
            'backgroundColor': '#f8f9fa'
        }, children=[
            html.Div("Hello! I'm your AI assistant for the Agentic Commerce Market Analysis Dashboard. I can help you understand market projections, update parameters, and analyze trends. What would you like to explore?", 
                    style={
                        'backgroundColor': '#e9ecef',
                        'padding': '10px',
                        'borderRadius': '10px',
                        'marginBottom': '10px'
                    })
        ]),
        
        # Input area
        html.Div([
            dcc.Input(
                id='chat-input',
                type='text',
                placeholder='Type your message...',
                style={
                    'flex': '1',
                    'padding': '10px',
                    'border': '1px solid #ddd',
                    'borderRadius': '20px',
                    'marginRight': '10px'
                }
            ),
            html.Button('Send', id='chat-send-button', style={
                'padding': '10px 20px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '20px',
                'cursor': 'pointer'
            })
        ], style={
            'display': 'flex',
            'padding': '15px',
            'backgroundColor': 'white',
            'borderTop': '1px solid #ddd'
        })
    ], id='chat-container', style={
        'position': 'fixed',
        'bottom': '80px',
        'right': '20px',
        'width': '350px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.15)',
        'display': 'none',
        'zIndex': '9998',
        'display': 'flex',
        'flexDirection': 'column'
    })
    
    # WebSocket connection store
    websocket_store = dcc.Store(id='websocket-connected', data=False)
    
    # Add client-side WebSocket handler
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='setupWebSocket'
        ),
        Output('websocket-connected', 'data'),
        Input('chat-container', 'style'),
        prevent_initial_call=True
    )
    
    # Toggle chat visibility
    @app.callback(
        [Output('chat-container', 'style'),
         Output('chat-toggle-button', 'style')],
        [Input('chat-toggle-button', 'n_clicks'),
         Input('chat-close-button', 'n_clicks')],
        [State('chat-container', 'style'),
         State('chat-toggle-button', 'style')],
        prevent_initial_call=True
    )
    def toggle_chat(open_clicks, close_clicks, container_style, button_style):
        import dash
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return container_style, button_style
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'chat-toggle-button':
            # Show chat
            container_style['display'] = 'flex'
            button_style['display'] = 'none'
        else:
            # Hide chat
            container_style['display'] = 'none'
            button_style['display'] = 'block'
            
        return container_style, button_style
    
    # Add message handling
    @app.callback(
        [Output('chat-messages', 'children'),
         Output('chat-input', 'value')],
        [Input('chat-send-button', 'n_clicks')],
        [State('chat-input', 'value'),
         State('chat-messages', 'children')],
        prevent_initial_call=True
    )
    def send_message(n_clicks, input_value, messages):
        if not input_value:
            return messages, ''
            
        # Add user message
        user_msg = html.Div([
            html.Div("You", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            html.Div(input_value, style={
                'backgroundColor': '#007bff',
                'color': 'white',
                'padding': '10px',
                'borderRadius': '10px',
                'marginLeft': '50px'
            })
        ], style={'marginBottom': '10px'})
        
        messages.append(user_msg)
        
        # Add placeholder response (in production, this would come from WebSocket)
        bot_msg = html.Div([
            html.Div("AI Assistant", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            html.Div("I understand you're asking about: " + input_value + ". The WebSocket connection will handle real responses when connected to the backend.", 
                    style={
                        'backgroundColor': '#e9ecef',
                        'padding': '10px',
                        'borderRadius': '10px',
                        'marginRight': '50px'
                    })
        ], style={'marginBottom': '10px'})
        
        messages.append(bot_msg)
        
        return messages, ''
    
    # Create wrapper with all components
    wrapped_layout = html.Div([
        layout,
        chat_button,
        chat_container,
        websocket_store,
        
        # Add client-side JavaScript for WebSocket
        html.Script('''
            window.dash_clientside = Object.assign({}, window.dash_clientside, {
                clientside: {
                    setupWebSocket: function(chatStyle) {
                        if (chatStyle.display !== 'none' && !window.wsConnection) {
                            window.wsConnection = new WebSocket('ws://localhost:8000/ws/agent');
                            
                            window.wsConnection.onopen = function() {
                                console.log('WebSocket connected');
                            };
                            
                            window.wsConnection.onmessage = function(event) {
                                const data = JSON.parse(event.data);
                                console.log('Received:', data);
                                // In production, update the chat messages
                            };
                            
                            window.wsConnection.onerror = function(error) {
                                console.error('WebSocket error:', error);
                            };
                        }
                        return true;
                    }
                }
            });
        ''')
    ])
    
    return wrapped_layout


def integrate_ai_with_enhanced_dashboard(app):
    """Factory function for compatibility"""
    class SimpleIntegration:
        def add_chat_to_dashboard(self, layout):
            return add_simple_chat_to_dashboard(app, layout)
    
    return SimpleIntegration()