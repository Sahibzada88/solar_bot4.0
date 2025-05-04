from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from solar_functions import get_solar_data
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # Or gemini-1.5-pro if you're using that

# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model
class UserQuery(BaseModel):
    Location: str
    Electricity_KWH_per_month: int

@app.post("/ask")
async def ask_gemini(user_query: UserQuery):
    location = user_query.Location
    electricity = user_query.Electricity_KWH_per_month
    solar_data = get_solar_data(location)

    # Construct prompt as a single string
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

User's average electricity consumption per month: {electricity} kWh
"""

    # Send prompt to Gemini
    try:
        response = model.generate_content([prompt])
        text_output = response.text.strip()
        return JSONResponse(content={"response": text_output})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
