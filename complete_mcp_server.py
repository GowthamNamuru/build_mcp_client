from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Travel Planner")

TRAVEL_ALERTS = {
    "london": "Tube strike schediled for Friday. Expect delays.",
    "paris": "Metro Line 4 under maintenance. Replacement busses active.",
    "tokyo": "Typhoon season approaching. Check weather daily.",
    "new york": "Subway running on holiday schedule."
}

@mcp.resource("travel://alerts/{city}")
def get_travel_alerts(city: str) -> str:
    """
    Returns current travel alerts or warnings for a specific day.
    """
    city_lower = city.lower()
    return TRAVEL_ALERTS.get(city_lower, "No active alerts reported for this city.")


@mcp.resource("travel://destinations/list")
def list_supported_destinations() -> str:
    """
    Returns a list of cities we have specific monitoring for .
    """

    return ", ".join([city.title() for city in TRAVEL_ALERTS.keys()])


@mcp.tool() 
def calculate_trip_budget(days: int, travelers: int, daily_spend: float, currency_rate: float = 1.0) -> str:
    """
    Calculate the totla estimated budget for a trip
    """

    if days < 1 or travelers < 1:
        return "Error: Days and travelers must be at least 1."

    base_total = days * travelers * daily_spend
    converted_total = base_total * currency_rate

    return (
        f"Budget Estimate:\n"
        f"- Travelers: {travelers}\n"
        f"- Duration: {days} days\n"
        f"- Daily avg: {daily_spend}\n"
        f"---------------------------\n"
        f"TOTAL: {converted_total:.2f} (at rate {currency_rate})"
    )

@mcp.prompt()
def draft_travel_plan(destination: str, days: int, travelers: int) -> str:
    """
    Creates a prompt with PRE-LOADED resource data.
    The LLM receives the alerts as context immediately. so it doesn't need to fetch them.
    """
    city_lower = destination.lower()
    current_alerts = TRAVEL_ALERTS.get(city_lower, "No active alerts reported for this city.")

    return f"""
    I would like to plan a trip to {destination} for {days} days for {travelers} people.

    === CONTEXT: TRAVEL ALERTS ===
    Current status for {destination}: "{current_alerts}"
    ==============================

    Please perform the following steps:
    1. Acknowledge the travel alerts provided above in the context.
    2. Use the 'calculate_trip_budget' tool to estimate costs (assume $150 per person/day).
    3. Draft a daily itinerary. If the alerts mentioned disruptions (like strikes or maintenance), adjust the itinerary to avoid those transport methods.

    Please present the final response as a structured travel guide.
    """

if __name__ == "__main__":
    mcp.run(transport="streamable-http")