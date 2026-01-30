from entities.CyberServiceEntity import ScannerTypes
import json

def findScanTypeId(input_text, field):
    try:
        # Query all documents from the ScannerTypes collection
        scanner_types_obj = ScannerTypes.objects()
        
        # List to hold the matched results
        matched_results = []
        scanner_type_data ={}
        # Loop through all scan_type values and check for partial match with input_text
        for scanner_type in scanner_types_obj:
            scan_type_value = scanner_type[field]
            
            # Check if the scan_type value is a substring of the input_text (case-insensitive)
            if scan_type_value.lower() in input_text.lower():  # Case-insensitive check
                matched_results.append(json.loads(scanner_type.to_json()))
                scanner_type_data = json.loads(scanner_type.to_json())
                
                break
        scan_type_id = scanner_type_data.get("_id",'')
        # Convert the matched results to JSON format
        # scanner_types_data = json.loads(json.dumps(matched_results, default=str))  # Convert to JSON
        
        if scan_type_id:
            return scan_type_id
        else:
            return 'others'
    except Exception as e:
        print("Exception:", e)
        return str(e)