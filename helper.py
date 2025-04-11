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
            
        print(f"Starting OCR processing for image: {file_path}")
            
        # Load a file from disk
        input_doc = mindee_client.source_from_path(file_path)

        try:
            # Load a file from disk and enqueue it.
            print("Sending request to Mindee API...")
            result = mindee_client.enqueue_and_parse(
                product.us.UsMailV2,
                input_doc,
            )
            print("Received response from Mindee API")
        except Exception as api_error:
            error_message = str(api_error)
            if "403" in error_message and "maximum number of requests" in error_message:
                print("Error: Mindee API rate limit exceeded. Please upgrade your plan or try again later.")
            elif "401" in error_message:
                print("Error: Invalid Mindee API key. Please check your API key.")
            else:
                print(f"Mindee API error: {error_message}")
            return None
        
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
                print("Successfully extracted document from result")
                
                if hasattr(doc, 'inference') and hasattr(doc.inference, 'prediction'):
                    pred = doc.inference.prediction
                    print("Found prediction in document inference")
                    
                    # Extract recipient name
                    if hasattr(pred, 'recipient_names') and pred.recipient_names:
                        label.recipient_name = pred.recipient_names[0].value
                        print(f"Found recipient name: {label.recipient_name}")
                    else:
                        print("No recipient name found in OCR result")
                        
                    # Extract recipient address
                    if hasattr(pred, 'recipient_addresses') and pred.recipient_addresses:
                        label.recipient_address = pred.recipient_addresses[0].complete
                        print(f"Found recipient address: {label.recipient_address}")
                    else:
                        print("No recipient address found in OCR result")
                        
                    # Extract sender name
                    if hasattr(pred, 'sender_name') and pred.sender_name:
                        label.sender_name = pred.sender_name.value
                        print(f"Found sender name: {label.sender_name}")
                    else:
                        print("No sender name found in OCR result")
                        
                    # Fallbacks
                    # If recipient name is empty but sender name is not, use sender name
                    if not label.recipient_name and label.sender_name:
                        print(f"Using sender name as fallback for recipient: {label.sender_name}")
                        label.recipient_name = label.sender_name
                        
                    # If recipient address is empty but sender address exists
                    if not label.recipient_address and hasattr(pred, 'sender_address') and pred.sender_address:
                        print(f"Using sender address as fallback for recipient address")
                        label.recipient_address = pred.sender_address.complete
                else:
                    print("No inference or prediction found in document")
            else:
                print("No document found in result")
                
            # Final check: return None if all fields are empty
            if not label.recipient_name and not label.sender_name and not label.recipient_address:
                print("All fields are empty, returning None")
                return None
                
            return label
        except Exception as extract_error:
            print(f"Error extracting data from response: {str(extract_error)}")
            return None
    except Exception as e:
        print(f"Error in generate_label_details: {str(e)}")
        return None

# Print a brief summary of the parsed data
# print(result.document)