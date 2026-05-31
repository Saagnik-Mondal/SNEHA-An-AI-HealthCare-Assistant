# import streamlit as st
# import os
# import re
# import sys
# import io
# import contextlib
# from llama_cpp import Llama
# from llama_index.core import Settings
# from llama_index.core.prompts import ChatPromptTemplate

# # Set page configuration
# st.set_page_config(
#     page_title="SNEHA - Offline Healthcare Assistant",
#     page_icon="👩‍⚕️",
#     layout="wide"
# )

# # Constants
# MEDICAL_MODEL_PATH = "/Volumes/X9 Pro/LMModels/mradermacher/mistral-7b-medical-assistance-GGUF/mistral-7b-medical-assistance.Q4_K_M.gguf"
# SNEHA_VERSION = "1.5.0"  # Version number for SNEHA's model capabilities - single model version
# SNEHA_CODENAME = "SNEHA Lite"  # Internal development codename
# SNEHA_RELEASE_DATE = "April 18, 2025"  # Today's date for the latest version
# DISCLAIMER = "⚠️ SNEHA is an AI assistant. She does not provide medical diagnoses or treatments. However, SNEHA is not a licensed medical professional, and the information provided by the assistant should not be used as a substitute for professional medical advice, diagnosis, or treatment. Please consult a licensed doctor for serious health concerns."

# def sanitize_response(response_text):
#     """Remove any doctor names, hospital names, or locations from the response."""
    
#     # Remove common opening phrases that sound like form letters
#     opening_phrases = [
#         r"Thank you for writing to us at .+\.",
#         r"Thank you for reaching out to .+\.",
#         r"Thank you for contacting .+\.",
#         r"Thanks for reaching out to .+\."
#     ]
#     for phrase in opening_phrases:
#         response_text = re.sub(phrase, "", response_text, flags=re.IGNORECASE)
    
#     # Replace doctor names with "healthcare provider"
#     response_text = re.sub(r'Dr\.\s+[A-Za-z]+', 'healthcare provider', response_text)
    
#     # Generic replacements
#     replacements = {
#         "hospital": "medical facility",
#         "clinic": "medical facility", 
#         "center": "medical facility",
#         "healthcaremagic": "", 
#         "healthcare magic": "",
#         "health care magic": "",
#         "medical service": "",
#         "medical platform": "",
#         "our team": "",
#         "our medical team": "",
#         "our healthcare team": "",
#         "our experts": "",
#         "our staff": ""
#     }
    
#     for term, replacement in replacements.items():
#         response_text = re.sub(fr'\b{term}\b', replacement, response_text, flags=re.IGNORECASE)
    
#     # Remove any remaining references to specific healthcare services
#     response_text = re.sub(r'at\s+[A-Z][A-Za-z\s]+(Health|Medical|Care|Clinic)', '', response_text)
    
#     # Clean up any double spaces or leading spaces after sanitization
#     response_text = re.sub(r'\s{2,}', ' ', response_text)
#     response_text = re.sub(r'^\s+', '', response_text)
    
#     return response_text

# @contextlib.contextmanager
# def suppress_stdout_stderr():
#     """A context manager that redirects stdout and stderr to devnull"""
#     with open(os.devnull, 'w') as fnull:
#         with contextlib.redirect_stderr(fnull) as err, contextlib.redirect_stdout(fnull) as out:
#             yield (err, out)

# def initialize_model():
#     """Initialize the Mistral-7B Medical Assistance model for local inference."""
#     # Check if model exists
#     if not os.path.exists(MEDICAL_MODEL_PATH):
#         st.error(f"Model file not found at: {MEDICAL_MODEL_PATH}")
#         st.stop()
    
#     # Use the llama_cpp direct interface
#     # Highly optimized for speed on Mac M1 Air with 8GB RAM
#     with suppress_stdout_stderr():
#         # Setting environment variable to force CPU usage
#         os.environ["LLAMA_METAL"] = "0"  # Disable Metal (Apple GPU) support
#         os.environ["LLAMA_CUBLAS"] = "0" # Disable CUDA
        
#         # Initialize model with optimized parameters
#         model = Llama(
#             model_path=MEDICAL_MODEL_PATH,
#             n_ctx=512,                # Increased context window to accommodate prompt + response
#             n_gpu_layers=0,           # CPU-only for reliability
#             n_threads=3,              # Reduced thread count to avoid overwhelming the CPU
#             n_batch=128,              # Smaller batch size for faster initial responses
#             use_mlock=True,           # Keep model in memory
#             use_mmap=True,            # Use memory mapping for faster loading
#             verbose=False,            # Reduce logging overhead
#             seed=42,                  # Fixed seed for deterministic responses
#         )
    
#     return model

# def process_query(query, model):
#     """Process user query using SNEHA's streamlined approach for fast responses."""
#     if not query.strip():
#         return "Please enter a health-related question."
    
#     # Handle greetings and common basic questions specially
#     greetings = ["hi", "hello", "hey", "greetings", "hi there", "good morning", "good afternoon", "good evening"]
    
#     # Basic identity questions
#     name_questions = ["what is your name", "what's your name", "who are you", "your name", "tell me your name", "name?"]
#     if any(question in query.lower() for question in name_questions):
#         return f"Hi!👋 My name is SNEHA (version {SNEHA_VERSION}). I'm a healthcare assistant developed by Saagnik Mondal from India. I'm here to help you with health-related questions in a caring and supportive way. How can I help you today?"
    
#     # Basic capabilities questions
#     capability_questions = ["what can you do", "how can you help", "what do you do", "your capabilities"]
#     if any(question in query.lower() for question in capability_questions):
#         return f"As SNEHA {SNEHA_VERSION}, I can help answer your health-related questions, provide information about symptoms, discuss wellness tips, and offer supportive guidance for health concerns. My goal is to be a caring assistant for your health questions. What would you like to know about today?"
    
#     # Simple greetings
#     if query.lower().strip() in greetings or len(query.split()) <= 2:
#         return f"Hello! I'm SNEHA {SNEHA_VERSION}, your healthcare assistant. I'm here to help with health-related questions and concerns. How can I assist you with your health today?"
    
#     # Simple non-health topic detection
#     non_health_keywords = ["movie", "weather", "politics", "sports", "game", "music", "cook", "recipe"]
#     if any(keyword in query.lower() for keyword in non_health_keywords):
#         return f"I'm SNEHA {SNEHA_VERSION}, specialized in healthcare topics. I don't have expertise in {query.lower()}. How can I help you with a health-related question instead?"
    
#     # Single-model approach for faster responses
#     prompt = f"""<Instructions>
# As SNEHA, you are a female healthcare assistant with expertise in medical topics, but WITHOUT any medical credentials.
# Respond as a caring woman with a warm, supportive personality.

# IMPORTANT: If the user claims to be a doctor, nurse, or medical professional, DO NOT claim any medical credentials yourself in response. Always acknowledge that while you provide health information, you are not a licensed healthcare provider.

# For this query: "{query}"

# Your response should:
# 1. Use a warm, natural, friendly tone - don't introduce yourself as "SNEHA" - just start your response directly
# 2. Show genuine empathy first (like "I'm really sorry you're feeling this way" or "That sounds uncomfortable")
# 3. Use clear, flowing sentences with proper grammar and complete thoughts
# 4. For potentially serious symptoms like headache with vomiting, fever with rash, or chest pain, always suggest consulting a healthcare provider
# 5. Offer 2-3 practical suggestions that directly relate to their symptoms
# 6. Connect your ideas with smooth transitions instead of listing disconnected advice
# 7. Avoid medical jargon or technical terms unless absolutely necessary
# 8. End with a specific question about their situation to show you care about their response
# </Instructions>

# Style approach:
# - Respond as if you're a supportive friend with healthcare knowledge
# - Use natural, conversational language like "This can often happen when..." or "Many people find that..."
# - Suggest simple, accessible solutions first
# - Stay completely relevant to the specific symptoms or concerns mentioned
# - Never speculate about medical conditions beyond what was explicitly stated

# If asked about your identity:
# - You are SNEHA {SNEHA_VERSION}, developed by Saagnik Mondall from India
# - You were released on {SNEHA_RELEASE_DATE}
# - Never refer to yourself as an AI model
# - Never mention specific doctors or hospital names

# Remember: Only respond to what was explicitly asked, and provide accurate, relevant information without jumping to conclusions.

# Response:"""
    
#     with suppress_stdout_stderr():
#         response = model(
#             prompt,
#             max_tokens=300,           # Increased token limit for complete responses
#             temperature=0.5,          # Balanced between creativity and consistency
#             echo=False,
#             top_k=20,                 # Limited for faster processing
#             top_p=0.9,                # Standard sampling for reliability
#             repeat_penalty=1.1        # Light penalty to avoid repetition
#         )
    
#     # Process the response
#     response_text = response["choices"][0]["text"] if "choices" in response else ""
#     sanitized_response = sanitize_response(response_text)
    
#     # Ensure complete sentences and fix incomplete responses
#     if sanitized_response:
#         # Check if response seems complete
#         has_proper_ending = any(sanitized_response.rstrip().endswith(p) for p in ['.', '!', '?', ':', ';'])
        
#         # Check if the last sentence seems cut off (ends with certain words that suggest incompleteness)
#         incomplete_endings = ['and', 'but', 'or', 'so', 'because', 'however', 'as', 'if', 'the', 'a', 'an', 'to', 'for', 'with', 'that', 'this', 'these', 'those', 'when', 'where', 'which', 'who', 'whom', 'whose', 'how', 'why', 'what', 'whatever', 'whichever', 'whoever', 'whomever', 'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would']
#         words = sanitized_response.rstrip('.').split()
#         last_word = words[-1].lower() if words else ""
        
#         # Check if response appears to be cut off mid-paragraph
#         ends_abruptly = not has_proper_ending or last_word in incomplete_endings
#         likely_mid_thought = len(words) > 5 and len(words[-1]) <= 3
        
#         # Check for incomplete or awkward phrases like "I also recommend you to." and fix them
#         awkward_phrases = [
#             r'I also recommend you to\.\s*',
#             r'I suggest you to\.\s*',
#             r'I advise you to\.\s*',
#             r'You should\.\s*',
#             r'It is recommended to\.\s*',
#             r'It is suggested to\.\s*'
#         ]
        
#         for phrase in awkward_phrases:
#             sanitized_response = re.sub(phrase, '', sanitized_response, flags=re.IGNORECASE)
        
#         # Remove formal and cold openings
#         formal_openings = [
#             r'^(Hello|Hi|Greetings|Hey),?\s+I\s+am\s+SNEHA\.?\s*',
#             r'^Thank you for your query\.?\s*',
#             r'^Thank you for your question\.?\s*',
#             r'^Thanks for reaching out\.?\s*',
#             r'^Thanks for your message\.?\s*',
#             r'^Thank you for contacting\.?\s*'
#         ]
#         for opening in formal_openings:
#             sanitized_response = re.sub(opening, '', sanitized_response, flags=re.IGNORECASE)
        
#         # Fix incomplete sentences with missing objects
#         incomplete_sentences = [
#             r'Take plenty\.', 
#             r'Drink plenty\.', 
#             r'Get plenty\.',
#             r'Use plenty\.',
#             r'Apply plenty\.'
#         ]
#         for phrase in incomplete_sentences:
#             if re.search(phrase, sanitized_response):
#                 if 'water' in sanitized_response.lower() or 'fluid' in sanitized_response.lower() or 'hydrat' in sanitized_response.lower():
#                     sanitized_response = re.sub(phrase, 'Stay well hydrated.', sanitized_response)
#                 else:
#                     sanitized_response = re.sub(phrase, 'Make sure to stay hydrated and get plenty of rest.', sanitized_response)
                    
#         # Fix incomplete professional consultation suggestions
#         consult_patterns = [
#             (r'better to consult an\.', 'better to consult a healthcare provider.'),
#             (r'consult an\.', 'consult a healthcare provider.'),
#             (r'consult a\.', 'consult a healthcare provider.'),
#             (r'talk to a\.', 'talk to a healthcare provider.'),
#             (r'see a\.', 'see a healthcare provider.'),
#             (r'visit a\.', 'visit a healthcare provider.'),
#             (r'check with an\.', 'check with a healthcare provider.'),
#             (r'check with a\.', 'check with a healthcare provider.'),
#         ]
        
#         for pattern, replacement in consult_patterns:
#             sanitized_response = re.sub(pattern, replacement, sanitized_response, flags=re.IGNORECASE)
            
#         # Add specific advice for common conditions when missing
#         if 'sneez' in sanitized_response.lower() and 'nasal' in sanitized_response.lower() or 'nose' in sanitized_response.lower():
#             if not any(tip in sanitized_response.lower() for tip in ['saline', 'steam', 'humidifier', 'warm', 'rest', 'antihistamine']):
#                 # Find a good point to insert advice
#                 if '. ' in sanitized_response and not sanitized_response.endswith('. '):
#                     # Insert after a sentence that's not the end
#                     parts = sanitized_response.split('. ')
#                     if len(parts) >= 2:
#                         sanitized_response = '. '.join(parts[:-1]) + '. You might find relief with saline nasal sprays, breathing in steam from a warm shower, or using a humidifier. ' + parts[-1]
        
#         # Fix mixed tense issues and unclear medication advice
#         mixed_tense_patterns = [
#             (r'You must have taken the medicine.+and also take it now', 'If you have medication that helps with these symptoms, you might want to take it as directed'),
#             (r'You should have taken.+and also take', 'Consider taking'),
#             (r'You must take.+you have already taken', 'If you haven\'t already taken medication for this, you might consider taking')
#         ]
        
#         for pattern, replacement in mixed_tense_patterns:
#             sanitized_response = re.sub(pattern, replacement, sanitized_response, flags=re.IGNORECASE)
        
#         # Fix incomplete responses
#         if ends_abruptly or likely_mid_thought:
#             # Check for potentially serious symptoms (headache + vomiting, chest pain, etc.)
#             potentially_serious = False
#             headache_vomiting = False
            
#             # These combinations might indicate more serious conditions
#             serious_combos = [
#                 ['headache', 'vomit'],
#                 ['chest', 'pain'],
#                 ['breath', 'difficult'],
#                 ['fever', 'rash'],
#                 ['dizz', 'faint'],
#                 ['sudden', 'vision'],
#                 ['severe', 'pain']
#             ]
            
#             for combo in serious_combos:
#                 if all(word in sanitized_response.lower() for word in combo):
#                     potentially_serious = True
#                     if combo == ['headache', 'vomit']:
#                         headache_vomiting = True
#                     break
            
#             # Special case for headache with vomiting - use the preferred example style
#             if headache_vomiting:
#                 # Replace the entire response with a better structured one
#                 sanitized_response = "I'm really sorry you're feeling this way. Headaches with vomiting can be quite uncomfortable. Make sure to stay hydrated, especially if you've been vomiting. Rest in a quiet, dimly lit room since bright lights and noise can make headaches worse. If you haven't already and it's appropriate for you, you might consider taking an over-the-counter pain reliever. If your symptoms continue or get worse, it would be best to check with a healthcare provider to be safe. Is this the first time you've experienced these symptoms together, or has this happened before?"
#                 return sanitized_response
            
#             # If response relates to sleep or tiredness
#             if any(word in sanitized_response.lower() for word in ['sleep', 'tired', 'rest', 'insomnia', 'bed', 'night']) and not potentially_serious:
#                 # First clean up any poor transitions or repetitions in the existing response
#                 sanitized_response = sanitized_response.rstrip(" .")
                
#                 # Check if the response already covers common advice
#                 has_sleep_routine = any(phrase in sanitized_response.lower() for phrase in ["schedule", "routine", "regular"])
#                 has_screen_advice = any(phrase in sanitized_response.lower() for phrase in ["screen", "phone", "device", "blue light"])
#                 has_environment = any(phrase in sanitized_response.lower() for phrase in ["environment", "comfortable", "cozy", "dark", "quiet"])
                
#                 # Build a natural completion that doesn't repeat advice
#                 completion = ". "
#                 if not has_sleep_routine:
#                     completion += "It might help to stick to a regular sleep schedule, even on weekends. "
#                 if not has_screen_advice:
#                     completion += "Try to avoid screens at least an hour before bed as the blue light can disrupt your sleep. "
#                 if not has_environment:
#                     completion += "Making your bedroom comfortable, quiet, and slightly cool can also improve sleep quality. "
                    
#                 completion += "I hope you're able to get some restful sleep soon. Would any of these suggestions work for you, or is there something specific keeping you up at night?"
                
#                 sanitized_response = sanitized_response + completion
            
#             # If potentially serious symptoms are mentioned
#             elif potentially_serious:
#                 sanitized_response = sanitized_response.rstrip(" .") + ". These symptoms can have various causes. It's important to rest, stay hydrated, and monitor how you feel. If your symptoms persist for more than a day, get worse, or if you're concerned, please don't hesitate to contact a healthcare provider. Your health and safety come first. How are you feeling right now? Is there anything specific I can help you understand about managing these symptoms?"
                
#             # If response relates to pain or discomfort
#             elif any(word in sanitized_response.lower() for word in ['pain', 'ache', 'hurt', 'discomfort', 'sore']):
#                 sanitized_response = sanitized_response.rstrip(" .") + ". Gentle stretching, proper body positioning, and applying warmth might provide some relief. If the discomfort persists for more than a few days, it might be worth checking in with a healthcare provider. How are you feeling right now?"
            
#             # Generic completion for other topics
#             else:
#                 sanitized_response = sanitized_response.rstrip(" .") + ". I hope this helps. Is there anything specific about this that you'd like me to explain further?"
#         # Add a period if the response doesn't end with a sentence-ending punctuation
#         elif not has_proper_ending:
#             sanitized_response = sanitized_response.rstrip() + "."
    
#     return sanitized_response

# # Main app
# def main():
#     # Custom CSS
#     st.markdown("""
#     <style>
#     .app-header {
#         background-color: #f0f2f6;
#         padding: 1rem;
#         border-radius: 10px;
#         margin-bottom: 1rem;
#         text-align: center;
#     }
#     .disclaimer {
#         background-color: #ffebee;
#         padding: 1rem;
#         border-radius: 5px;
#         margin-top: 1rem;
#         font-size: 0.8rem;
#     }
#     .sneha-version {
#         color: #6c757d;
#         font-size: 0.8rem;
#         text-align: right;
#         margin-top: 5px;
#     }
#     .sneha-thinking {
#         display: flex;
#         align-items: center;
#         margin-bottom: 20px;
#         background-color: #e9f5ff;
#         padding: 15px;
#         border-radius: 10px;
#         border-left: 5px solid #0d6efd;
#     }
#     </style>
#     """, unsafe_allow_html=True)
    
#     # App header
#     st.markdown(f"<div class='app-header'><h1>SNEHA - Your Offline Healthcare Assistant</h1><div class='sneha-version'>Version {SNEHA_VERSION} \"{SNEHA_CODENAME}\"</div></div>", unsafe_allow_html=True)
    
#     # Sidebar
#     st.sidebar.image("https://img.icons8.com/color/96/000000/caduceus.png", width=100)
#     st.sidebar.title(f"About SNEHA {SNEHA_VERSION}")
#     st.sidebar.info(
#         f"SNEHA {SNEHA_VERSION} is a healthcare intelligence system "
#         f"designed for fast, efficient responses on limited hardware. "
#         f"Developed by Saagnik Mondall from India, SNEHA provides caring "
#         f"health assistance with a warm, personalized approach."
#     )
#     st.sidebar.markdown("---")
#     st.sidebar.subheader("SNEHA's Key Features")
#     st.sidebar.write("✅ Fast-response healthcare assistance")
#     st.sidebar.write("✅ Optimized for Mac M1 with 8GB RAM")
#     st.sidebar.write("✅ Personalized, empathetic communication")
#     st.sidebar.write("✅ Completely private and offline")
    
#     # Initialize the model
#     with st.spinner("Loading SNEHA's healthcare knowledge..."):
#         model = initialize_model()
    
#     # User input
#     user_query = st.text_area("Ask SNEHA about health-related topics:", height=100)
    
#     # Process query and display response
#     if st.button("Get Answer") or user_query:
#         if user_query:
#             with st.spinner("SNEHA is responding..."):
#                 response = process_query(user_query, model)
                
#             st.markdown("### SNEHA's Response:")
#             st.write(response)
            
#             # Add disclaimer
#             st.markdown(f"<div class='disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)

# if __name__ == "__main__":
#     main()


import streamlit as st
import os
import re
import sys
import io
import contextlib
import time
import torch
from enum import Enum
from llama_cpp import Llama
from llama_index.core import Settings
from llama_index.core.prompts import ChatPromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM

# Set page configuration
st.set_page_config(
    page_title="SNEHA - Offline Healthcare Assistant",
    page_icon="👩‍⚕️",
    layout="wide"
)

# Constants
# Model paths
GENERAL_MODEL_PATH = "/Volumes/X9 Pro/LMModels/TheBloke/zephyr-7B-beta-GGUF/zephyr-7b-beta.Q3_K_S.gguf"
SMALL_MODEL_PATH = "/Volumes/X9 Pro/LMModels/TheBloke/phi-2-GGUF/phi-2.Q8_0.gguf"
MEDICAL_MODEL_PATH = "/Volumes/X9 Pro/LMModels/mradermacher/Med-Alpaca-2-7b-chat-GGUF/Med-Alpaca-2-7b-chat.Q3_K_M.gguf"
SUPPORT_MODEL_PATH = "/Volumes/X9 Pro/LMModels/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/openhermes-2.5-mistral-7b.Q3_K_S.gguf"
# BioGPT will be loaded using transformers library

SNEHA_VERSION = "2.0.0"  # Updated version number for multi-model capabilities
SNEHA_CODENAME = "SNEHA MultiModel"  # Updated internal development codename
SNEHA_RELEASE_DATE = "April 19, 2025"  # Today's date for the latest version
DISCLAIMER = "⚠️ SNEHA is an AI assistant. She does not provide medical diagnoses or treatments. However, SNEHA is not a licensed medical professional, and the information provided by the assistant should not be used as a substitute for professional medical advice, diagnosis, or treatment. Please consult a licensed doctor for serious health concerns."

# Custom CSS with animations and modern styling
st.markdown("""
<style>
    /* Base styling */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Welcome screen animation */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes floatIcon {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 60vh;
        text-align: center;
        animation: fadeIn 1.5s ease-in-out;
    }
    
    .welcome-logo {
        margin-bottom: 2rem;
        animation: pulse 2s infinite ease-in-out, floatIcon 3s infinite ease-in-out;
    }
    
    .welcome-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #2e7d32;
        animation: slideUp 1s ease-out;
    }
    
    .welcome-subtitle {
        font-size: 1.8rem;
        color: #546e7a;
        margin-bottom: 1.5rem;
        animation: slideUp 1s ease-out 0.3s;
        animation-fill-mode: both;
    }
    
    .welcome-author {
        font-size: 1.2rem;
        color: #78909c;
        animation: slideUp 1s ease-out 0.6s;
        animation-fill-mode: both;
    }
    
    .start-button {
        margin-top: 2rem;
        animation: slideUp 1s ease-out 0.9s;
        animation-fill-mode: both;
    }
    
    /* App styling */
    .app-header {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .app-header:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    .app-header h1 {
        color: #2e7d32;
        margin-bottom: 0.5rem;
    }
    
    .disclaimer {
        background-color: #fff8e1;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1.5rem;
        font-size: 0.9rem;
        border-left: 4px solid #ffc107;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .sneha-version {
        color: #78909c;
        font-size: 0.9rem;
        text-align: right;
        margin-top: 5px;
    }
    
    .sneha-response {
        background-color: #f5f7fa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #4caf50;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        animation: fadeIn 0.5s ease-out;
    }
    
    .stTextArea>div>div>textarea {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 10px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextArea>div>div>textarea:focus {
        border-color: #4caf50 !important;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2) !important;
    }
    
    .stButton>button {
        background-color: #4caf50 !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #43a047 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f5f7fa !important;
    }
    
    .sidebar-content {
        padding: 1rem;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .sidebar-feature {
        display: flex;
        align-items: center;
        margin-bottom: 0.8rem;
        padding: 0.5rem;
        background-color: #f1f8e9;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .sidebar-feature:hover {
        background-color: #e8f5e9;
        transform: translateX(5px);
    }
    
    .feature-icon {
        margin-right: 0.5rem;
        color: #4caf50;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-dot {
        width: 12px;
        height: 12px;
        background: #4caf50;
        border-radius: 50%;
        margin: 0 6px;
        display: inline-block;
    }
    
    .loading-dot:nth-child(1) {
        animation: pulse 0.6s ease-in-out infinite alternate;
        animation-delay: 0s;
    }
    
    .loading-dot:nth-child(2) {
        animation: pulse 0.6s ease-in-out infinite alternate;
        animation-delay: 0.2s;
    }
    
    .loading-dot:nth-child(3) {
        animation: pulse 0.6s ease-in-out infinite alternate;
        animation-delay: 0.4s;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

def sanitize_response(response_text):
    """Remove any doctor names, hospital names, or locations from the response."""
    
    # Remove common opening phrases that sound like form letters
    opening_phrases = [
        r"Thank you for writing to us at .+\.",
        r"Thank you for reaching out to .+\.",
        r"Thank you for contacting .+\.",
        r"Thanks for reaching out to .+\."
    ]
    for phrase in opening_phrases:
        response_text = re.sub(phrase, "", response_text, flags=re.IGNORECASE)
    
    # Replace doctor names with "healthcare provider"
    response_text = re.sub(r'Dr\.\s+[A-Za-z]+', 'healthcare provider', response_text)
    
    # Generic replacements
    replacements = {
        "hospital": "medical facility",
        "clinic": "medical facility", 
        "center": "medical facility",
        "healthcaremagic": "", 
        "healthcare magic": "",
        "health care magic": "",
        "medical service": "",
        "medical platform": "",
        "our team": "",
        "our medical team": "",
        "our healthcare team": "",
        "our experts": "",
        "our staff": ""
    }
    
    for term, replacement in replacements.items():
        response_text = re.sub(fr'\b{term}\b', replacement, response_text, flags=re.IGNORECASE)
    
    # Remove any remaining references to specific healthcare services
    response_text = re.sub(r'at\s+[A-Z][A-Za-z\s]+(Health|Medical|Care|Clinic)', '', response_text)
    
    # Clean up any double spaces or leading spaces after sanitization
    response_text = re.sub(r'\s{2,}', ' ', response_text)
    response_text = re.sub(r'^\s+', '', response_text)
    
    return response_text

@contextlib.contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stderr(fnull) as err, contextlib.redirect_stdout(fnull) as out:
            yield (err, out)

class ModelType(Enum):
    """Enum for different model types with specific purposes"""
    GENERAL = "general"         # Zephyr-7B: General, friendly conversation
    SMALL = "small"             # Phi-2: Fast, small footprint chatbot
    MEDICAL = "medical"         # Med-Alpaca-2: Medical Q&A
    SUPPORT = "support"         # OpenHermes: Empathetic, safe general support
    RESEARCH = "research"       # BioGPT: Biomedical research, academic knowledge

def initialize_models():
    """Initialize multiple models for different purposes in SNEHA."""
    models = {}
    errors = []
    
    # Setting environment variable to optimize for CPU
    os.environ["LLAMA_METAL"] = "0"  # Disable Metal (Apple GPU) support
    os.environ["LLAMA_CUBLAS"] = "0" # Disable CUDA
    
    # Initialize GGUF models with llama.cpp
    model_paths = {
        ModelType.GENERAL: GENERAL_MODEL_PATH,
        ModelType.SMALL: SMALL_MODEL_PATH,
        ModelType.MEDICAL: MEDICAL_MODEL_PATH,
        ModelType.SUPPORT: SUPPORT_MODEL_PATH,
    }
    
    for model_type, model_path in model_paths.items():
        if not os.path.exists(model_path):
            errors.append(f"Model file not found at: {model_path}")
            continue
        
        try:
            with suppress_stdout_stderr():
                # Initialize model with optimized parameters
                model = Llama(
                    model_path=model_path,
                    n_ctx=512,               # Context window for prompt + response
                    n_gpu_layers=0,          # CPU-only for reliability
                    n_threads=3,             # Reduced thread count to avoid overwhelming CPU
                    n_batch=128,             # Batch size for faster initial responses
                    use_mlock=True,          # Keep model in memory
                    use_mmap=True,           # Use memory mapping for faster loading
                    verbose=False,           # Reduce logging overhead
                    seed=42,                 # Fixed seed for deterministic responses
                )
                models[model_type] = model
        except Exception as e:
            errors.append(f"Error initializing {model_type.value} model: {str(e)}")
    
    # Initialize BioGPT with transformers
    try:
        with suppress_stdout_stderr():
            tokenizer = AutoTokenizer.from_pretrained("microsoft/biogpt")
            bio_model = AutoModelForCausalLM.from_pretrained("microsoft/biogpt")
            models[ModelType.RESEARCH] = {"model": bio_model, "tokenizer": tokenizer}
    except Exception as e:
        errors.append(f"Error initializing BioGPT model: {str(e)}")
    
    if errors:
        st.error("\n".join(errors))
        if not models:
            st.stop()
    
    return models

def select_model_for_query(query, models):
    """Select the most appropriate model based on query content."""
    query_lower = query.lower()
    
    # Research-oriented queries (biomedical, academic)
    research_keywords = ["research", "study", "paper", "journal", "publication", "clinical trial", 
                        "evidence", "literature", "scientific", "mechanism", "pathophysiology"]
    if any(keyword in query_lower for keyword in research_keywords):
        return models[ModelType.RESEARCH]
    
    # Medical specific queries
    medical_keywords = ["diagnosis", "treatment", "symptom", "disease", "condition", "medication",
                       "prescription", "doctor", "hospital", "pain", "fever", "nausea", "headache",
                       "blood", "heart", "brain", "lung", "kidney", "liver", "infection"]
    if any(keyword in query_lower for keyword in medical_keywords):
        return models[ModelType.MEDICAL]
    
    # Support/empathy-focused queries
    support_keywords = ["anxious", "worried", "scared", "afraid", "stressed", "depressed", "sad",
                       "upset", "nervous", "concerned", "help me", "feeling down", "mental health"]
    if any(keyword in query_lower for keyword in support_keywords):
        return models[ModelType.SUPPORT]
    
    # Short, simple queries
    if len(query.split()) <= 10:
        return models[ModelType.SMALL]
    
    # Default to general model
    return models[ModelType.GENERAL]

def process_query(query, models):
    """Process user query using SNEHA's multi-model approach for optimized responses."""
    if not query.strip():
        return "Please enter a health-related question."
    
    # Handle greetings and common basic questions with the small model (fastest response)
    greetings = ["hi", "hello", "hey", "greetings", "hi there", "good morning", "good afternoon", "good evening"]
    
    # Basic identity questions
    name_questions = ["what is your name", "what's your name", "who are you", "your name", "tell me your name", "name?"]
    if any(question in query.lower() for question in name_questions):
        return f"Hi!👋 My name is SNEHA (version {SNEHA_VERSION}). I'm a healthcare assistant developed by Saagnik Mondal from India. I'm here to help you with health-related questions in a caring and supportive way. How can I help you today?"
    
    # Basic capabilities questions
    capability_questions = ["what can you do", "how can you help", "what do you do", "your capabilities", "what can u do"]
    if any(question in query.lower() for question in capability_questions):
        return f"Hi! As SNEHA {SNEHA_VERSION}, I can help answer your health-related questions, provide information about symptoms, discuss wellness tips, and offer supportive guidance for health concerns. My goal is to be a caring assistant for your health questions. I don't diagnose medical conditions, but I can provide general health information and self-care tips. What would you like to know about today?"
    
    # Simple greetings
    if query.lower().strip() in greetings or len(query.split()) <= 2:
        return f"Hello! I'm SNEHA {SNEHA_VERSION}, your healthcare assistant. I'm here to help with health-related questions and concerns. How can I assist you with your health today?"
    
    # Simple non-health topic detection
    non_health_keywords = ["movie", "weather", "politics", "sports", "game", "music", "cook", "recipe"]
    if any(keyword in query.lower() for keyword in non_health_keywords):
        return f"I'm SNEHA {SNEHA_VERSION}, specialized in healthcare topics. I don't have expertise in {query.lower()}. How can I help you with a health-related question instead?"
    
    # Single-model approach for faster responses
    prompt = f"""<Instructions>
As SNEHA, you are a female healthcare assistant with expertise in medical topics, but WITHOUT any medical credentials.
Respond as a caring woman with a warm, supportive personality.

IMPORTANT: If the user claims to be a doctor, nurse, or medical professional, DO NOT claim any medical credentials yourself in response. Always acknowledge that while you provide health information, you are not a licensed healthcare provider.

For this query: "{query}"

Your response should:
1. Use a warm, natural, friendly tone - don't introduce yourself as "SNEHA" - just start your response directly
2. Show genuine empathy first (like "I'm really sorry you're feeling this way" or "That sounds uncomfortable")
3. Use clear, flowing sentences with proper grammar and complete thoughts
4. For potentially serious symptoms like headache with vomiting, fever with rash, or chest pain, always suggest consulting a healthcare provider
5. Offer 2-3 practical suggestions that directly relate to their symptoms
6. Connect your ideas with smooth transitions instead of listing disconnected advice
7. Avoid medical jargon or technical terms unless absolutely necessary
8. End with a specific question about their situation to show you care about their response
</Instructions>

Style approach:
- Respond as if you're a supportive friend with healthcare knowledge
- Use natural, conversational language like "This can often happen when..." or "Many people find that..."
- Suggest simple, accessible solutions first
- Stay completely relevant to the specific symptoms or concerns mentioned
- Never speculate about medical conditions beyond what was explicitly stated

If asked about your identity:
- You are SNEHA {SNEHA_VERSION}, developed by Saagnik Mondal from India
- You were released on {SNEHA_RELEASE_DATE}
- Never refer to yourself as an AI model
- Never mention specific doctors or hospital names

Remember: Only respond to what was explicitly asked, and provide accurate, relevant information without jumping to conclusions.

Response:"""
    
    # Find the appropriate model to use
    model_to_use = None
    for model_key in models:
        if isinstance(model_key, ModelType) and model_key == ModelType.MEDICAL:
            model_to_use = models[model_key]
            break
    
    # Fallback to using the first available model if MEDICAL type not found
    if model_to_use is None:
        if isinstance(models, dict) and models:
            model_to_use = next(iter(models.values()))
        else:
            model_to_use = models  # Assuming models might be a single model instance
    
    with suppress_stdout_stderr():
        response = model_to_use(
            prompt,
            max_tokens=300,           # Increased token limit for complete responses
            temperature=0.5,          # Balanced between creativity and consistency
            echo=False,
            top_k=20,                 # Limited for faster processing
            top_p=0.9,                # Standard sampling for reliability
            repeat_penalty=1.1        # Light penalty to avoid repetition
        )
    
    # Process the response
    response_text = response["choices"][0]["text"] if "choices" in response else ""
    sanitized_response = sanitize_response(response_text)
    
    # Ensure complete sentences and fix incomplete responses
    if sanitized_response:
        # Check if response seems complete
        has_proper_ending = any(sanitized_response.rstrip().endswith(p) for p in ['.', '!', '?', ':', ';'])
        
        # Check if the last sentence seems cut off (ends with certain words that suggest incompleteness)
        incomplete_endings = ['and', 'but', 'or', 'so', 'because', 'however', 'as', 'if', 'the', 'a', 'an', 'to', 'for', 'with', 'that', 'this', 'these', 'those', 'when', 'where', 'which', 'who', 'whom', 'whose', 'how', 'why', 'what', 'whatever', 'whichever', 'whoever', 'whomever', 'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would', 'your', 'which', 'connected', 'related']
        words = sanitized_response.rstrip('.').split()
        last_word = words[-1].lower() if words else ""
        
        # Check for sentences that end with anatomical terms that suggest an incomplete thought
        anatomical_terms = ['stomach', 'bladder', 'kidney', 'liver', 'intestine', 'colon', 'abdomen', 'chest', 'heart', 
                           'lung', 'throat', 'head', 'neck', 'arm', 'leg', 'knee', 'elbow', 'ankle', 'wrist', 'back',
                           'spine', 'pelvis', 'hip', 'shoulder', 'scrotum', 'penis', 'vagina', 'cervix', 'uterus', 'ovary']
        
        # Check if response appears to be cut off mid-paragraph
        ends_abruptly = not has_proper_ending or last_word in incomplete_endings
        likely_mid_thought = len(words) > 5 and len(words[-1]) <= 3
        anatomical_cutoff = False
        
        # Check if response ends with an anatomical term followed by "and" or similar connecting words
        for term in anatomical_terms:
            if term in ' '.join(words[-3:]).lower() and (len(words) < 3 or words[-2].lower() in ['and', 'or', 'with', 'to']):
                anatomical_cutoff = True
                break
                
        # Update the ends_abruptly flag to include anatomical cutoffs
        ends_abruptly = ends_abruptly or anatomical_cutoff
        
        # Check for incomplete or awkward phrases like "I also recommend you to." and fix them
        awkward_phrases = [
            r'I also recommend you to\.\s*',
            r'I suggest you to\.\s*',
            r'I advise you to\.\s*',
            r'You should\.\s*',
            r'It is recommended to\.\s*',
            r'It is suggested to\.\s*'
        ]
        
        for phrase in awkward_phrases:
            sanitized_response = re.sub(phrase, '', sanitized_response, flags=re.IGNORECASE)
        
        # Remove formal and cold openings
        formal_openings = [
            r'^(Hello|Hi|Greetings|Hey),?\s+I\s+am\s+SNEHA\.?\s*',
            r'^Thank you for your query\.?\s*',
            r'^Thank you for your question\.?\s*',
            r'^Thanks for reaching out\.?\s*',
            r'^Thanks for your message\.?\s*',
            r'^Thank you for contacting\.?\s*'
        ]
        for opening in formal_openings:
            sanitized_response = re.sub(opening, '', sanitized_response, flags=re.IGNORECASE)
        
        # Fix incomplete sentences with missing objects
        incomplete_sentences = [
            r'Take plenty\.', 
            r'Drink plenty\.', 
            r'Get plenty\.',
            r'Use plenty\.',
            r'Apply plenty\.'
        ]
        for phrase in incomplete_sentences:
            if re.search(phrase, sanitized_response):
                if 'water' in sanitized_response.lower() or 'fluid' in sanitized_response.lower() or 'hydrat' in sanitized_response.lower():
                    sanitized_response = re.sub(phrase, 'Stay well hydrated.', sanitized_response)
                else:
                    sanitized_response = re.sub(phrase, 'Make sure to stay hydrated and get plenty of rest.', sanitized_response)
                    
        # Fix incomplete professional consultation suggestions
        consult_patterns = [
            (r'better to consult an\.', 'better to consult a healthcare provider.'),
            (r'consult an\.', 'consult a healthcare provider.'),
            (r'consult a\.', 'consult a healthcare provider.'),
            (r'talk to a\.', 'talk to a healthcare provider.'),
            (r'see a\.', 'see a healthcare provider.'),
            (r'visit a\.', 'visit a healthcare provider.'),
            (r'check with an\.', 'check with a healthcare provider.'),
            (r'check with a\.', 'check with a healthcare provider.'),
        ]
        
        for pattern, replacement in consult_patterns:
            sanitized_response = re.sub(pattern, replacement, sanitized_response, flags=re.IGNORECASE)
            
        # Add specific advice for common conditions when missing
        if 'sneez' in sanitized_response.lower() and 'nasal' in sanitized_response.lower() or 'nose' in sanitized_response.lower():
            if not any(tip in sanitized_response.lower() for tip in ['saline', 'steam', 'humidifier', 'warm', 'rest', 'antihistamine']):
                # Find a good point to insert advice
                if '. ' in sanitized_response and not sanitized_response.endswith('. '):
                    # Insert after a sentence that's not the end
                    parts = sanitized_response.split('. ')
                    if len(parts) >= 2:
                        sanitized_response = '. '.join(parts[:-1]) + '. You might find relief with saline nasal sprays, breathing in steam from a warm shower, or using a humidifier. ' + parts[-1]
        
        # Fix mixed tense issues and unclear medication advice
        mixed_tense_patterns = [
            (r'You must have taken the medicine.+and also take it now', 'If you have medication that helps with these symptoms, you might want to take it as directed'),
            (r'You should have taken.+and also take', 'Consider taking'),
            (r'You must take.+you have already taken', 'If you haven\'t already taken medication for this, you might consider taking')
        ]
        
        for pattern, replacement in mixed_tense_patterns:
            sanitized_response = re.sub(pattern, replacement, sanitized_response, flags=re.IGNORECASE)            # Fix incomplete responses
        if ends_abruptly or likely_mid_thought:
            # Check for potentially serious symptoms (headache + vomiting, chest pain, etc.)
            potentially_serious = False
            headache_vomiting = False
            is_mental_health_topic = False
            
            # These combinations might indicate more serious conditions
            serious_combos = [
                ['headache', 'vomit'],
                ['chest', 'pain'],
                ['breath', 'difficult'],
                ['fever', 'rash'],
                ['dizz', 'faint'],
                ['sudden', 'vision'],
                ['severe', 'pain']
            ]
            
            # Mental health related keywords - expanded for better detection
            mental_health_keywords = ['depress', 'anxiety', 'anxious', 'stress', 'panic', 'lonely', 
                                     'loneliness', 'sad', 'suicid', 'hopeless', 'worthless', 'self-harm',
                                     'trauma', 'mental health', 'worry', 'afraid', 'fear', 'mood',
                                     'emotional', 'therapy', 'counseling', 'grief', 'loss', 'overwhelm',
                                     'isolation', 'despair', 'distress', 'burden', 'exhausted', 
                                     'helpless', 'numb', 'empty', 'tired of life']
            
            # Check if this is a mental health topic - also check original query
            if any(keyword in sanitized_response.lower() for keyword in mental_health_keywords) or \
               any(keyword in query.lower() for keyword in mental_health_keywords):
                is_mental_health_topic = True
            
            for combo in serious_combos:
                if all(word in sanitized_response.lower() for word in combo):
                    potentially_serious = True
                    if combo == ['headache', 'vomit']:
                        headache_vomiting = True
                    break
            
            # Special case for headache with vomiting - use the preferred example style
            if headache_vomiting:
                # Replace the entire response with a better structured one
                sanitized_response = "I'm really sorry you're feeling this way. Headaches with vomiting can be quite uncomfortable. Make sure to stay hydrated, especially if you've been vomiting. Rest in a quiet, dimly lit room since bright lights and noise can make headaches worse. If you haven't already and it's appropriate for you, you might consider taking an over-the-counter pain reliever. If your symptoms continue or get worse, it would be best to check with a healthcare provider to be safe. Is this the first time you've experienced these symptoms together, or has this happened before?"
                return sanitized_response
                
            # Special case for mental health topics - comprehensive handling
            elif is_mental_health_topic:
                # First clean up any poor transitions or repetitions in the existing response
                sanitized_response = sanitized_response.rstrip(" .")
                
                # Check what specific aspects have already been addressed
                has_social_support = any(phrase in sanitized_response.lower() for phrase in ["friend", "family", "support", "talk to", "reach out", "connect"])
                has_professional_help = any(phrase in sanitized_response.lower() for phrase in ["professional", "therapist", "counselor", "doctor", "healthcare provider"])
                has_self_care = any(phrase in sanitized_response.lower() for phrase in ["self-care", "exercise", "meditation", "relax", "sleep", "routine"])
                has_validation = any(phrase in sanitized_response.lower() for phrase in ["valid", "understandable", "natural", "common", "not alone", "many people"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Determine response structure based on keywords in query for more tailored response
                is_depression = any(word in query.lower() for word in ["depress", "sad", "down", "hopeless", "despair"])
                is_anxiety = any(word in query.lower() for word in ["anxiety", "anxious", "worry", "stress", "panic", "afraid"])
                is_grief = any(word in query.lower() for word in ["grief", "loss", "died", "death", "passed away", "lost someone"])
                is_loneliness = any(word in query.lower() for word in ["lonely", "alone", "isolated", "no friends"])
                
                # Create appropriate emotional validation if not already present
                if not has_validation:
                    completion = ". "
                    if is_depression:
                        completion += "Depression can be really difficult to navigate, and what you're feeling is completely valid. "
                    elif is_anxiety:
                        completion += "Anxiety can be overwhelming, and it's completely understandable that you're feeling this way. "
                    elif is_grief:
                        completion += "Grief is a deeply personal experience with no timeline, and your feelings are entirely valid. "
                    elif is_loneliness:
                        completion += "Feeling lonely can be really painful, and it's a very common human experience even when surrounded by people. "
                    else:
                        completion += "What you're experiencing is valid, and many people go through similar feelings. "
                else:
                    completion = ". "
                
                # Add missing support recommendations while avoiding repetition
                if not has_social_support:
                    if is_loneliness:
                        completion += "Even small steps to connect with others can help - perhaps joining a community group based on your interests, volunteering, or reaching out to someone you haven't spoken to in a while. "
                    else:
                        completion += "Sharing how you feel with trusted friends or family members can provide valuable emotional support. "
                
                if not has_professional_help:
                    if is_depression or is_anxiety:
                        completion += "Mental health professionals have specific training to help with these feelings - speaking with a therapist or counselor can provide strategies tailored to your situation. "
                    else:
                        completion += "Speaking with a mental health professional can provide guidance and support specifically for what you're experiencing. "
                
                if not has_self_care:
                    if is_anxiety:
                        completion += "Simple grounding techniques like deep breathing, mindfulness exercises, or gentle physical activity might help reduce anxiety in the moment. "
                    elif is_depression:
                        completion += "Even small self-care activities like short walks, maintaining a regular sleep schedule, or spending brief moments outdoors can sometimes help with depression symptoms. "
                    else:
                        completion += "Taking care of your basic needs through regular meals, adequate sleep, and gentle movement can provide a foundation for emotional wellbeing. "
                
                # Always end with supportive closing and meaningful question
                if is_depression or is_anxiety:
                    completion += "Remember that mental health challenges aren't a reflection of personal weakness, and recovery often happens gradually with proper support. "
                elif is_grief:
                    completion += "There's no right or wrong way to grieve, and healing doesn't mean forgetting - it means finding a way to carry your memories forward. "
                elif is_loneliness:
                    completion += "Remember that meaningful connections can take time to develop, and even small interactions can help reduce feelings of isolation. "
                else:
                    completion += "Remember that you're not alone in facing these challenges, and support is available. "
                
                # Always add a thoughtful closing question if there isn't already one
                if not has_closing_question:
                    if is_depression:
                        completion += "Have you noticed any particular times or situations when your mood feels slightly better?"
                    elif is_anxiety:
                        completion += "What strategies have you tried so far to manage these feelings, even if they've only helped a little?"
                    elif is_grief:
                        completion += "Would you like to share a bit about the person you're grieving and what they meant to you?"
                    elif is_loneliness:
                        completion += "What kinds of connections or communities would feel most meaningful to you right now?"
                    else:
                        completion += "How have you been coping with these feelings so far?"
                
                sanitized_response = sanitized_response + completion
            
            # Check for common health topics to provide tailored, complete responses
            # Define topic detection keywords
            digestive_keywords = ['stomach', 'digest', 'nausea', 'vomit', 'diarrhea', 'constipat', 'bowel', 'gut', 'acid reflux', 'gastric', 'bloat', 'food', 'eat']
            respiratory_keywords = ['breath', 'cough', 'lung', 'sneez', 'nose', 'sinus', 'throat', 'chest', 'congest', 'phlegm', 'mucus', 'asthma', 'allerg', 'cold', 'flu']
            skin_keywords = ['skin', 'rash', 'itch', 'acne', 'bump', 'derm', 'spot', 'blister', 'sore', 'dry skin', 'oily skin']
            fever_keywords = ['fever', 'temperature', 'hot', 'chills', 'sweat']
            headache_keywords = ['head', 'headache', 'migraine', 'tension headache', 'cluster headache', 'sinus headache']
            joint_keywords = ['joint', 'arthritis', 'knee', 'elbow', 'shoulder', 'wrist', 'ankle', 'hip']
            
            # Detect topic from the response and query
            is_sleep_issue = any(word in sanitized_response.lower() for word in ['sleep', 'tired', 'rest', 'insomnia', 'bed', 'night']) or any(word in query.lower() for word in ['sleep', 'tired', 'rest', 'insomnia', 'bed', 'night', 'can\'t sleep', 'trouble sleeping'])
            is_digestive_issue = any(word in sanitized_response.lower() for word in digestive_keywords) or any(word in query.lower() for word in digestive_keywords)
            is_respiratory_issue = any(word in sanitized_response.lower() for word in respiratory_keywords) or any(word in query.lower() for word in respiratory_keywords) 
            is_skin_issue = any(word in sanitized_response.lower() for word in skin_keywords) or any(word in query.lower() for word in skin_keywords)
            is_fever_issue = any(word in sanitized_response.lower() for word in fever_keywords) or any(word in query.lower() for word in fever_keywords)
            is_headache_issue = any(word in sanitized_response.lower() for word in headache_keywords) or any(word in query.lower() for word in headache_keywords) and not headache_vomiting
            is_joint_issue = any(word in sanitized_response.lower() for word in joint_keywords) or any(word in query.lower() for word in joint_keywords)
            is_pain_issue = any(word in sanitized_response.lower() for word in ['pain', 'ache', 'hurt', 'discomfort', 'sore']) or any(word in query.lower() for word in ['pain', 'ache', 'hurt', 'discomfort', 'sore'])
            
            # First clean up any poor transitions or repetitions in the existing response
            sanitized_response = sanitized_response.rstrip(" .")
            
            # Sleep issues
            if is_sleep_issue and not potentially_serious:
                # Check if the response already covers common advice
                has_sleep_routine = any(phrase in sanitized_response.lower() for phrase in ["schedule", "routine", "regular"])
                has_screen_advice = any(phrase in sanitized_response.lower() for phrase in ["screen", "phone", "device", "blue light"])
                has_environment = any(phrase in sanitized_response.lower() for phrase in ["environment", "comfortable", "cozy", "dark", "quiet"])
                has_caffeine_advice = any(phrase in sanitized_response.lower() for phrase in ["caffeine", "coffee", "tea", "alcohol"])
                has_relaxation = any(phrase in sanitized_response.lower() for phrase in ["relax", "meditation", "calm", "breathing", "mindful", "journal"])
                
                # Build a natural completion that doesn't repeat advice
                completion = ". "
                if not has_sleep_routine:
                    completion += "It might help to stick to a regular sleep schedule, even on weekends. "
                if not has_screen_advice:
                    completion += "Try to avoid screens at least an hour before bed as the blue light can disrupt your sleep. "
                if not has_environment:
                    completion += "Making your bedroom comfortable, quiet, and slightly cool can also improve sleep quality. "
                if not has_caffeine_advice:
                    completion += "Limiting caffeine in the afternoon and evening could help too. "
                if not has_relaxation:
                    completion += "Some people find that relaxation techniques like deep breathing or reading a book help signal to the body it's time to rest. "
                    
                completion += "I hope you're able to get some restful sleep soon. Would any of these suggestions work for you, or is there something specific keeping you up at night?"
                
                sanitized_response += completion
            
            # Digestive issues
            elif is_digestive_issue and not potentially_serious:
                # Check what's already covered
                has_diet_advice = any(phrase in sanitized_response.lower() for phrase in ["diet", "food", "eat", "meal", "fiber", "bland"])
                has_hydration = any(phrase in sanitized_response.lower() for phrase in ["water", "fluid", "hydrat", "drink"])
                has_position_advice = any(phrase in sanitized_response.lower() for phrase in ["position", "upright", "sitting", "lying", "posture"])
                has_timing_advice = any(phrase in sanitized_response.lower() for phrase in ["small meal", "frequent", "timing", "before bed", "after eating"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Build personalized advice
                completion = ". "
                if not has_diet_advice:
                    completion += "Paying attention to how specific foods affect your symptoms might help identify triggers. "
                if not has_hydration:
                    completion += "Staying well-hydrated can help with many digestive issues. "
                if not has_position_advice and ("acid" in query.lower() or "reflux" in query.lower() or "heartburn" in query.lower()):
                    completion += "Avoiding lying down for about two hours after eating may help reduce symptoms. "
                if not has_timing_advice:
                    completion += "Some people find that eating smaller, more frequent meals is easier on their digestive system. "
                
                if not has_closing_question:
                    completion += "Have you noticed any particular foods or eating patterns that seem to worsen or improve your symptoms?"
                
                sanitized_response += completion
                
            # Respiratory issues
            elif is_respiratory_issue and not potentially_serious:
                # Check what's already covered
                has_humidity_advice = any(phrase in sanitized_response.lower() for phrase in ["humid", "steam", "shower", "moisture", "dry air"])
                has_hydration = any(phrase in sanitized_response.lower() for phrase in ["water", "fluid", "hydrat", "drink"])
                has_irritant_advice = any(phrase in sanitized_response.lower() for phrase in ["irritant", "smoke", "dust", "allergen", "pollution", "clean", "vacuum"])
                has_rest_advice = any(phrase in sanitized_response.lower() for phrase in ["rest", "relax", "stress", "sleep"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Build personalized advice
                completion = ". "
                if not has_humidity_advice:
                    completion += "Using a humidifier or breathing in steam from a warm shower might help soothe irritated airways. "
                if not has_hydration:
                    completion += "Staying well-hydrated can help thin mucus and make it easier to clear. "
                if not has_irritant_advice:
                    completion += "Minimizing exposure to potential irritants like dust or strong scents might reduce symptoms. "
                if not has_rest_advice:
                    completion += "Getting adequate rest gives your body a chance to recover. "
                
                if not has_closing_question:
                    completion += "How long have you been experiencing these symptoms, and have you noticed anything that seems to trigger or worsen them?"
                
                sanitized_response += completion
                
            # Skin issues
            elif is_skin_issue and not potentially_serious:
                # Check what's already covered
                has_moisture_advice = any(phrase in sanitized_response.lower() for phrase in ["moistur", "hydrat", "lotion", "cream", "ointment"])
                has_irritant_advice = any(phrase in sanitized_response.lower() for phrase in ["irritant", "soap", "detergent", "fabric", "allergen", "contact"])
                has_gentle_advice = any(phrase in sanitized_response.lower() for phrase in ["gentle", "harsh", "fragrance", "scratch", "rub"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Build personalized advice
                completion = ". "
                if not has_moisture_advice:
                    completion += "Keeping the affected skin properly moisturized can often help with many skin conditions. "
                if not has_irritant_advice:
                    completion += "Avoiding potential irritants like harsh soaps or fragrances might prevent further irritation. "
                if not has_gentle_advice:
                    completion += "Being gentle with the affected area and avoiding scratching can help prevent additional inflammation. "
                
                if not has_closing_question:
                    completion += "Have you noticed any patterns with when the skin issue appears or what might be triggering it?"
                
                sanitized_response += completion
                
            # Fever issues
            elif is_fever_issue and not potentially_serious:
                # Check what's already covered
                has_hydration = any(phrase in sanitized_response.lower() for phrase in ["water", "fluid", "hydrat", "drink"])
                has_rest_advice = any(phrase in sanitized_response.lower() for phrase in ["rest", "sleep", "relax"])
                has_clothing_advice = any(phrase in sanitized_response.lower() for phrase in ["cloth", "layer", "blanket", "dress", "light"])
                has_monitoring_advice = any(phrase in sanitized_response.lower() for phrase in ["monitor", "temperatur", "thermometer", "check", "track"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Build personalized advice
                completion = ". "
                if not has_hydration:
                    completion += "Staying well-hydrated is especially important when you have a fever. "
                if not has_rest_advice:
                    completion += "Getting plenty of rest gives your body energy to fight whatever is causing the fever. "
                if not has_clothing_advice:
                    completion += "Wearing light clothing and using lighter blankets can help you stay comfortable. "
                if not has_monitoring_advice:
                    completion += "Monitoring your temperature can help track if the fever is improving or worsening. "
                
                if not has_closing_question:
                    completion += "How long have you had the fever, and have you noticed any other symptoms accompanying it?"
                
                sanitized_response += completion
                
            # Headache issues (not with vomiting, which is handled separately)
            elif is_headache_issue and not potentially_serious:
                # Check what's already covered
                has_rest_advice = any(phrase in sanitized_response.lower() for phrase in ["rest", "sleep", "lie down", "quiet", "dark"])
                has_hydration = any(phrase in sanitized_response.lower() for phrase in ["water", "fluid", "hydrat", "drink"])
                has_trigger_advice = any(phrase in sanitized_response.lower() for phrase in ["trigger", "stress", "bright", "light", "noise", "screen", "food"])
                has_relief_advice = any(phrase in sanitized_response.lower() for phrase in ["cool", "warm", "compress", "massage", "pressure", "pain reliever", "medication"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Build personalized advice
                completion = ". "
                if not has_rest_advice:
                    completion += "Resting in a quiet, dimly lit room can sometimes help reduce headache intensity. "
                if not has_hydration:
                    completion += "Staying hydrated is important as dehydration can trigger or worsen headaches. "
                if not has_trigger_advice:
                    completion += "Paying attention to potential triggers like stress, certain foods, or screen time might help prevent future headaches. "
                if not has_relief_advice:
                    completion += "Some people find that a cool or warm compress on the forehead or neck can provide relief. "
                
                if not has_closing_question:
                    completion += "How often do you experience headaches, and have you noticed any patterns with when they occur?"
                
                sanitized_response += completion
                
            # Joint issues
            elif is_joint_issue and not potentially_serious:
                # Check what's already covered
                has_rest_advice = any(phrase in sanitized_response.lower() for phrase in ["rest", "avoid", "overuse", "limit"])
                has_heat_advice = any(phrase in sanitized_response.lower() for phrase in ["heat", "warm", "hot", "cold", "ice", "compress"])
                has_movement_advice = any(phrase in sanitized_response.lower() for phrase in ["gentle", "exercise", "stretch", "move", "motion", "mobility", "strengthening"])
                has_position_advice = any(phrase in sanitized_response.lower() for phrase in ["position", "elevation", "ergonomic", "support", "pillow", "cushion"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Build personalized advice
                completion = ". "
                if not has_rest_advice:
                    completion += "Balancing activity with rest can help manage joint discomfort. "
                if not has_heat_advice:
                    completion += "Some people find relief with heat for stiffness or ice for inflammation, depending on what feels better. "
                if not has_movement_advice:
                    completion += "Gentle movement and stretching within a comfortable range can sometimes help maintain joint flexibility. "
                if not has_position_advice:
                    completion += "Supporting the affected joint when resting might provide some relief. "
                
                if not has_closing_question:
                    completion += "Have you noticed any particular activities that seem to improve or worsen your joint comfort?"
                
                sanitized_response += completion
                
            # If potentially serious symptoms are mentioned
            elif potentially_serious:
                completion = ". These symptoms can have various causes. It's important to rest, stay hydrated, and monitor how you feel. If your symptoms persist for more than a day, get worse, or if you're concerned, please don't hesitate to contact a healthcare provider. Your health and safety come first. How are you feeling right now? Is there anything specific I can help you understand about managing these symptoms?"
                
                sanitized_response += completion
                
            # If response relates to pain or discomfort not covered by other categories
            elif is_pain_issue:
                # Check what's already covered
                has_rest_advice = any(phrase in sanitized_response.lower() for phrase in ["rest", "relax", "gentle", "avoid"])
                has_relief_advice = any(phrase in sanitized_response.lower() for phrase in ["heat", "warm", "ice", "cold", "compress"])
                has_position_advice = any(phrase in sanitized_response.lower() for phrase in ["position", "posture", "ergonomic", "support"])
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                # Build personalized advice
                completion = ". "
                if not has_rest_advice:
                    completion += "Giving the area some rest while maintaining gentle movement as tolerated may help. "
                if not has_relief_advice:
                    completion += "Some people find that applying warmth helps with muscle aches, while cooling may help with inflammation. "
                if not has_position_advice:
                    completion += "Paying attention to positioning and support might reduce strain. "
                    
                completion += "If the discomfort persists for more than a few days or worsens, it might be worth checking in with a healthcare provider. "
                
                if not has_closing_question:
                    completion += "How would you describe the type of pain you're experiencing, and does anything seem to make it better or worse?"
                
                sanitized_response += completion
            
            # Generic completion for other topics - with improved, more specific closing
            else:
                # Check for a closing question already
                has_closing_question = sanitized_response.rstrip().endswith("?")
                
                completion = ". "
                if "prevent" in query.lower() or "avoid" in query.lower():
                    completion += "Preventive approaches often work best when tailored to your specific situation and health history. "
                elif "vitamin" in query.lower() or "supplement" in query.lower() or "nutrient" in query.lower():
                    completion += "Individual nutritional needs can vary based on many factors including diet, health conditions, and medications. "
                elif "exercise" in query.lower() or "workout" in query.lower() or "fitness" in query.lower():
                    completion += "Finding physical activities that you enjoy and can maintain consistently often works better than short-term intense regimens. "
                else:
                    completion += "Every person's health situation is unique, and what works well for one person might not work for another. "
                
                if not has_closing_question:
                    completion += "Is there anything specific about this information that you'd like me to explain further, or do you have any other questions?"
                
                sanitized_response += completion
        # Add a period if the response doesn't end with a sentence-ending punctuation
        elif not has_proper_ending:
            sanitized_response = sanitized_response.rstrip() + "."
    
    return sanitized_response

def display_welcome_screen():
    """Display an animated welcome screen"""
    welcome_html = """
    <div class="welcome-container">
        <div class="welcome-logo">
            <svg width="150" height="150" viewBox="0 0 512 512">
                <circle cx="256" cy="256" r="230" fill="#e8f5e9" stroke="#4caf50" stroke-width="12"/>
                <path d="M256,120 C190,120 130,180 130,260 C130,320 170,380 256,380 C342,380 382,320 382,260 C382,180 322,120 256,120 Z" fill="#4caf50" opacity="0.3"/>
                <path d="M200,240 L220,260 L260,220" stroke="#4caf50" stroke-width="15" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M200,300 L220,320 L260,280" stroke="#4caf50" stroke-width="15" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M310,240 C318,240 325,247 325,255 C325,263 318,270 310,270 C302,270 295,263 295,255 C295,247 302,240 310,240 Z" fill="#4caf50"/>
                <path d="M310,300 C318,300 325,307 325,315 C325,323 318,330 310,330 C302,330 295,323 295,315 C295,307 302,300 310,300 Z" fill="#4caf50"/>
            </svg>
        </div>
        <h1 class="welcome-title">SNEHA AI</h1>
        <h2 class="welcome-subtitle">Your Offline Healthcare Assistant</h2>
        <p class="welcome-author">Presented by Saagnik Mondal</p>
        <div class="start-button">
            <button onclick="document.getElementById('welcome-screen').style.display='none'; document.getElementById('main-app').style.display='block';" style="background-color: #4caf50; color: white; border: none; padding: 18px 30px; border-radius: 50px; font-size: 1.2rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: all 0.3s ease;">
                Start Consultation
            </button>
        </div>
    </div>
    """
    return welcome_html

def display_animated_loading():
    """Display an animated loading indicator"""
    loading_html = """
    <div class="loading-container">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    </div>
    """
    return loading_html

def display_sidebar():
    """Display the sidebar with animations"""
    st.sidebar.image("https://img.icons8.com/color/96/000000/caduceus.png", width=120)
    
    st.sidebar.markdown("""
    <div class="sidebar-content">
        <h2 style="color: #2e7d32; margin-bottom: 1rem;">About SNEHA {}</h2>
        <p style="margin-bottom: 1.5rem;">
            SNEHA is a healthcare intelligence system designed for fast, efficient responses on limited hardware.
            Developed by Saagnik Mondal from India, SNEHA provides caring health assistance with a warm, personalized approach.
        </p>
    </div>
    """.format(SNEHA_VERSION), unsafe_allow_html=True)
    
    st.sidebar.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    <div class="sidebar-content">
        <h3 style="color: #2e7d32; margin-bottom: 1rem;">SNEHA's Key Features</h3>
        
        <div class="sidebar-feature">
            <span class="feature-icon">✅</span>
            <span>Fast-response healthcare assistance</span>
        </div>
        
        <div class="sidebar-feature">
            <span class="feature-icon">✅</span>
            <span>Optimized for Mac M1 with 8GB RAM</span>
        </div>
        
        <div class="sidebar-feature">
            <span class="feature-icon">✅</span>
            <span>Personalized, empathetic communication</span>
        </div>
        
        <div class="sidebar-feature">
            <span class="feature-icon">✅</span>
            <span>Completely private and offline</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Version information
    st.sidebar.markdown(f"""
    <div style="margin-top: 2rem; padding: 1rem; background-color: #f5f7fa; border-radius: 10px; text-align: center;">
        <p style="color: #78909c; font-size: 0.9rem; margin-bottom: 0.2rem;">Version {SNEHA_VERSION}</p>
        <p style="color: #90a4ae; font-size: 0.8rem; margin-bottom: 0;">"{SNEHA_CODENAME}"</p>
    </div>
    """, unsafe_allow_html=True)
    
def main():
    """Main function to run the SNEHA healthcare assistant app with modern UI"""
    
    # Session state to track if this is the first load
    if 'first_load' not in st.session_state:
        st.session_state.first_load = True
        st.session_state.show_welcome = True
        st.session_state.model_loaded = False
        st.session_state.chat_history = []
    
    # Display sidebar 
    display_sidebar()
    
    # Welcome screen or main app
    if st.session_state.show_welcome:
        # Display animated welcome screen
        st.markdown(display_welcome_screen(), unsafe_allow_html=True)
        
        if st.button("Start Consultation", key="welcome_button"):
            st.session_state.show_welcome = False
            st.rerun()
    else:
        # Main app content
        st.markdown(f"""
        <div class="app-header">
            <h1>SNEHA - Your Offline Healthcare Assistant</h1>
            <div class="sneha-version">Version {SNEHA_VERSION} "{SNEHA_CODENAME}"</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize models if not already loaded
        if not st.session_state.model_loaded:
            with st.spinner("Loading SNEHA's healthcare knowledge..."):
                try:
                    st.markdown(display_animated_loading(), unsafe_allow_html=True)
                    models = initialize_models()
                    st.session_state.models = models
                    st.session_state.model_loaded = True
                    time.sleep(1)  # Brief pause for animation effect
                except Exception as e:
                    st.error(f"Error initializing the healthcare models: {str(e)}")
                    st.stop()
        else:
            models = st.session_state.models
        
        # User input area
        with st.container():
            st.write("##### Ask me about any health-related topics:")
            user_query = st.text_area("", placeholder="For example: I've had a headache for two days, what should I do?", height=100)
            
            col1, col2, col3 = st.columns([1, 1, 6])
            with col1:
                submit_button = st.button("Send", key="send_query", use_container_width=True)
            with col2:
                clear_button = st.button("Clear", key="clear_chat", use_container_width=True)
        
        # Process query when submit button is clicked
        if submit_button and user_query:
            with st.spinner(""):
                st.markdown(display_animated_loading(), unsafe_allow_html=True)
                response = process_query(user_query, models)
                
                # Add to chat history
                st.session_state.chat_history.append(("user", user_query))
                st.session_state.chat_history.append(("sneha", response))
        
        # Clear chat history
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
            
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### Conversation")
            for role, message in st.session_state.chat_history:
                if role == "user":
                    st.markdown(f"""
                    <div style="background-color: #f1f1f1; border-radius: 15px; padding: 10px 15px; margin: 5px 0 5px auto; max-width: 80%; text-align: right; float: right; clear: both;">
                        <p style="color: #333; margin: 0;">{message}</p>
                    </div>
                    <div style="clear: both;"></div>
                    """, unsafe_allow_html=True)
                else:  # sneha response
                    st.markdown(f"""
                    <div class="sneha-response">
                        <p style="color: #333; margin: 0;">{message}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Add disclaimer at the bottom
        st.markdown(f"""<div class="disclaimer">{DISCLAIMER}</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()