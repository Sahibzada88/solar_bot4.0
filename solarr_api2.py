from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import re
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from solar_functions import get_solar_data

class UserQuery(BaseModel):
    Location: str
    Electricity_KWH_per_month: int

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.post("/ask")
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
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return JSONResponse(content={"response": response.choices[0].message.content.replace("*", "")})

