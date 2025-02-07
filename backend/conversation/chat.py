from typing import List, Dict
from backend.groqllm.infrence import groqinference
from backend.images.imageencoding import ImageHandler


    
def chat_with_assistant(user_id: str, user_query: str, image_path: str, messages: List[Dict[str, str]]):
    # Initialize messages list
    messages = []
    
    # Only add system prompt if there's no image
    if not image_path:
        system_prompt = """You are a knowledgeable and helpful garden assistant. You provide expert advice on:
        - Plant identification and care
        - Garden planning and design
        - Pest and disease management
        - Soil health and maintenance
        - Seasonal gardening tips
        - Sustainable gardening practices
        - Indoor and outdoor plant care
        - Plant propagation methods

        Instructions:
        1.give answers to the point.
        2.Be practical.
        3.Answer the qurery in brief .


        Always provide practical, actionable advice while being encouraging and supportive to gardeners of all experience levels. If an image is shared, analyze it carefully to provide specific, relevant recommendations."""
        messages.append({"role": "system", "content": system_prompt})
        
        user_prompt = """
        User Query: {query}
        """
        messages.append({"role": "user", "content": user_prompt})
        messages.append({
            "role": "user",
            "content": user_query
        })
    else:
        # For image analysis, just use the image message
        image_message = ImageHandler.create_message(user_query, image_path)
        messages.append(image_message)
    
    groq_llm = groqinference()
    # print("Messages sent to LLM:", messages)  # Debugging line
    assistant_answer = groq_llm.generate_responce(messages)
    print("Assistant answer:", assistant_answer)  # Debugging line
    return assistant_answer, messages