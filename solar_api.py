from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from solar_functions import get_solar_data
from datetime import datetime

class UserQuery(BaseModel):
    Location: str
    Electricity_KWH_per_month: int

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = "llama-3.3-70b-versatile"

@app.post("/ask")
async def ask_groq(user_query: UserQuery):
    location = user_query.Location
    electricity = user_query.Electricity_KWH_per_month
    solar_data = get_solar_data(location)

    prompt = f"""
You are a solar energy advisor AI. Based on the solar data provided below and the user's electricity consumption, return a detailed and structured JSON response strictly in the following format (no markdown or text):

{{
  "response": "Brief one-sentence recommendation.",
  "json_list": [
    {{
      "name": "recommended_system_size_kw",
      "short_description": "Short explanation of the recommended system size."
    }},
    {{
      "name": "number_of_panels",
      "short_description": "Short explanation of how many panels are needed."
    }},
    {{
      "name": "panel_type",
      "short_description": "Recommendation of the panel type with reason."
    }},
    {{
      "name": "estimated_annual_production_kwh",
      "short_description": "Estimated yearly production of the system in kWh."
    }},
    {{
      "name": "percentage_of_usage_covered",
      "short_description": "How much of the user's needs are met by this system."
    }},
    {{
      "name": "battery_storage_kwh",
      "short_description": "Recommended battery capacity in kWh."
    }},
    {{
      "name": "backup_power_duration_hours",
      "short_description": "How long the battery can provide backup in hours."
    }},
    {{
      "name": "system_type",
      "short_description": "Type of solar system recommended (grid-tied, hybrid, off-grid)."
    }}
  ],
  "detailed_summary": "A longer summary in paragraph form with assumptions if any.",
  "confidence_percent": A number between 80 and 100,
  "timestamp": "Current UTC time in ISO 8601 format (e.g., 2025-05-04T15:00:00Z)"
}}

Solar data from our API:
{solar_data}

User input:
- Location: {location}
- Monthly Electricity Consumption: {electricity} kWh

Please generate only the JSON object. Do not add any extra explanation or formatting.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    # Try to parse JSON content safely
    import json
    try:
        content = response.choices[0].message.content.strip()
        json_response = json.loads(content)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to parse model response", "raw_response": content})

    return JSONResponse(content=json_response)

@app.post("/ask2")
async def ask_groq(user_query: UserQuery):
    location = user_query.Location
    electricity = user_query.Electricity_KWH_per_month

    # Fetch solar data using the solar_functions module
    solar_data = get_solar_data(location)
    prompt = f"""
    You are a solar energy advisor.

    Based on the following solar data from our API:
    {solar_data}

    The user has provided the following input:
    Location: {location}
    Monthly Electricity Consumption: {electricity} kWh
 
    Please analyze the data and provide a clear, professional recommendation that includes:
    1. The recommended size of the solar system in kilowatts (kW) needed to offset the user's monthly electricity usage.
    2. The recommended capacity of the solar inverter (in kW) that matches the system size.
    3. The number of solar panels required, based on standard panel capacities (e.g., 400W or 450W), and which panel size is most appropriate.
    4. Any assumptions you make in your calculation (such as average daily sunlight hours, system efficiency, etc.).

    The response should be easy to understand for a non-technical user, and it should highlight the best-fit solution based on their location and electricity needs.
    """


    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return JSONResponse(content={"response": response.choices[0].message.content.replace("*", "")})


