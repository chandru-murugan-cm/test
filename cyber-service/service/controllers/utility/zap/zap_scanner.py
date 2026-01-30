import requests
import time
import json
import re
from datetime import datetime, timezone
from uuid import uuid4
from enum import Enum

# Constants
zap_base_url = 'http://localhost:8080'
api_key = 'tmfqqgpr89e8o5v1s1qv6pk27d'

# Enum for severity levels
class FindingSeverity(Enum):
    Critical = 'critical'
    High = 'high'
    Medium = 'medium'
    Low = 'low'
    Information = 'informational'

# Helper functions for extracting risk and cleaning data
# def extract_risk_level(risk):
#     risk_desc_clean = risk.lower()
#     if 'critical' in risk_desc_clean:
#         return FindingSeverity.Critical.value
#     elif 'high' in risk_desc_clean:
#         return FindingSeverity.High.value
#     elif 'medium' in risk_desc_clean:
#         return FindingSeverity.Medium.value
#     elif 'low' in risk_desc_clean:
#         return FindingSeverity.Low.value
#     elif 'informational' in risk_desc_clean or 'information' in risk_desc_clean:
#         return FindingSeverity.Information.value
#     else:
#         raise ValueError(f"Unrecognized severity: {risk_desc}")

def strip_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def convert_raw_output(alert_data):
    transformed_alerts = []
    if 'alerts' not in alert_data:
        return transformed_alerts
    
    for alert in alert_data['alerts']:
        transformed_alert = {
            "finding_id": "",  
            "finding_date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "target_id": "",  
            "scan_type_id": "",
            "finding_name": alert.get("url", ""),
            "finding_desc": alert.get("description", ""),
            "severity": alert.get("risk", "").lower(),
            "status": "Open",
            "extended_finding_details_name": "DomainZap1",  
            "extended_finding_details_id": "",  
            "fix_recommendation": alert.get("solution", ""),
            "raw_scan_output_id": "",
            "domain_zap_1_record": {
                # "finding_id": alert_id,
                "alert":alert.get("alert", ""),
                "other":alert.get("other", ""),
                "method": alert.get("method", ""),
                "evidence": alert.get("evidence", ""),
                "cweid": alert.get("cweid", ""),
                "confidence": alert.get("confidence", ""),
                "wascid": alert.get("wascid", ""),
                "tags": alert.get("tags", ""),
                "reference": alert.get("reference", ""),
                "param": alert.get("param", ""),
                "attack": alert.get("attack", ""),
            }
        }
        transformed_alerts.append(transformed_alert)

    # for site in site_data['site']:
    #     target_domain = site.get('@name', '')
    #     target_host = site.get('@host', '')
    #     target_port = site.get('@port', '')
    #     ssl_enabled = site.get('@ssl', '')

    #     for alert in site.get('alerts', []):
    #         alert_id = alert.get("pluginid", "")
    #         raw_alert = alert.get("alert", "")
    #         finding_desc = strip_html_tags(alert.get("desc", ""))
    #         severity = extract_risk_level(alert.get("riskdesc", ""))
    #         status = "Open"
    #         fix_recommendation = strip_html_tags(alert.get("solution", ""))
    #         scan_type_id = ""  # Assuming ZAP scanner predefined with a scan type ID

    #         for instance in alert.get("instances", []):
    #             transformed_alert = {
    #                 "finding_id": "",  # Same alert_id for all instances of this alert
    #                 "finding_date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
    #                 "target_id": target_domain,  # Target domain here
    #                 "scan_type_id": scan_type_id,
    #                 "finding_name": instance.get("uri", ""),
    #                 "finding_desc": finding_desc,
    #                 "severity": severity,
    #                 "status": status,
    #                 "extended_finding_details_name": "DomainZap1",  # Unique ID for extended details
    #                 "extended_finding_details_id": "",  # Unique ID for extended details
    #                 "fix_recommendation": fix_recommendation,
    #                 "raw_scan_output_id": "",
    #                 "domain_zap_1_record": {
    #                     "finding_id": alert_id,
    #                     "alert":raw_alert,
    #                     "uri": instance.get("uri", ""),
    #                     "method": instance.get("method", ""),
    #                     "param": instance.get("param", ""),
    #                     "evidence": instance.get("evidence", ""),
    #                     "otherinfo": instance.get("otherinfo", ""),
    #                     "attack": instance.get("attack", ""),
    #                     "confidence": alert.get("confidence", ""),
    #                     "cweid": alert.get("cweid", ""),
    #                     "wascid": alert.get("wascid", ""),
    #                     "target_host": target_host,
    #                     "target_port": target_port,
    #                     "ssl_enabled": ssl_enabled,
    #                 }
    #             }
    #             transformed_alerts.append(transformed_alert)

    return transformed_alerts

def run_zap_scan(target):
    print(f"Starting ZAP scan on {target}...")

    # Spider the website (reduced maxChildren and recursion disabled)
    print(f"Starting spidering on {target}...")
    spider_endpoint = f'{zap_base_url}/JSON/spider/action/scan/'
    spider_params = {'apikey': api_key, 'url': target, 'maxChildren': '10', 'recurse': 'true'}
    spider_response = requests.get(spider_endpoint, params=spider_params).json()
    scan_id = spider_response.get('scan')
    print(f"Spider scan initiated with scan ID: {scan_id}")

    # Wait for spider to finish
    print("Waiting for spider scan to finish...")
    while True:
        status_endpoint = f'{zap_base_url}/JSON/spider/view/status/'
        status_response = requests.get(status_endpoint, params={'apikey': api_key}).json()
        status = status_response.get('status')
        if int(status) >= 100:
            print("Spider scan completed.")
            break
        time.sleep(5)

    # Wait for passive scan to finish
    print("Waiting for passive scan to finish...")
    while True:
        pscan_status_endpoint = f'{zap_base_url}/JSON/pscan/view/recordsToScan/'
        pscan_status_response = requests.get(pscan_status_endpoint, params={'apikey': api_key}).json()
        records_to_scan = int(pscan_status_response.get('recordsToScan', 0))
        if records_to_scan == 0:
            print("Passive scan completed.")
            break
        print(f"Records remaining for passive scan: {records_to_scan}")
        time.sleep(5)

    # Start active scan with increased threads and reduced scope
    print("Starting active scan with enhanced thread count...")
    ascan_endpoint = f'{zap_base_url}/JSON/ascan/action/scan/'
    ascan_params = {'apikey': api_key, 'url': target, 'recurse': 'false', 'maxChildren': '5', 'threadPerHost': '15'}
    requests.get(ascan_endpoint, params=ascan_params)


    # Wait for active scan to finish
    print("Waiting for active scan to finish...")
    while True:
        ascan_status_endpoint = f'{zap_base_url}/JSON/ascan/view/status/'
        ascan_status_response = requests.get(ascan_status_endpoint, params={'apikey': api_key}).json()
        ascan_status = ascan_status_response.get('status')
        if int(ascan_status) >= 100:
            print("Active scan completed.")
            break
        time.sleep(5)

    # Exclude unnecessary file types (like images)
    print("Excluding unnecessary file types from scan...")
    exclude_from_scan_endpoint = f'{zap_base_url}/JSON/spider/action/excludeFromScan/'
    exclude_params = {'apikey': api_key, 'regex': '.*(jpg|png|gif|mp4)$'}
    requests.get(exclude_from_scan_endpoint, params=exclude_params)

    # Get alerts
    print("Retrieving alerts from ZAP...")
    alerts_endpoint = f'{zap_base_url}/JSON/core/view/alerts/'
    alerts_params = {'apikey': api_key, 'baseurl': target, 'start': '0', 'count': '1000'}
    alerts_response = requests.get(alerts_endpoint, params=alerts_params).json()
    print(f'Alerts: {alerts_response}')

    # Parse the report
    # report_endpoint = f'{zap_base_url}/OTHER/core/other/jsonreport/'
    # report_response = requests.get(report_endpoint, params={'apikey': api_key})
    # print("type", type(alerts_response))
    # alert_json = json.loads(alerts_response)
    # raw_op = alerts_response.get('alerts')
    print("found alerts", len(alerts_response.get('alerts')))
    return alerts_response

    # transformed_alerts = convert_alerts(parsed_report)
    # print(f"Found {len(transformed_alerts)} alerts.")
    # return transformed_alerts