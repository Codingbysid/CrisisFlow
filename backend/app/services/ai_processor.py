import random
import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from app.services.geocoder import get_coordinates

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
    
    # Geocode the location
    latitude, longitude = get_coordinates(location)
    
    return {
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "hazard_type": hazard_type,
        "severity": severity,
        "confidence_score": confidence_score
    }


async def process_image_with_vision(image_base64: str, text: str = "", provider: str = "openai") -> Dict[str, any]:
    """
    Process an image report using vision models (GPT-4o or Gemini Pro Vision).
    
    Args:
        image_base64: Base64 encoded image
        text: Optional text description
        provider: LLM provider ("openai" or "gemini")
        
    Returns:
        Dictionary with location, hazard_type, severity, and confidence_score
    """
    vision_prompt = """Analyze this image. Does it show a disaster? If yes, what type (Fire, Flood, Earthquake, Storm, Tornado)? 
Estimate the severity (Low, Medium, High). Extract any visible street signs or landmarks for location.
Return ONLY valid JSON in this exact format:
{
    "location": "extracted location from image or 'Location not specified'",
    "hazard_type": "Fire, Flood, Earthquake, Storm, Tornado, or Unknown",
    "severity": "Low, Medium, or High",
    "confidence_score": 0.0-1.0
}"""
    
    if text:
        vision_prompt += f"\n\nUser description: {text}"
    
    try:
        if provider.lower() == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            
            client = openai.OpenAI(api_key=api_key)
            
            # Remove data URL prefix if present
            image_data = image_base64.split(',')[1] if ',' in image_base64 else image_base64
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            # Clean JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Geocode location
            location_str = result.get("location", "Location not specified")
            latitude, longitude = get_coordinates(location_str)
            result["latitude"] = latitude
            result["longitude"] = longitude
            
            # Increase confidence for image-based reports
            if result.get("confidence_score"):
                result["confidence_score"] = min(1.0, result["confidence_score"] * 1.2)
            
            return result
            
        elif provider.lower() == "gemini" and GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro-vision')
            
            # Remove data URL prefix if present
            image_data = image_base64.split(',')[1] if ',' in image_base64 else image_base64
            import base64
            image_bytes = base64.b64decode(image_data)
            
            response = model.generate_content([
                vision_prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])
            
            content = response.text.strip()
            # Clean JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Geocode location
            location_str = result.get("location", "Location not specified")
            latitude, longitude = get_coordinates(location_str)
            result["latitude"] = latitude
            result["longitude"] = longitude
            
            # Increase confidence for image-based reports
            if result.get("confidence_score"):
                result["confidence_score"] = min(1.0, result["confidence_score"] * 1.2)
            
            return result
            
        else:
            raise ValueError(f"Provider {provider} not available for vision")
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from vision model: {e}")
        return process_report(text if text else "Image report")
    except Exception as e:
        print(f"Error calling vision model ({provider}): {e}")
        return process_report(text if text else "Image report")


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
            
            # Geocode the extracted location
            location_str = result.get("location", "Location not specified")
            latitude, longitude = get_coordinates(location_str)
            result["latitude"] = latitude
            result["longitude"] = longitude
            
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
            
            # Geocode the extracted location
            location_str = result.get("location", "Location not specified")
            latitude, longitude = get_coordinates(location_str)
            result["latitude"] = latitude
            result["longitude"] = longitude
            
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

