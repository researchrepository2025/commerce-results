"""
Tools for the AI agent to interact with the dashboard
"""
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class DashboardState:
    """Manages the current state of dashboard variables"""
    
    def __init__(self):
        self._state = {
            # Consumer/Generation parameters
            'gen_z_adoption_rate': 25.0,
            'millennials_adoption_rate': 35.0,
            'gen_x_adoption_rate': 20.0,
            'baby_boomers_adoption_rate': 10.0,
            'gen_z_spending_per_person': 1200.0,
            'millennials_spending_per_person': 1800.0,
            'gen_x_spending_per_person': 1500.0,
            'baby_boomers_spending_per_person': 800.0,
            
            # Business parameters
            'retail_adoption_rate': 40.0,
            'healthcare_adoption_rate': 30.0,
            'finance_adoption_rate': 50.0,
            'manufacturing_adoption_rate': 25.0,
            'technology_adoption_rate': 60.0,
            'retail_spending': 500000.0,
            'healthcare_spending': 750000.0,
            'finance_spending': 1200000.0,
            'manufacturing_spending': 800000.0,
            'technology_spending': 2000000.0,
            
            # Government parameters
            'federal_readiness': 60.0,
            'state_readiness': 50.0,
            'local_readiness': 40.0,
            'federal_spending': 10000000.0,
            'state_spending': 5000000.0,
            'local_spending': 2000000.0,
            
            # Fee structure
            'payment_rate': 2.5,
            'ai_rate': 1.0,
            'ad_rate': 0.5,
            'data_rate': 1.0,
            
            # Growth rates
            'consumer_growth_rate': 25.0,
            'business_growth_rate': 35.0,
            'government_growth_rate': 20.0,
        }
        self._websocket_connections = []
    
    def get(self, key: str) -> Any:
        """Get a dashboard variable"""
        return self._state.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a dashboard variable"""
        if key in self._state:
            old_value = self._state[key]
            self._state[key] = value
            
            # Notify WebSocket connections of the change
            self._broadcast_update(key, value, old_value)
            return True
        return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all dashboard variables"""
        return self._state.copy()
    
    def add_websocket(self, websocket):
        """Add WebSocket connection for updates"""
        self._websocket_connections.append(websocket)
    
    def remove_websocket(self, websocket):
        """Remove WebSocket connection"""
        if websocket in self._websocket_connections:
            self._websocket_connections.remove(websocket)
    
    def _broadcast_update(self, key: str, new_value: Any, old_value: Any):
        """Broadcast update to all WebSocket connections"""
        update_message = {
            "type": "dashboard_update",
            "data": {
                "variable": key,
                "new_value": new_value,
                "old_value": old_value
            }
        }
        
        # In a real implementation, you'd broadcast to WebSocket connections
        print(f"Dashboard Update: {key} changed from {old_value} to {new_value}")


# Global dashboard state
dashboard_state = DashboardState()


class Tool(BaseModel):
    """Base tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]


def update_dashboard_variable(variable_name: str, new_value: float) -> Dict[str, Any]:
    """
    Update a dashboard variable with a new value
    
    Args:
        variable_name: Name of the variable to update (e.g., 'gen_z_adoption_rate')
        new_value: New numeric value for the variable
    
    Returns:
        Result of the update operation
    """
    success = dashboard_state.set(variable_name, new_value)
    
    if success:
        return {
            "success": True,
            "message": f"Updated {variable_name} to {new_value}",
            "variable": variable_name,
            "new_value": new_value
        }
    else:
        return {
            "success": False,
            "message": f"Variable '{variable_name}' not found. Available variables: {list(dashboard_state.get_all().keys())}",
            "variable": variable_name
        }


def get_dashboard_variable(variable_name: str) -> Dict[str, Any]:
    """
    Get the current value of a dashboard variable
    
    Args:
        variable_name: Name of the variable to retrieve
    
    Returns:
        Current value of the variable
    """
    value = dashboard_state.get(variable_name)
    
    if value is not None:
        return {
            "success": True,
            "variable": variable_name,
            "value": value
        }
    else:
        return {
            "success": False,
            "message": f"Variable '{variable_name}' not found. Available variables: {list(dashboard_state.get_all().keys())}",
            "variable": variable_name
        }


def list_dashboard_variables() -> Dict[str, Any]:
    """
    List all available dashboard variables and their current values
    
    Returns:
        Dictionary of all dashboard variables
    """
    return {
        "success": True,
        "variables": dashboard_state.get_all()
    }


def calculate_market_projection(year: int = 2025, segment: str = "consumer") -> Dict[str, Any]:
    """
    Calculate market projection for a specific year and segment
    
    Args:
        year: Target year for projection (default: 2025)
        segment: Market segment ('consumer', 'business', 'government')
    
    Returns:
        Calculated market projection
    """
    current_state = dashboard_state.get_all()
    
    if segment == "consumer":
        total_market = (
            current_state['gen_z_adoption_rate'] * current_state['gen_z_spending_per_person'] * 95.0 +  # 95M Gen Z
            current_state['millennials_adoption_rate'] * current_state['millennials_spending_per_person'] * 72.0 +  # 72M Millennials
            current_state['gen_x_adoption_rate'] * current_state['gen_x_spending_per_person'] * 65.0 +  # 65M Gen X
            current_state['baby_boomers_adoption_rate'] * current_state['baby_boomers_spending_per_person'] * 71.0   # 71M Boomers
        ) / 100.0  # Convert percentages to decimals
        
        growth_factor = (1 + current_state['consumer_growth_rate'] / 100.0) ** (year - 2024)
        projected_market = total_market * growth_factor
        
    elif segment == "business":
        total_market = (
            current_state['retail_spending'] * current_state['retail_adoption_rate'] / 100.0 +
            current_state['healthcare_spending'] * current_state['healthcare_adoption_rate'] / 100.0 +
            current_state['finance_spending'] * current_state['finance_adoption_rate'] / 100.0 +
            current_state['manufacturing_spending'] * current_state['manufacturing_adoption_rate'] / 100.0 +
            current_state['technology_spending'] * current_state['technology_adoption_rate'] / 100.0
        )
        
        growth_factor = (1 + current_state['business_growth_rate'] / 100.0) ** (year - 2024)
        projected_market = total_market * growth_factor
        
    elif segment == "government":
        total_market = (
            current_state['federal_spending'] * current_state['federal_readiness'] / 100.0 +
            current_state['state_spending'] * current_state['state_readiness'] / 100.0 +
            current_state['local_spending'] * current_state['local_readiness'] / 100.0
        )
        
        growth_factor = (1 + current_state['government_growth_rate'] / 100.0) ** (year - 2024)
        projected_market = total_market * growth_factor
        
    else:
        return {
            "success": False,
            "message": f"Unknown segment '{segment}'. Available: consumer, business, government"
        }
    
    return {
        "success": True,
        "segment": segment,
        "year": year,
        "projected_market_size": projected_market,
        "formatted_value": f"${projected_market:,.0f}"
    }


# Tool definitions for the LLM
AVAILABLE_TOOLS = [
    Tool(
        name="update_dashboard_variable",
        description="Update a dashboard variable with a new value. Use this when users want to change parameters like adoption rates, spending amounts, or growth rates.",
        parameters={
            "type": "object",
            "properties": {
                "variable_name": {
                    "type": "string",
                    "description": "Name of the variable to update (e.g., 'gen_z_adoption_rate', 'retail_spending')"
                },
                "new_value": {
                    "type": "number",
                    "description": "New numeric value for the variable"
                }
            },
            "required": ["variable_name", "new_value"]
        }
    ),
    Tool(
        name="get_dashboard_variable",
        description="Get the current value of a specific dashboard variable",
        parameters={
            "type": "object",
            "properties": {
                "variable_name": {
                    "type": "string",
                    "description": "Name of the variable to retrieve"
                }
            },
            "required": ["variable_name"]
        }
    ),
    Tool(
        name="list_dashboard_variables",
        description="List all available dashboard variables and their current values",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="calculate_market_projection",
        description="Calculate market projection for a specific year and segment based on current dashboard settings",
        parameters={
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "Target year for projection (default: 2025)"
                },
                "segment": {
                    "type": "string",
                    "description": "Market segment: 'consumer', 'business', or 'government'"
                }
            },
            "required": ["segment"]
        }
    )
]


# Tool execution mapping
TOOL_FUNCTIONS = {
    "update_dashboard_variable": update_dashboard_variable,
    "get_dashboard_variable": get_dashboard_variable,
    "list_dashboard_variables": list_dashboard_variables,
    "calculate_market_projection": calculate_market_projection
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool with given arguments"""
    if tool_name in TOOL_FUNCTIONS:
        try:
            return TOOL_FUNCTIONS[tool_name](**arguments)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    else:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
            "available_tools": list(TOOL_FUNCTIONS.keys())
        }