"""
Final simplified integration that works reliably
"""
from dash import html, dcc, Input, Output, State, callback, ALL
import json
import requests
import time


def _get_mock_response(query):
    """Provide helpful mock responses when backend is not connected"""
    query_lower = query.lower()
    
    if 'adoption' in query_lower or 'rate' in query_lower:
        return "To view adoption rates, check the Consumer Spending tab. Current Gen Z adoption is at 25%. To connect to the AI backend for real-time updates, ensure the backend server is running."
    elif 'business' in query_lower or 'industry' in query_lower:
        return "Business segment analysis is available in the Business Spending tab. You can adjust industry-specific parameters and risk tolerance there. For AI-powered insights, please start the backend server."
    elif 'government' in query_lower:
        return "Government spending projections are in the Government Spending tab. You can see segment breakdowns and regulatory readiness scores. Connect the AI backend for detailed analysis."
    elif 'help' in query_lower:
        return "I can help you with:\n• Understanding market projections\n• Analyzing consumer, business, and government segments\n• Explaining adoption rates and growth trends\n\nFor full AI capabilities, run: cd agentic-commerce-chatbot && ./launch.sh"
    else:
        return f"I understand you're asking about: '{query}'. To get AI-powered responses, please ensure the backend is running at http://localhost:8000. Check the tabs above to explore different market segments."


def add_ai_chat_final(app, layout):
    """Add working AI chat to dashboard"""
    
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
        
        # Messages area with initial message
        dcc.Store(id='chat-messages-store', data=[
            {
                'role': 'assistant',
                'content': "Hello! I'm your AI assistant for the Agentic Commerce Market Analysis Dashboard. I can help you understand market projections, update parameters, and analyze trends. What would you like to explore?",
                'timestamp': time.time()
            }
        ]),
        html.Div(id='chat-messages-display', style={
            'height': '400px',
            'overflowY': 'auto',
            'padding': '15px',
            'backgroundColor': '#f8f9fa'
        }),
        
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
                    'marginRight': '10px',
                    'fontSize': '14px'
                },
                debounce=True
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
        }),
        
        # Hidden div for triggering updates
        html.Div(id='chat-trigger', style={'display': 'none'})
    ], id='chat-container', style={
        'position': 'fixed',
        'bottom': '80px',
        'right': '20px',
        'width': '400px',
        'backgroundColor': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.15)',
        'display': 'none',
        'zIndex': '9998',
        'flexDirection': 'column'
    })
    
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
            container_style['display'] = 'flex'
            button_style['display'] = 'none'
        else:
            container_style['display'] = 'none'
            button_style['display'] = 'block'
            
        return container_style, button_style
    
    # Update messages display
    @app.callback(
        Output('chat-messages-display', 'children'),
        Input('chat-messages-store', 'data')
    )
    def update_messages_display(messages):
        """Update the chat display with messages"""
        message_elements = []
        
        for msg in messages:
            if msg['role'] == 'user':
                message_elements.append(
                    html.Div([
                        html.Div("You", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#007bff'}),
                        html.Div(msg['content'], style={
                            'backgroundColor': '#007bff',
                            'color': 'white',
                            'padding': '10px',
                            'borderRadius': '10px',
                            'marginLeft': '50px'
                        })
                    ], style={'marginBottom': '10px'})
                )
            elif msg['role'] == 'assistant':
                message_elements.append(
                    html.Div([
                        html.Div("AI Assistant", style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#666'}),
                        html.Div(msg['content'], style={
                            'backgroundColor': '#e9ecef',
                            'padding': '10px',
                            'borderRadius': '10px',
                            'marginRight': '50px',
                            'whiteSpace': 'pre-wrap'
                        })
                    ], style={'marginBottom': '10px'})
                )
            elif msg['role'] == 'status':
                message_elements.append(
                    html.Div(msg['content'], style={
                        'textAlign': 'center',
                        'color': '#666',
                        'fontSize': '12px',
                        'fontStyle': 'italic',
                        'margin': '10px 0'
                    })
                )
        
        return message_elements
    
    # Handle sending messages
    @app.callback(
        [Output('chat-messages-store', 'data'),
         Output('chat-input', 'value'),
         Output('chat-trigger', 'children')],
        [Input('chat-send-button', 'n_clicks'),
         Input('chat-input', 'n_submit')],
        [State('chat-input', 'value'),
         State('chat-messages-store', 'data')],
        prevent_initial_call=True
    )
    def handle_send_message(n_clicks, n_submit, input_value, messages):
        """Handle sending a message and getting AI response"""
        
        if not input_value or not input_value.strip():
            return messages, '', ''
        
        # Add user message
        messages.append({
            'role': 'user',
            'content': input_value.strip(),
            'timestamp': time.time()
        })
        
        # Add status message
        messages.append({
            'role': 'status',
            'content': 'AI is thinking...',
            'timestamp': time.time()
        })
        
        try:
            # Try HTTP POST first (simpler than WebSocket)
            response = requests.post(
                'http://localhost:8000/api/chat',
                json={'message': input_value.strip()},
                timeout=30
            )
            
            if response.status_code == 200:
                ai_response = response.json().get('response', 'I received your message but encountered an error.')
            else:
                # Fallback to mock response
                ai_response = f"I understand you're asking about: '{input_value}'. The AI backend needs to be running for real responses. Make sure to run: cd agentic-commerce-chatbot && ./launch.sh"
                
        except:
            # If backend is not available, provide helpful response
            ai_response = _get_mock_response(input_value.strip())
        
        # Remove status message and add AI response
        messages = [m for m in messages if m.get('role') != 'status']
        messages.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': time.time()
        })
        
        return messages, '', str(time.time())
    
    
    # Add HTTP endpoint to backend if not exists
    if hasattr(app, 'server'):
        @app.server.route('/api/chat', methods=['POST'])
        def chat_endpoint():
            """Simple HTTP endpoint for chat (fallback from WebSocket)"""
            try:
                import flask
                data = flask.request.get_json()
                message = data.get('message', '')
                
                # Try to forward to backend
                try:
                    backend_response = requests.post(
                        'http://localhost:8000/api/chat',
                        json={'message': message},
                        timeout=5
                    )
                    return backend_response.json()
                except:
                    return {'response': _get_mock_response(message)}
                    
            except Exception as e:
                return {'error': str(e)}, 500
    
    # Create wrapper with all components
    wrapped_layout = html.Div([
        layout,
        chat_button,
        chat_container
    ])
    
    return wrapped_layout


def integrate_ai_with_enhanced_dashboard(app):
    """Factory function for compatibility"""
    class FinalIntegration:
        def add_chat_to_dashboard(self, layout):
            return add_ai_chat_final(app, layout)
    
    return FinalIntegration()