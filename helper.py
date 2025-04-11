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

        try:
            # Load a file from disk and enqueue it.
            result = mindee_client.enqueue_and_parse(
                product.us.UsMailV2,
                input_doc,
            )
        except Exception as api_error:
            error_message = str(api_error)
            if "403" in error_message and "maximum number of requests" in error_message:
                print("Error: Mindee API rate limit exceeded. Please upgrade your plan or try again later.")
            elif "401" in error_message:
                print("Error: Invalid Mindee API key. Please check your API key.")
            else:
                print(f"Mindee API error: {error_message}")
            return None
        
        # Debug: inspect what's available in the result
        print(f"Result type: {type(result)}")
        print(f"Result attributes: {dir(result)}")
        
        # Create a Label object with default empty values
        label = Label(
            recipient_name="",
            recipient_address="",
            sender_name=""
        )
        
        # Try to safely extract data from result
        try:
            if hasattr(result, 'document'):
                doc = result.document
                print(f"Document type: {type(doc)}")
                print(f"Document attributes: {dir(doc)}")
                
                if hasattr(doc, 'inference') and hasattr(doc.inference, 'prediction'):
                    pred = doc.inference.prediction
                    
                    # Extract recipient name - check for sender name if recipient name isn't available
                    if hasattr(pred, 'recipient_names') and pred.recipient_names:
                        label.recipient_name = pred.recipient_names[0].value
                    elif hasattr(pred, 'sender_name') and pred.sender_name:
                        label.recipient_name = pred.sender_name.value  # Use sender name as fallback
                    
                    # Extract recipient address - check for sender address if recipient address isn't available
                    if hasattr(pred, 'recipient_addresses') and pred.recipient_addresses:
                        label.recipient_address = pred.recipient_addresses[0].complete
                    elif hasattr(pred, 'sender_address') and pred.sender_address:
                        label.recipient_address = pred.sender_address.complete  # Use sender address as fallback
                        
                    # Extract sender name
                    if hasattr(pred, 'sender_name') and pred.sender_name:
                        label.sender_name = pred.sender_name.value
        except Exception as extract_error:
            print(f"Error extracting data from response: {str(extract_error)}")
        
        return label
    except Exception as e:
        print(f"Error in generate_label_details: {str(e)}")
        return None

# Print a brief summary of the parsed data
# print(result.document)