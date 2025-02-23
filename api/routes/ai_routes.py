from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv
import json
from typing import Optional, List

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
print(os.getenv("OPENAI_API_KEY"))
openai.api_key = ""
print(openai.api_key)

# Initialize API Router
router = APIRouter()

class SubscriptionRequest(BaseModel):
    description: str
    price: float
    dates: Optional[List[str]] = None  # Make dates optional

@router.post("/generate-subscription-info")
async def generate_subscription_info(request: SubscriptionRequest):
    try:
        # Construct the prompt for the language model
        prompt = (
            f"Given the following subscription details:\n"
            f"Description: '{request.description}'\n"
            f"Price: {request.price}\n"
        )
        
        if request.dates:
            prompt += f"Dates: {request.dates}\n\n"
        else:
            prompt += "Dates: Not provided\n\n"

        prompt += """(
            "Generate a JSON object with the following format according to the subscription details:\n"
            '''
            "For example, if the subscription is for 'Netflix', the JSON might look like this:\n"
            '''
            {
                "cancellation_link": "https://www.netflix.com/cancel",
                "alternatives": [
                    {
                        "name": "Hulu",
                        "description": "Hulu offers a wide variety of TV shows, movies, and original content. It provides both live TV and on-demand streaming options."
                    },
                    {
                        "name": "Amazon Prime Video",
                        "description": "Amazon Prime Video is a streaming service that offers a vast library of movies, TV shows, and original content. It is included with an Amazon Prime membership."
                    },
                    {
                        "name": "Disney+",
                        "description": "Disney+ is a streaming service that features content from Disney, Pixar, Marvel, Star Wars, and National Geographic."
                    }
                ]
            }
            '''
            "Ensure the response is **only valid JSON** with no additional text, explanations, or markdown formatting. "
            "Do not include introductory phrases or any content outside the JSON block."
            "Use reason in your answers - maybe start with 'you should use this over x because...' or 'this is better than y because...'"
        )"""

        # Call the OpenAI API using the chat completion method
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI that strictly outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3  # Lower temperature to make responses more deterministic
        )

        # Log the AI response
        print("AI Response:", response)

        # Extract and validate the generated JSON text
        generated_text = response.choices[0].message["content"].strip()

        # Clean up the response
        if generated_text.startswith("```json"):
            generated_text = generated_text[7:]  # Remove the starting ```json
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3]  # Remove the ending ```
        generated_text = generated_text.strip()  # Remove any leading/trailing whitespace

        try:
            print("Generated JSON:", generated_text)
            json_object = json.loads(generated_text)  # Ensure valid JSON
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON received from OpenAI API.")

        # Log the final JSON object
        print("Final JSON Object:", json_object)

        return json_object

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))