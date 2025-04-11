from typing import List, Dict
from backend.groqllm.infrence import groqinference
from backend.images.imageencoding import ImageHandler
from backend.memory.retrivedata import query_chroma

groq_llm = groqinference()

# Store conversation history
conversation_history = {}

def get_or_create_conversation(user_id: str) -> List[Dict[str, str]]:
    """Get existing conversation or create new one for user"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]

def chat_with_assistant(user_id: str, user_query: str, image_path: str = None) -> str:
    """
    Chat with the garden assistant.
    
    Args:
        user_id: Unique identifier for the user
        user_query: The user's question
        image_path: Optional path to an image
        
    Returns:
        The assistant's response
    """
    # Get or create conversation history
    messages = get_or_create_conversation(user_id)
    documents = ""  # Initialize documents variable
    
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
    0. STRICTLY ONLY answer from the provided knowledge base documents. DO NOT use any external knowledge.
    1. If the answer cannot be found in the provided documents, respond with: "I don't have enough information in my knowledge base to answer this question."
    2. Give answers to the point.
    3. Be practical.
    4. Answer the query in brief.

    Always provide practical, actionable advice while being encouraging and supportive to gardeners of all experience levels."""
    
    # Add knowledge source from ChromaDB for both text and image queries
    documents = query_chroma(
        user_query, collection_name="garden", n_results=3
    )
    print("\n📚 Knowledge Source:", documents)
    
    # Check if we have relevant documents
    if not documents or documents.strip() == "":
        print("\n⚠️ Warning: No relevant documents found in knowledge base")
        return "I don't have enough information in my knowledge base to answer this question."
    
    if image_path:
        # For image analysis, create a new message list without system message
        image_message = ImageHandler.create_message(user_query, image_path)
        current_messages = [image_message]  # Start with image message
        
        # Add context from previous messages if available
        if messages and len(messages) > 1:  # Skip system message
            current_messages.extend(messages[1:])  # Add all messages except system message
        
        user_prompt = f"""
        User Query: {user_query}
        
        RELEVANT DOCUMENTS:
        {documents}
        
        IMPORTANT: 
        1. First identify the plant in the image.
        2. Then provide care information based on the documents.
        3. Only use information from the above documents to answer the query.
        4. If the answer cannot be found in these documents, say "I don't have enough information in my knowledge base to answer this question."
        """
        current_messages.append({"role": "user", "content": user_prompt})
        
        # Generate response for image query
        assistant_answer = groq_llm.generate_responce(current_messages)
        
        # Add the image query and response to the conversation history
        messages.append({"role": "user", "content": user_query})
        messages.append({"role": "assistant", "content": assistant_answer})
    else:
        # For text-only queries, include system message if this is the first message
        if not messages:
            messages.append({"role": "system", "content": system_prompt})
        
        # If this is a follow-up question about a previously identified plant
        if len(messages) > 2 and "identified" in messages[-2]["content"].lower():
            # Extract plant name from previous identification
            plant_name = None
            for msg in reversed(messages):
                if "identified" in msg["content"].lower():
                    # Look for plant name after "identified as a" or similar phrases
                    content = msg["content"].lower()
                    if "identified as a" in content:
                        plant_name = content.split("identified as a")[1].split()[0]
                    elif "identified as" in content:
                        plant_name = content.split("identified as")[1].split()[0]
                    if plant_name:
                        break
            
            if plant_name:
                # Add context about the identified plant
                user_prompt = f"""
                Previous Context: We were discussing a {plant_name} plant.
                Current Query: {user_query}
                
                RELEVANT DOCUMENTS:
                {documents}
                
                IMPORTANT: Only use information from the above documents to answer the query. If the answer cannot be found in these documents, say "I don't have enough information in my knowledge base to answer this question."
                """
            else:
                user_prompt = f"""
                User Query: {user_query}
                
                RELEVANT DOCUMENTS:
                {documents}
                
                IMPORTANT: Only use information from the above documents to answer the query. If the answer cannot be found in these documents, say "I don't have enough information in my knowledge base to answer this question."
                """
        else:
            user_prompt = f"""
            User Query: {user_query}
            
            RELEVANT DOCUMENTS:
            {documents}
            
            IMPORTANT: Only use information from the above documents to answer the query. If the answer cannot be found in these documents, say "I don't have enough information in my knowledge base to answer this question."
            """
        
        messages.append({"role": "user", "content": user_prompt})
        
        # Generate response for text query
        assistant_answer = groq_llm.generate_responce(messages)
        
        # Add assistant's response to conversation history
        messages.append({"role": "assistant", "content": assistant_answer})
    
    # Validate if the answer contains information from the knowledge base
    if not any(doc in assistant_answer for doc in documents.split("\n")):
        print("\n⚠️ Warning: Assistant's response may not be based on knowledge base")
        return "I don't have enough information in my knowledge base to answer this question."
    
    print("\nAssistant answer:", assistant_answer)
    return assistant_answer

