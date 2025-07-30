# AI Assistant for Agentic Commerce Dashboard

## Overview

The AI Assistant is a local LLM-powered chatbot integrated with the Agentic Commerce Market Analysis Dashboard. It can help users understand market projections and update dashboard variables through natural language commands.

## Features

- **100% Local**: Uses Ollama with local LLM models (no external API calls)
- **Tool Integration**: Can read and modify dashboard variables
- **Natural Language**: Interact using plain English commands
- **Real-time Updates**: Changes are immediately reflected in the dashboard

## Quick Start

### Prerequisites

1. **Ollama**: Must be installed and running
   - macOS: Download from https://ollama.com or `brew install ollama`
   - Start Ollama app before running the assistant

2. **Python 3.10+**: Required for both backend and dashboard

### Launch Everything

```bash
./launch_all.sh
```

This will:
1. Start the AI backend on http://localhost:8000
2. Start the dashboard on http://127.0.0.1:8050
3. Enable the AI Assistant button in the dashboard

### Using the AI Assistant

1. Open the dashboard at http://127.0.0.1:8050
2. Click the "💬 AI Assistant" button in the bottom-right corner
3. Type your message and press Enter (or click Send)
4. Ask questions or give commands in natural language

## Available Commands

### Query Variables
- "What is the current Gen Z adoption rate?"
- "Show me all dashboard variables"
- "What's the retail spending value?"

### Update Variables
- "Set Gen Z adoption rate to 30%"
- "Update retail spending to 500000"
- "Change federal readiness to 45%"

### Calculate Projections
- "Calculate the 2026 consumer market projection"
- "What's the business market projection for 2025?"

## Architecture

### Components

1. **Backend** (`agentic-commerce-chatbot/backend/main_simple.py`)
   - FastAPI server with chat endpoint
   - Ollama integration for LLM inference
   - Tool system for dashboard manipulation

2. **Frontend Integration** (`add_chat_button_fixed.py`)
   - Dash component injection
   - WebSocket-free HTTP communication
   - Conflict-free callback system

3. **Dashboard State** (`backend/tools.py`)
   - Manages 50+ dashboard variables
   - Provides calculation functions
   - Handles state persistence

### Tool System

The AI has access to these tools:
- `get_dashboard_variable(variable_name)` - Read variable values
- `update_dashboard_variable(variable_name, new_value)` - Modify variables
- `list_dashboard_variables()` - Show all available variables
- `calculate_market_projection(segment, year)` - Compute projections

## Testing

### Test Backend Only
```bash
python test_backend_simple.py
```

### Test Chat CLI
```bash
python chat_cli.py
```

### Test Isolated Chat UI
```bash
python chat_interface_simple.py
```

## Troubleshooting

### "Backend offline" Error
1. Check if Ollama is running: `pgrep -x ollama`
2. Verify backend is running: `ps aux | grep main_simple.py`
3. Test backend health: `curl http://localhost:8000/api/health`

### Chat Not Responding
- The local LLM may take 10-30 seconds to respond
- Check backend logs for errors
- Ensure port 8000 is not blocked

### Variables Not Updating
- Verify variable names match exactly (case-sensitive)
- Check tool execution in backend logs
- Use "list variables" command to see available options

## Development

### Adding New Tools

Edit `backend/tools.py` to add new functions:

```python
def my_new_tool(param1: str, param2: float) -> Dict[str, Any]:
    """Tool description"""
    # Implementation
    return {"success": True, "result": "..."}

# Register in AVAILABLE_TOOLS
AVAILABLE_TOOLS["my_new_tool"] = my_new_tool
```

### Modifying the UI

Edit `add_chat_button_fixed.py` to customize:
- Chat panel styling
- Button appearance
- Message formatting

## Variable Reference

Key dashboard variables include:

**Generation Adoption Rates** (0-100%):
- gen_z_adoption_rate
- millennials_adoption_rate
- gen_x_adoption_rate
- baby_boomers_adoption_rate

**Business Adoption Rates** (0-100%):
- retail_adoption_rate
- healthcare_adoption_rate
- finance_adoption_rate
- manufacturing_adoption_rate
- logistics_adoption_rate
- services_adoption_rate

**Government Readiness** (0-100%):
- federal_readiness
- state_readiness
- local_readiness

**Spending Parameters**:
- retail_spending
- healthcare_spending
- finance_spending
- federal_spending
- state_spending
- local_spending

**Growth Rates** (%):
- consumer_growth_rate
- business_growth_rate
- government_growth_rate

**Fee Rates** (%):
- payment_rate
- ai_rate
- ad_rate
- data_rate