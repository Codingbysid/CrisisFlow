import random
import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Try importing LLM libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def process_report(text: str) -> Dict[str, any]:
    """
    Process a raw text report and extract structured information.
    
    This is a dummy implementation that will be replaced with real LLM calls.
    The structure is modular to allow easy swapping with OpenAI/Gemini.
    
    Args:
        text: Raw text report from user
        
    Returns:
        Dictionary with location, hazard_type, severity, and confidence_score
    """
    text_lower = text.lower()
    
    # Dummy logic: detect hazard type from keywords
    hazard_type = None
    if "fire" in text_lower:
        hazard_type = "Fire"
    elif "flood" in text_lower:
        hazard_type = "Flood"
    elif "earthquake" in text_lower or "quake" in text_lower:
        hazard_type = "Earthquake"
    elif "hurricane" in text_lower or "storm" in text_lower:
        hazard_type = "Storm"
    elif "tornado" in text_lower:
        hazard_type = "Tornado"
    else:
        hazard_type = "Unknown"
    
    # Extract location (simple dummy: look for common location keywords)
    location = None
    location_keywords = ["street", "ave", "avenue", "road", "rd", "st", "blvd", "boulevard"]
    words = text.split()
    for i, word in enumerate(words):
        if any(keyword in word.lower() for keyword in location_keywords) and i > 0:
            # Try to get the word before the location keyword as potential location
            location = " ".join(words[max(0, i-2):i+1])
            break
    
    if not location:
        location = "Location not specified"
    
    # Random severity for dummy
    severity_options = ["Low", "Medium", "High"]
    severity = random.choice(severity_options)
    
    # Random confidence score between 0.8 and 1.0
    confidence_score = round(random.uniform(0.8, 1.0), 2)
    
    return {
        "location": location,
        "hazard_type": hazard_type,
        "severity": severity,
        "confidence_score": confidence_score
    }


async def process_report_with_llm(text: str, provider: str = "openai") -> Dict[str, any]:
    """
    Process a raw text report using a real LLM (OpenAI or Gemini).
    
    Args:
        text: Raw text report from user
        provider: LLM provider ("openai" or "gemini")
        
    Returns:
        Dictionary with location, hazard_type, severity, and confidence_score
    """
    system_prompt = """You are a disaster intelligence agent. Extract the location, hazard type, and severity from this text. 
Return ONLY valid JSON in this exact format:
{
    "location": "extracted location or 'Location not specified'",
    "hazard_type": "Fire, Flood, Earthquake, Storm, Tornado, or Unknown",
    "severity": "Low, Medium, or High",
    "confidence_score": 0.0-1.0
}"""

    try:
        if provider.lower() == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
            
        elif provider.lower() == "gemini" and GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"{system_prompt}\n\nUser text: {text}"
            response = model.generate_content(prompt)
            
            content = response.text.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
            
        else:
            # Provider not available or not configured, fall back to dummy
            raise ValueError(f"Provider {provider} not available or not configured")
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response content: {content if 'content' in locals() else 'N/A'}")
        # Fall back to dummy implementation
        return process_report(text)
        
    except Exception as e:
        print(f"Error calling LLM ({provider}): {e}")
        # Fall back to dummy implementation
        return process_report(text)

