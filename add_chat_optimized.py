"""
Optimized chat with immediate user feedback and AI response streaming
"""
from dash import html, dcc, Input, Output, State, callback_context, no_update, ALL
import json
import requests
import uuid
from datetime import datetime


def add_chat_optimized(app):
    """Add chat UI with immediate user messages and streaming AI responses"""
    
    # Generate unique prefix
    chat_prefix = f"ai_chat_{uuid.uuid4().hex[:8]}"
    
    # Create components
    chat_button = html.Button(
        "💬 AI Assistant",
        id=f'{chat_prefix}_toggle_btn',
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
    
    chat_panel = html.Div([
        # Header
        html.Div([
            html.H3("AI Market Assistant", style={
                'margin': '0', 
                'color': 'white', 
                'fontSize': '18px',
                'fontWeight': '600'
            }),
            html.Button("×", 
                       id=f'{chat_prefix}_close_btn',
                       style={
                           'background': 'none',
                           'border': 'none',
                           'color': 'white',
                           'fontSize': '28px',
                           'cursor': 'pointer',
                           'padding': '0',
                           'marginTop': '-5px'
                       })
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '15px 20px',
            'backgroundColor': '#007bff',
            'borderRadius': '10px 10px 0 0'
        }),
        
        # Messages area
        html.Div(id=f'{chat_prefix}_messages_div', 
                children=[
                    html.Div([
                        html.Div("Hello! I can help you analyze market data and update dashboard variables.", 
                               style={'marginBottom': '10px', 'fontWeight': '500'}),
                        html.Div("Try asking:", style={'marginBottom': '5px', 'fontWeight': '500'}),
                        html.Ul([
                            html.Li("'What is the Gen Z adoption rate?'"),
                            html.Li("'Set retail spending to 500000'"),
                            html.Li("'List all variables'")
                        ], style={'marginLeft': '20px', 'marginTop': '5px'})
                    ], style={
                        'backgroundColor': '#f8f9fa',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'margin': '10px',
                        'color': '#212529',
                        'fontSize': '14px',
                        'lineHeight': '1.5',
                        'border': '1px solid #e9ecef'
                    })
                ],
                style={
                    'height': '400px',
                    'overflowY': 'auto',
                    'padding': '10px',
                    'backgroundColor': 'white'
                }),
        
        # Input area
        html.Div([
            dcc.Input(
                id=f'{chat_prefix}_input_field',
                type='text',
                placeholder='Type your message and press Enter...',
                style={
                    'width': 'calc(100% - 80px)',
                    'padding': '10px 15px',
                    'border': '1px solid #ddd',
                    'borderRadius': '20px',
                    'fontSize': '14px',
                    'marginRight': '10px',
                    'color': '#212529',
                    'backgroundColor': 'white'
                },
                n_submit=0,
                debounce=False
            ),
            html.Button('Send', 
                       id=f'{chat_prefix}_send_btn',
                       n_clicks=0,
                       style={
                           'width': '60px',
                           'padding': '10px',
                           'backgroundColor': '#007bff',
                           'color': 'white',
                           'border': 'none',
                           'borderRadius': '20px',
                           'cursor': 'pointer',
                           'fontSize': '14px',
                           'fontWeight': '500'
                       })
        ], style={
            'display': 'flex',
            'padding': '15px',
            'borderTop': '1px solid #eee',
            'backgroundColor': '#fafafa'
        })
    ], id=f'{chat_prefix}_panel_div',
       style={
           'position': 'fixed',
           'bottom': '80px',
           'right': '20px',
           'width': '400px',
           'height': '580px',
           'backgroundColor': 'white',
           'borderRadius': '10px',
           'boxShadow': '0 4px 20px rgba(0,0,0,0.15)',
           'display': 'none',
           'zIndex': '9999',
           'flexDirection': 'column'
       })
    
    # Stores
    message_store = dcc.Store(id=f'{chat_prefix}_msg_store', data=[])
    pending_response = dcc.Store(id=f'{chat_prefix}_pending', data={'active': False})
    stream_store = dcc.Store(id=f'{chat_prefix}_stream', data={'content': '', 'position': 0})
    
    # Interval for streaming
    stream_interval = dcc.Interval(
        id=f'{chat_prefix}_interval',
        interval=30,  # 30ms for smooth streaming
        disabled=True
    )
    
    # Container
    chat_container = html.Div([
        chat_button, chat_panel, message_store, pending_response, 
        stream_store, stream_interval
    ], id=f'{chat_prefix}_container')
    
    # Add to layout
    if hasattr(app, 'layout') and app.layout is not None:
        if isinstance(app.layout, html.Div) and hasattr(app.layout, 'children'):
            if isinstance(app.layout.children, list):
                app.layout.children.append(chat_container)
            else:
                app.layout.children = [app.layout.children, chat_container]
        else:
            app.layout = html.Div([app.layout, chat_container])
    
    # Callbacks
    @app.callback(
        [Output(f'{chat_prefix}_panel_div', 'style'),
         Output(f'{chat_prefix}_toggle_btn', 'style')],
        [Input(f'{chat_prefix}_toggle_btn', 'n_clicks'),
         Input(f'{chat_prefix}_close_btn', 'n_clicks')],
        [State(f'{chat_prefix}_panel_div', 'style'),
         State(f'{chat_prefix}_toggle_btn', 'style')],
        prevent_initial_call=True
    )
    def toggle_chat(open_clicks, close_clicks, panel_style, button_style):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        panel_style = dict(panel_style)
        button_style = dict(button_style)
        
        if trigger_id == f'{chat_prefix}_toggle_btn':
            panel_style['display'] = 'flex'
            button_style['display'] = 'none'
        elif trigger_id == f'{chat_prefix}_close_btn':
            panel_style['display'] = 'none'
            button_style['display'] = 'block'
        
        return panel_style, button_style
    
    # Step 1: Immediately show user message
    @app.callback(
        [Output(f'{chat_prefix}_msg_store', 'data'),
         Output(f'{chat_prefix}_input_field', 'value'),
         Output(f'{chat_prefix}_pending', 'data')],
        [Input(f'{chat_prefix}_send_btn', 'n_clicks'),
         Input(f'{chat_prefix}_input_field', 'n_submit')],
        [State(f'{chat_prefix}_input_field', 'value'),
         State(f'{chat_prefix}_msg_store', 'data')],
        prevent_initial_call=True
    )
    def add_user_message(n_clicks, n_submit, input_value, messages):
        """Immediately add user message and clear input"""
        if not input_value or not input_value.strip():
            return no_update, '', no_update
        
        messages = messages or []
        
        # Add user message
        messages.append({
            'type': 'user',
            'text': input_value.strip(),
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        
        # Add placeholder for AI response with typing indicator
        messages.append({
            'type': 'bot',
            'text': '',
            'timestamp': '',
            'streaming': True
        })
        
        # Mark that we need an AI response
        pending = {
            'active': True,
            'message': input_value.strip(),
            'message_id': len(messages) - 1
        }
        
        return messages, '', pending
    
    # Step 2: Get AI response when pending
    @app.callback(
        [Output(f'{chat_prefix}_stream', 'data'),
         Output(f'{chat_prefix}_interval', 'disabled'),
         Output(f'{chat_prefix}_pending', 'data', allow_duplicate=True)],
        Input(f'{chat_prefix}_pending', 'data'),
        State(f'{chat_prefix}_msg_store', 'data'),
        prevent_initial_call=True
    )
    def get_ai_response(pending, messages):
        """Get AI response when there's a pending request"""
        if not pending.get('active'):
            return no_update, no_update, no_update
        
        # Get AI response
        try:
            response = requests.post(
                'http://localhost:8000/api/chat',
                json={'message': pending['message']},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_text = data.get('response', 'Sorry, I encountered an error.')
                
                # Add tool information if present
                if 'tool_used' in data:
                    tool_result = data.get('tool_result', {})
                    if tool_result.get('success'):
                        bot_text += f"\n\n✅ Successfully executed: {data['tool_used']}"
                        if 'variable' in tool_result and 'new_value' in tool_result:
                            bot_text += f"\n📊 {tool_result['variable']} → {tool_result['new_value']}"
            else:
                bot_text = f'Error: Backend returned status {response.status_code}'
        except requests.exceptions.Timeout:
            bot_text = 'The AI is taking longer than expected. Please try again.'
        except Exception as e:
            bot_text = 'Cannot connect to AI backend. Please ensure it\'s running on http://localhost:8000'
        
        # Prepare streaming
        stream_data = {
            'content': bot_text,
            'position': 0,
            'message_id': pending['message_id']
        }
        
        # Clear pending and start streaming
        return stream_data, False, {'active': False}
    
    # Step 3: Stream the response
    @app.callback(
        [Output(f'{chat_prefix}_msg_store', 'data', allow_duplicate=True),
         Output(f'{chat_prefix}_interval', 'disabled', allow_duplicate=True),
         Output(f'{chat_prefix}_stream', 'data', allow_duplicate=True)],
        Input(f'{chat_prefix}_interval', 'n_intervals'),
        [State(f'{chat_prefix}_msg_store', 'data'),
         State(f'{chat_prefix}_stream', 'data')],
        prevent_initial_call=True
    )
    def stream_response(n_intervals, messages, stream_data):
        """Stream AI response character by character"""
        if not stream_data.get('content'):
            return no_update, True, no_update
        
        content = stream_data['content']
        position = stream_data['position']
        message_id = stream_data['message_id']
        
        # Calculate next chunk
        chunk_size = 2  # Characters per interval
        next_pos = min(position + chunk_size, len(content))
        
        # Update message
        if 0 <= message_id < len(messages):
            messages[message_id]['text'] = content[:next_pos]
            
            # Check if streaming is complete
            if next_pos >= len(content):
                messages[message_id]['streaming'] = False
                messages[message_id]['timestamp'] = datetime.now().strftime('%I:%M %p')
                return messages, True, {'content': '', 'position': 0}
            else:
                stream_data['position'] = next_pos
                return messages, False, stream_data
        
        return no_update, True, {'content': '', 'position': 0}
    
    @app.callback(
        Output(f'{chat_prefix}_messages_div', 'children'),
        Input(f'{chat_prefix}_msg_store', 'data')
    )
    def update_messages(messages):
        """Update message display with typing indicator"""
        if not messages:
            return [html.Div([
                html.Div("Hello! I can help you analyze market data and update dashboard variables.", 
                       style={'marginBottom': '10px', 'fontWeight': '500'}),
                html.Div("Try asking:", style={'marginBottom': '5px', 'fontWeight': '500'}),
                html.Ul([
                    html.Li("'What is the Gen Z adoption rate?'"),
                    html.Li("'Set retail spending to 500000'"),
                    html.Li("'List all variables'")
                ], style={'marginLeft': '20px', 'marginTop': '5px'})
            ], style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '8px',
                'margin': '10px',
                'color': '#212529',
                'fontSize': '14px',
                'lineHeight': '1.5',
                'border': '1px solid #e9ecef'
            })]
        
        elements = []
        for msg in messages:
            if msg['type'] == 'user':
                elements.append(
                    html.Div([
                        html.Div(msg['text'], style={
                            'color': '#212529',
                            'fontSize': '14px',
                            'lineHeight': '1.4'
                        }),
                        html.Div(msg['timestamp'], style={
                            'fontSize': '11px',
                            'color': '#6c757d',
                            'marginTop': '4px'
                        })
                    ], style={
                        'backgroundColor': '#e3f2fd',
                        'color': '#212529',
                        'padding': '10px 15px',
                        'borderRadius': '18px',
                        'margin': '5px 10px 5px 60px',
                        'wordWrap': 'break-word',
                        'border': '1px solid #bbdefb'
                    })
                )
            else:
                # Bot message
                if msg.get('streaming', False):
                    # Show typing indicator or partial text
                    if msg['text']:
                        # Streaming text with cursor
                        elements.append(
                            html.Div([
                                html.Div(msg['text'] + '▌', style={
                                    'color': '#212529',
                                    'fontSize': '14px',
                                    'lineHeight': '1.4',
                                    'whiteSpace': 'pre-wrap'
                                })
                            ], style={
                                'backgroundColor': '#f8f9fa',
                                'color': '#212529',
                                'padding': '10px 15px',
                                'borderRadius': '18px',
                                'margin': '5px 60px 5px 10px',
                                'wordWrap': 'break-word',
                                'border': '1px solid #dee2e6'
                            })
                        )
                    else:
                        # Typing indicator
                        elements.append(
                            html.Div([
                                html.Div([
                                    html.Span("AI is typing", style={'marginRight': '5px'}),
                                    html.Span("●●●", style={
                                        'animation': 'pulse 1.4s infinite',
                                        'color': '#007bff'
                                    })
                                ], style={
                                    'color': '#666',
                                    'fontSize': '13px',
                                    'fontStyle': 'italic'
                                })
                            ], style={
                                'backgroundColor': '#f8f9fa',
                                'padding': '10px 15px',
                                'borderRadius': '18px',
                                'margin': '5px 60px 5px 10px',
                                'border': '1px solid #dee2e6'
                            })
                        )
                else:
                    # Complete message
                    elements.append(
                        html.Div([
                            html.Div(msg['text'], style={
                                'color': '#212529',
                                'fontSize': '14px',
                                'lineHeight': '1.4',
                                'whiteSpace': 'pre-wrap'
                            }),
                            html.Div(msg['timestamp'], style={
                                'fontSize': '11px',
                                'color': '#6c757d',
                                'marginTop': '4px'
                            }) if msg.get('timestamp') else None
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'color': '#212529',
                            'padding': '10px 15px',
                            'borderRadius': '18px',
                            'margin': '5px 60px 5px 10px',
                            'wordWrap': 'break-word',
                            'border': '1px solid #dee2e6'
                        })
                    )
        
        # Auto-scroll and CSS injection
        elements.append(html.Div([
            html.Script(f"""
                // Auto-scroll to bottom
                var messagesDiv = document.getElementById('{chat_prefix}_messages_div');
                if (messagesDiv) {{
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }}
                
                // Add CSS for animations if not already added
                if (!document.getElementById('{chat_prefix}_pulse_style')) {{
                    var style = document.createElement('style');
                    style.id = '{chat_prefix}_pulse_style';
                    style.textContent = `
                        @keyframes pulse {{
                            0%, 60%, 100% {{ opacity: 0.3; }}
                            30% {{ opacity: 1; }}
                        }}
                    `;
                    document.head.appendChild(style);
                }}
            """)
        ], style={'display': 'none'}))
        
        return elements
    
    print(f"✅ Optimized AI Chat added (ID: {chat_prefix})")