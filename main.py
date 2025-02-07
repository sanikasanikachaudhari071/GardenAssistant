from backend.conversation.chat import chat_with_assistant

if __name__ == "__main__":
    user_id = input("Enter your user ID (or type 'exit' to quit): ")
    while True:
        # user_id = input("Enter your user ID (or type 'exit' to quit): ")
        # if user_id.lower() == 'exit':
        #     break  # Exit the loop if the user types 'exit'
        
        user_query = input("Enter your query (or leave blank if not applicable): ")
        
        # Ask if the user wants to add an image
        add_image = input("Do you want to add an image? (yes/no): ").strip().lower()
        image_url = ""
        
        if add_image == 'yes':
            image_url = input("Enter the image URL (e.g., http://127.0.0.1:5000/images/download.jpg): ")
        
        # Call the chat_with_assistant function
        assistant_response, messages = chat_with_assistant(user_id, user_query, image_url, [])
        
        # Print the assistant's response
        print("Assistant's response:", assistant_response)   