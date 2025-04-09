from mindee import Client, product, AsyncPredictResponse
from label import *
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_label_details():
    try:
        # Get API key from environment variable
        api_key = os.environ.get("MINDEE_API_KEY", "")
        if not api_key:
            print("Error: MINDEE_API_KEY environment variable not set")
            return None
            
        # Init a new client
        mindee_client = Client(api_key=api_key)
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join("static", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Check if package.jpg exists
        file_path = os.path.join("static", "uploads", "package.jpg")
        if not os.path.exists(file_path):
            print("Error: package.jpg not found")
            return None
            
        # Load a file from disk
        input_doc = mindee_client.source_from_path(file_path)

        # Load a file from disk and enqueue it.
        result: AsyncPredictResponse = mindee_client.enqueue_and_parse(
            product.us.UsMailV2,
            input_doc,
        )
        return json_to_label(result)
    except Exception as e:
        print(f"Error in generate_label_details: {str(e)}")
        return None

# Print a brief summary of the parsed data
# print(result.document)