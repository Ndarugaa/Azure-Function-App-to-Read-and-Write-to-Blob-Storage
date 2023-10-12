import logging
import random
import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobType


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        print("The timer is past due!")

    # Connect to Azure Blob Storage
    connection_string = "DefaultEndpointsProtocol=https;AccountName=telegram1downloads;AccountKey=Zo5Upi+prHmobzttXaEMs9vJpnLtO4lICsfzb++EOyZCDq69W3qmmlkroqxVrJYYNdkHV/L8pV2w+AStS9LytQ==;EndpointSuffix=core.windows.net"
    container_name = "mytestcontainer"
    blob_name = "loggg" # File to log data

    # connection_string = "Your Connection String"
    # container_name = "Container name"
    # blob_name = "Blob name" # File to log data

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Check if the container exists, and create it if it doesn't
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()

    # Get a reference to the block blob
    blob_client = blob_service_client.get_blob_client(container_name, blob_name)

    # Check if the blob exists, and create it if it doesn't
    if not blob_client.exists():
        blob_client.upload_blob(b"", blob_type=BlobType.BlockBlob)

    # Generate a random number and a random word
    num = str(random.choice(range(1, 10)))
    random_word = random.choice(['apple', 'banana', 'cherry', 'date', 'elderberry'])

    # Create the data string with current time, number, and random word
    data = f"{utc_timestamp}, {num}, {random_word}"

    try:
        # Read the existing data from the blob (if it exists)
        existing_data = blob_client.download_blob().readall() if blob_client.exists() else b""
        
        # Convert the existing data to a string and split it into lines
        existing_lines = existing_data.decode('utf-8').strip().split('\n')
        
        # Check if the generated number already exists in the existing data
        if any(num in line for line in existing_lines):
            logging.warning(f"Number {num} already exists in the blob. Skipping.")
            return

        # Append the new data to the blob with a comma separator and a newline character
        updated_data = existing_data + (b'\n' if existing_data else b"") + data.encode('utf-8')
        
        # Upload the updated data to the blob
        blob_client.upload_blob(updated_data, blob_type=BlobType.BlockBlob, overwrite=True)
        
        logging.info(f"Appended data: {data}")
    except Exception as e:
        logging.error(f"Error: {str(e)}")