import os
from mcp.server.fastmcp import FastMCP
import requests
from datetime import datetime
import logging
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.DEBUG)

mcp = FastMCP("AgriAdvisorAI")


@mcp.tool()
def say_hello(name: str) -> str:
    """
    Return a friendly greeting to the user with the given name.
    
    Args:
        name (str): The name of the user to greet.
    
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"


@mcp.tool()
def get_commodity_price(name: str, commodity: str) -> str:
    """
    Fetch the latest commodity prices for a given commodity and user, using the user's location.
    
    Args:
        name (str): The user's name. Used to determine their location.
        commodity (str): The commodity for which to fetch prices.
    
    Returns:
        str: A formatted summary of recent prices for the commodity in the user's region, grouped by market and date.
    """
    sending_name = name.title()
    sending_commodity = commodity.title()
    api_key = os.getenv("MANDI_API_KEY")
    try:
        user_location = get_user_location_from_database(sending_name)
        state = user_location["state"]
        district = user_location["district"]

        url = (
            "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"
            "?api-key=579b464db66ec23bdd000001058a4475183144cc444349d08700a279"
            f"&format=json&offset=0&limit=10"
            f"&filters[State]={state}&filters[District]={district}&filters[Commodity]={sending_commodity}"
        )

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        data = clean_price_data(data["records"])
        logging.info(data)
        return data
    except Exception as e:
        logging.error(f"Error fetching commodity price: {e}")
        return f"Failed to fetch commodity price: {e}"


@mcp.tool()
def get_weather_forecast(name: str) -> str:
    """
    Fetch the 5-day weather forecast for the user's location, based on their name.
    
    Args:
        name (str): The user's name. Used to determine their location.
    
    Returns:
        str: A formatted weather forecast for the next 5 days for the user's district.
    """
    try:
        user_location = get_user_location_from_database(name)
        district = user_location["district"]

        API_KEY = "9b5f97f06cfe4a5482f200910252207"
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={district}&days=5"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        forecast_days = data["forecast"]["forecastday"]

        lines = [f"Weather forecast for {district}:\n"]
        for day in forecast_days:
            date = day["date"]
            condition = day["day"]["condition"]["text"]
            avg_temp = day["day"]["avgtemp_c"]
            total_rain = day["day"]["totalprecip_mm"]

            lines.append(f"{date}: {condition}, Avg Temp: {avg_temp}°C, Rain: {total_rain} mm")
        
        logging.info(lines)

        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Error fetching weather forecast: {e}")
        return f"Failed to fetch weather forecast: {e}"


def get_user_location(name: str) -> dict:
    """
    Look up the user's location (state and district) based on their name.
    
    Args:
        name (str): The user's name.
    
    Returns:
        dict: A dictionary with 'state' and 'district' keys.
    
    Raises:
        ValueError: If the user is not found in the user map.
    """
    user_map = {
        "Sameer": {"state": "Maharashtra", "district": "Nagpur"},
        "Rajesh": {"state": "Maharashtra", "district": "Mumbai"},
        "Suresh": {"state": "Maharashtra", "district": "Pune"}
    }
    if name not in user_map:
        raise ValueError(f"Unknown user: {name}")
    return user_map[name]


def get_user_location_from_database(name: str) -> dict:
    """
    Look up the user's location (state and district) based on their name.
    
    Args:
        name (str): The user's name.
    """
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from backend.database import get_session
    from backend.repositories.farmer_repository import FarmerRepository
    farmer_repository = FarmerRepository()
    farmer = farmer_repository.get_farmer_by_name(name)
    return {"state": farmer.state, "district": farmer.city}


def clean_price_data(records: list) -> str:
    """
    Clean and format raw commodity price records for LLM consumption.
    
    Args:
        records (list): List of raw price records from the API.
    
    Returns:
        str: A formatted string summarizing prices by market and date.
    """
    for entry in records:
        entry["Arrival_Date"] = datetime.strptime(entry["Arrival_Date"], "%d/%m/%Y")

    records.sort(key=lambda x: (x["Market"], x["Arrival_Date"]))

    markets = defaultdict(list)
    for entry in records:
        markets[entry["Market"]].append(entry)

    summary = []
    for market, entries in markets.items():
        summary.append(f"Market: {market}")
        for e in entries:
            summary.append(
                f"  Date: {e['Arrival_Date'].strftime('%d-%b-%Y')}, "
                f"Min: ₹{e['Min_Price']}, Max: ₹{e['Max_Price']}, Modal: ₹{e['Modal_Price']}"
            )
        summary.append("")  

    final_text = "\n".join(summary)
    logging.info(final_text)
    return final_text



if __name__ == "__main__":
    mcp.run(transport="stdio")