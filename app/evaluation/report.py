import google.generativeai as genai
import json
from app.models import APIKey
API_KEY = APIKey.objects.filter(is_active=True).order_by('-created_at').first().key
genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

def generate_report(result):
    prompt = f"""
    Format the following JSON response in a clean and structured format without introducing errors or making any interpretations.

    Perform the following calculations:

    1. Determine the total possible score:
    - Part A: Count the number of questions labeled as Part A and multiply by 2 marks each.
    - Part B: Count the number of questions labeled as Part B and multiply by 13 marks each.
    - Part C: Count the number of questions labeled as Part C and multiply by 14 marks each.

    2. Calculate the user’s total score by summing up the "marks_awarded" values from the JSON response.

    3. Display the user’s total score out of the computed total possible score.
    4. remove all the special characters like \n and the * etc
    Ensure all calculations are accurate and that no marks are added or subtracted incorrectly.

    JSON Data:
    {result} 
    """
    # Generate evaluation using GenAI
    response = model.generate_content(prompt)

    return response.text 

