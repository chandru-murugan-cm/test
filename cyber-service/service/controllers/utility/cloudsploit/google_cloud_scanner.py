import json
import subprocess
import tempfile
import os
import requests
import time
import re
from datetime import datetime, timezone
from uuid import uuid4
from enum import Enum
from openai import OpenAI


# Get OpenAI API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set your OpenAI API key
client = OpenAI(api_key=openai_api_key)



def map_scan_type_id(finding, scanner_types):
    """
    Use OpenAI to map finding to the appropriate scan_type_id from scanner_types.
    """
    prompt = f"""
    You are given a list of available scanner types and a security finding. Your task is to identify the most appropriate scan_type_id for the finding from the list of scanner types.

    Scanner types (in JSON format):
    {scanner_types}
    
    Finding (in JSON format):
    {finding}
    
    Use the description of the scanner types and the details of the finding to match the finding with the most relevant scan_type_id. Return the scan_type_id as a JSON response.

    Must have the appropriate scan_type_id in the response.
    
    Response format:
    {{
      "scan_type_id": "<appropriate_scan_type_id>"
    }}
    """
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        # print("response:", response)

        structured_results = response.choices[0].message.content
        print("INFO: Structured results received from OpenAI.")
        print(f"DEBUG: Structured results: {structured_results}")

        # Safeguard JSON extraction
        if "```json" in structured_results:
            cleaned_results = structured_results.split('```json', 1)[-1].split('```', 1)[0].strip()
        else:
            cleaned_results = structured_results.strip()

        # Validate and parse JSON
        findings_data = json.loads(cleaned_results)
        print("INFO: Successfully parsed structured JSON.", findings_data)
        scan_type_id = findings_data.get("scan_type_id", None)
        if scan_type_id is None:
            return "others"
        return scan_type_id
    except Exception as e:
        print(f"Error mapping scan_type_id: {e}")
        return None, str(e)
  
def run_google_cloud_scan(project_id, scan_id, google_cloud_data, google_scanner_id, current_user, google_cloudsploit_config_path, google_cloudsploit_original_content):
    # Step 1: Create a temp file to store the output of the scan
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as temp_output_file:
        temp_output_file_path = temp_output_file.name

    cloudsploit_base_path = os.getenv('CLOUDSPLOIT_CLONE_PATH')

    index_js_path = os.path.join(cloudsploit_base_path, "index.js")
    config_js_path = os.path.join(cloudsploit_base_path, "config_example.js")
    
    # Step 2: Define the command to run the scan (credentials are handled in config_example.js)
    scan_command = [
        index_js_path,
        "--config", config_js_path,
        "--json", temp_output_file_path,
        "--cloud", "google",
        "--ignore-ok",
        "--run-asl"
    ]

    # Step 3: Run the scan using subprocess and capture the output
    try:
        result = subprocess.run(scan_command, capture_output=True, text=True, check=True)
        print(f"Scan successful. Command output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running scan: {e.stderr}")
        return {"error": "Scan failed", "details": e.stderr}, None

    # Restore the original content after printing
    with open(google_cloudsploit_config_path, 'w') as file:
        file.write(google_cloudsploit_original_content) 

    # Step 4: Check for any generic error message in stdout
    # error_pattern = r"(ERROR|Error|error):\s*(.*)"
    # match = re.search(error_pattern, result.stdout)
    # if match:
    #     error_message = match.group(2)  # Extract the error message after "ERROR"
    #     print(f"Error detected: {error_message}")
    #     return {"error": "Scan encountered an error", "details": error_message}, None

    # Step 5: Read the JSON output from the temp file
    try:
        with open(temp_output_file_path, 'r') as output_file:
            scan_output = json.load(output_file)
        print(f"Scan output: {scan_output}")
    except Exception as e:
        print(f"Failed to read scan output: {str(e)}")
        return {"error": "Failed to parse scan output", "details": str(e)}, None
    finally:
        # Step 6: Clean up the temp output file
        os.remove(temp_output_file_path)


    print(f"Reverted {google_cloudsploit_config_path} back to its original state.")

    # Return the command output and parsed JSON output of the scan
    return result.stdout, scan_output

def convert_structured_google_output(google_scan_json_data, scanner_types):
    result = []
   
    for data in google_scan_json_data:
        finding = {
            "finding_id": "",  
            "finding_date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "target_id": "",  
            "scan_type_id": map_scan_type_id(data, scanner_types),
            "finding_name": data.get("title", ""),
            "finding_desc": data.get("description", ""),
            "severity": "high",
            "status": "open",
            "extended_finding_details_name": "CloudCloudSploitGoogle1",  
            "extended_finding_details_id": "",  
            "fix_recommendation": "",
            "raw_scan_output_id": "",
            "cloud_cloudsploit_google_1_record": {  
                "plugin": data.get("plugin"),
                "title": data.get("title"),
                "category":  data.get("category"), 
                "description":  data.get("description"),
                "resource":  data.get("resource"),
                "region":  data.get("region"), 
                "status":  data.get("status"), 
                "message":  data.get("message")
            }
        }
        result.append(finding)

    # Pass the constructed findings to map_scan_type_id function
    # response = map_scan_type_id(result, scanner_types)

    print("openai response:", result)
    return result