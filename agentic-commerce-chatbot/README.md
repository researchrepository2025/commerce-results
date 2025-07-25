# Agentic Commerce AI Chatbot

A 100% local AI assistant for the Agentic Commerce Market Analysis Dashboard, built with LangGraph, AG-UI protocol, and Ollama.

## Features

- **100% Local**: No external API calls, complete data privacy
- **LangGraph Agent**: Sophisticated agent orchestration with state management
- **AG-UI Protocol**: Standardized agent-to-UI communication
- **Multi-type Memory**: Procedural, episodic, and semantic memory systems
- **Real-time Updates**: WebSocket-based communication for instant dashboard updates
- **Tool Integration**: Built-in tools for market analysis and projections

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LOCAL MACHINE                                 │
│                                                                      │
│  ┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐ │
│  │   Dash Frontend │     │  FastAPI Backend │     │    Ollama      │ │
│  │   + AG-UI Client│◄────┤  + AG-UI Protocol│◄────┤  Llama 3.1     │ │
│  └─────────────────┘     └──────────────────┘     └──────────────┘ │
│                                    │                                 │
│                          ┌─────────┴──────────┐                     │
│                          │   LangGraph Agent  │                     │
│                          │   + Local Memory   │                     │
│                          └────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.8+
- 16GB RAM (minimum for 8B models)
- 64GB RAM (recommended for 70B models)
- Ollama installed ([Download](https://ollama.com/download))

## Quick Start

1. **Clone and Setup**
   ```bash
   cd agentic-commerce-chatbot
   ./setup.sh
   ```

2. **Start Ollama** (if not already running)
   ```bash
   ollama serve
   ```

3. **Activate Environment and Start Backend**
   ```bash
   source venv/bin/activate
   python backend/main.py
   ```

4. **Integrate with Dashboard**
   
   In your `dashboard_enhanced.py`:
   ```python
   # Add at the top
   import sys
   sys.path.append('./agentic-commerce-chatbot')
   from frontend.dashboard_integration import integrate_ai_with_enhanced_dashboard
   
   # After creating app
   ai_integration = integrate_ai_with_enhanced_dashboard(app)
   
   # Wrap your layout
   original_layout = app.layout
   app.layout = ai_integration.add_chat_to_dashboard(original_layout)
   ```

## Usage

Once integrated, you'll see an "AI Assistant" button in the bottom-right corner of your dashboard.

### Example Commands

- **Update Projections**: "Set consumer adoption rate to 30% for 2025"
- **Analyze Segments**: "Analyze business segment growth trends"
- **Compare Data**: "Compare government and business adoption rates"
- **Save Scenarios**: "Save current projections as 'optimistic scenario'"

### Tool Capabilities

1. **update_market_projection**: Modify any dashboard parameter
2. **analyze_market_segment**: Deep analysis of specific segments
3. **search_memory**: Query agent's knowledge base
4. **save_market_scenario**: Save current state for later

## Configuration

Edit `.env` file for customization:

```env
# Backend settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b  # Options: llama3.1:8b, llama3.1:70b, mixtral:8x7b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Memory settings
MEMORY_PATH=./agent_memory
```

## Memory System

The agent uses three types of memory:

1. **Procedural Memory**: Learned patterns and behaviors
2. **Episodic Memory**: Conversation history and interactions
3. **Semantic Memory**: Facts and knowledge about the market

Memory is stored locally in:
- SQLite: Conversation checkpoints
- ChromaDB: Vector embeddings
- File System: Patterns and caches

## API Endpoints

### WebSocket
- `ws://localhost:8000/ws/agent` - Main chat interface (AG-UI protocol)

### REST
- `GET /api/health` - Health check
- `POST /api/dashboard/update` - Programmatic updates
- `GET /api/memory/search` - Search agent memory
- `POST /api/memory/fact` - Store new facts

## AG-UI Protocol

Messages follow the AG-UI standard:

```json
{
  "id": "unique-id",
  "type": "text|tool_call|ui_update|error",
  "timestamp": "ISO-8601",
  "content": {
    "text": "Message content",
    "uiUpdates": [...]
  },
  "metadata": {}
}
```

## Performance Optimization

### Model Selection

| Model | RAM Required | Quality | Speed |
|-------|-------------|---------|--------|
| llama3.1:8b | 8GB | Good | Fast |
| mixtral:8x7b | 26GB | Better | Medium |
| llama3.1:70b | 40GB | Best | Slow |

### Tips

1. **Use GPU acceleration**: Add GPU layers in Ollama settings
2. **Adjust context window**: Reduce for faster responses
3. **Enable caching**: Responses are cached for repeated queries
4. **Batch updates**: Agent batches dashboard updates for efficiency

## Troubleshooting

### Ollama not responding
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart
killall ollama
ollama serve
```

### Memory errors
- Reduce model size or context window
- Use quantized models (e.g., `llama3.1:8b-q4_0`)

### WebSocket disconnections
- Check CORS settings match your dashboard URL
- Ensure backend is running on correct port

## Development

### Project Structure
```
agentic-commerce-chatbot/
├── backend/
│   ├── main.py          # FastAPI + WebSocket server
│   ├── agent.py         # LangGraph agent logic
│   └── models.py        # Pydantic models
├── frontend/
│   ├── chat_sidebar.py  # Dash chat component
│   └── dashboard_integration.py
├── agent_memory/        # Local storage
└── requirements.txt
```

### Testing
```bash
# Run tests
pytest tests/

# Test WebSocket connection
python -m websockets ws://localhost:8000/ws/agent
```

## Security

- All data stays local - no external API calls
- WebSocket authentication via session tokens
- CORS restricted to dashboard origin
- Input validation on all endpoints

## License

MIT License - See LICENSE file

## Contributing

1. Fork the repository
2. Create feature branch
3. Test with local models
4. Submit pull request

## Acknowledgments

- Built with LangGraph for agent orchestration
- Uses AG-UI protocol for standardized communication
- Powered by Ollama for local LLM inference