import os
import subprocess
import json
from datetime import datetime, timezone
import uuid
from enum import Enum
import tempfile

class FindingStatus(Enum):
    Open = 'open'
    Closed = 'closed'
    Ignored = 'ignored'
    FalsePositive = 'false positive'


class FindingSeverity(Enum):
    Critical = 'critical'
    High = 'high'
    Medium = 'medium'
    Low = 'low'
    Informational = 'informational'


def install_dependencies(repo_path):
    """
    Installs necessary dependencies for the repository before scanning.

    Args:
        repo_path (str): Path to the repository being scanned.

    Returns:
        bool: True if dependencies were installed, False otherwise.
    """
    installed = False
    for root, _, files in os.walk(repo_path):
        # Skip test directories
        if 'tests' in root.lower() or 'test' in root.lower():
            print(f"Skipping installation in the 'tests' folder: {repo_path}")
            continue

        # Check for dependency files and run appropriate install commands
        if "package.json" in files:
            print(f"Detected npm at {root}. Running 'npm install'...")
            try:
                subprocess.run(["npm", "install"], cwd=root, check=True)
                installed = True
            except subprocess.CalledProcessError as e:
                print(f"Error running 'npm install' in {root}: {e}")
                continue
        elif "requirements.txt" in files:
            print(f"Detected pip at {root}. Running 'pip install -r requirements.txt'...")
            try:
                subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=root, check=True)
                installed = True
            except subprocess.CalledProcessError as e:
                print(f"Error running 'pip install' in {root}: {e}")
                continue
        elif "go.mod" in files:
            print(f"Detected Go at {root}. Running 'go mod tidy'...")
            try:
                subprocess.run(["go", "mod", "tidy"], cwd=root, check=True)
                installed = True
            except subprocess.CalledProcessError as e:
                print(f"Error running 'go mod tidy' in {root}: {e}")
                continue
    return installed

def convert_trivy_output(raw_data):
    """
    Converts raw Trivy output to a structured JSON format.

    Args:
        raw_data (dict): Raw Trivy scan results in dictionary format.

    Returns:
        list: Transformed structured results.
    """
    transformed_alerts = []
    # raw_data = json.loads(raw_data)

    # Check if the raw_data contains results
    if 'Results' not in raw_data:
        return transformed_alerts

    for result in raw_data['Results']:
        target = result.get('Target', '')
        target_type = result.get('Type', '')

        # Handle vulnerabilities
        vulnerabilities = result.get('Vulnerabilities', [])
        for vuln in vulnerabilities:
            alert_id = vuln.get('VulnerabilityID', '')
            raw_alert = vuln.get('Title', '')

            severity_value = vuln.get('Severity', '').strip().lower()
            severity = next(
                (severity_enum.value for severity_enum in FindingSeverity if severity_enum.value == severity_value),
                ''  # Default to empty string if no match is found
            )

            # Build the repository_trivy_1_record
            repository_trivy_1_record = {
                "finding_id": alert_id,
                "alert": raw_alert,
                "uri": vuln.get('PkgName', ''),
                "param": vuln.get('InstalledVersion', ''),
                "evidence": vuln.get('Description', ''),
                "otherinfo": vuln.get('PrimaryURL', ''),
                "cweid": vuln.get('CweIDs', []),
                "target_host": target  # Target path or file scanned
            }

            # Add structured alert
            transformed_alert = {
                "finding_date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                "scan_type": target_type,
                "vulnerability_id": alert_id,
                "package_name": vuln.get('PkgName', ''),
                "installed_version": vuln.get('InstalledVersion', ''),
                "fixed_version": vuln.get('FixedVersion', ''),
                "severity": severity,
                "finding_name": raw_alert,
                "finding_desc": vuln.get('Description', ''),
                "target_id": vuln.get('PrimaryURL', ''),
                "cwe_ids": vuln.get('CweIDs', []),
                "references": vuln.get('References', []),
                "repository_trivy_1_record": repository_trivy_1_record,
                "status": FindingStatus.Open.value
            }

            transformed_alerts.append(transformed_alert)

        # Handle misconfigurations
        misconfigurations = result.get('Misconfigurations', [])
        for misconf in misconfigurations:
            alert_id = misconf.get('ID', '')
            raw_alert = misconf.get('Title', '')

            # Determine severity using enums
            severity_value = misconf.get('Severity', '').strip().lower()  # Normalize severity value
            severity = next(
                (severity_enum.value for severity_enum in FindingSeverity if severity_enum.value == severity_value),
                ''  # Default to empty string if no match is found
            )

            # Build the repository_trivy_1_record for misconfigurations
            repository_trivy_1_record = {
                "finding_id": alert_id,
                "alert": raw_alert,
                "uri": misconf.get('Namespace', ''),
                "param": misconf.get('Query', ''),
                "evidence": misconf.get('Resolution', ''),
                "otherinfo": misconf.get('Message', ''),
                "cweid": [],  # Misconfigurations may not have CWE IDs
                "target_host": target
            }

            # Add structured alert for misconfiguration
            transformed_alert = {
                "finding_date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                "scan_type": target_type,
                "vulnerability_id": alert_id,
                "package_name": misconf.get('Namespace', ''),
                "installed_version": "N/A",  # Not applicable for misconfigurations
                "fixed_version": "N/A",  # Not applicable for misconfigurations
                "severity": severity,
                "finding_name": raw_alert,
                "finding_desc": misconf.get('Description', ''),
                "target_id": misconf.get('PrimaryURL', ''),
                "cwe_ids": [],
                "references": misconf.get('References', []),
                "repository_trivy_1_record": repository_trivy_1_record,
                "status": FindingStatus.Open.value
            }

            transformed_alerts.append(transformed_alert)

    return transformed_alerts


def run_trivy_scan(repo_path, access_token, is_private_repo):
    """
    Runs the Trivy scan and converts the output to a structured format.

    Args:
        repo_path (str): Path to the repository being scanned.

    Returns:
        list: Structured Trivy scan results.
    """

    set_github_token(access_token, is_private_repo)

    # Install dependencies
    dependencies_installed = install_dependencies(repo_path)
    if dependencies_installed:
        print("Dependencies installed successfully.")
    else:
        print("No dependencies detected to install.")
    print("Running Trivy...")
    print("Repo path:", repo_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as output_file:
        output_temp_file_path = output_file.name
    try:
        # Run the Trivy scan and capture the output
        result = subprocess.run(
            [
                "trivy", "repo",
                "--scanners", "vuln,misconfig",
                "--ignore-unfixed",
                "--format", "json",
                repo_path,
                "-o", output_temp_file_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        trivy_output = result.stdout
        print("Trivy scan completed successfully.")

        # Read the output from the temporary file
        with open(output_temp_file_path, 'r') as file:
            trivy_output = file.read()
            trivy_json_data = json.loads(trivy_output)  # Convert JSON string to Python object
        print("raw_data ", trivy_json_data)

        # Clean up temporary files
        os.remove(output_temp_file_path)

        # Convert raw Trivy output to structured format
        # raw_data = json.loads(trivy_output)
        return trivy_output, trivy_json_data

    except subprocess.CalledProcessError as e:
        print(f"Error running Trivy: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: Trivy is not installed or not found in the system path.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to parse Trivy output.")
        return None

def run_licenses_and_sbom_scan(repo_path, access_token, is_private_repo):
    """
    Runs the Trivy SBOM and license scan, and converts the output to a structured format.

    Args:
        repo_path (str): Path to the repository being scanned.
        access_token (str): GitHub access token if scanning a private repo.
        is_private_repo (bool): Whether the repository is private.

    Returns:
        tuple: Trivy raw output and structured JSON data.
    """
    print("Running Trivy for SBOM and licenses...")
    print("Repo path:", repo_path)

    set_github_token(access_token, is_private_repo)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            sbom_temp_file_path = temp_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as output_file:
            output_temp_file_path = output_file.name

        # Step 1: Run the Trivy SBOM scan with vulnerabilities
        sbom_scan_cmd = [
            "trivy", "repository",
            "--format", "spdx-json",
            "--output", sbom_temp_file_path,
            repo_path,
            "--include-dev-deps",
            "--scanners", "vuln"
        ]
        subprocess.run(sbom_scan_cmd, check=True)
        print("SBOM scan completed successfully.")

        # Step 2: Run the Trivy SBOM scan for licenses
        license_scan_cmd = [
            "trivy", "sbom", sbom_temp_file_path,
            "--scanners", "vuln,license",
            "-f", "json",
            "-o", output_temp_file_path
        ]
        subprocess.run(license_scan_cmd, check=True)
        print("License and vulnerability scan completed successfully.")
        
        # Read the output from the temporary file
        with open(output_temp_file_path, 'r') as file:
            trivy_output = file.read()
            trivy_json_data = json.loads(trivy_output)  # Convert JSON string to Python object
        print("raw_data ", trivy_json_data)
        
        # Clean up temporary files
        os.remove(sbom_temp_file_path)
        os.remove(output_temp_file_path)

        return trivy_output, trivy_json_data

    except subprocess.CalledProcessError as e:
        print(f"Error running Trivy: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: Trivy is not installed or not found in the system path.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to parse Trivy output.")
        return None
    

def run_package_licenses_scan(repo_path, access_token, is_private_repo):
    """
    Runs the Trivy SBOM and license scan, and converts the output to a structured format.

    Args:
        repo_path (str): Path to the repository being scanned.
        access_token (str): GitHub access token if scanning a private repo.
        is_private_repo (bool): Whether the repository is private.

    Returns:
        tuple: Trivy raw output and structured JSON data.
    """

    # print("Running Trivy for SBOM and licenses...")
    # print("Repo path:", repo_path)

    set_github_token(access_token, is_private_repo)

    # Install dependencies
    dependencies_installed = install_dependencies(repo_path)
    if dependencies_installed:
        print("Dependencies installed successfully.")
    else:
        print("No dependencies detected to install.")
    print("Running Trivy...")
    print("Repo path:", repo_path)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as output_file:
            output_temp_file_path = output_file.name

        # Step 1: Run the Trivy SBOM scan with vulnerabilities
        sbom_scan_cmd = [
            "trivy", "fs",
            repo_path,
            "--scanners", "license",
            "--license-full",
            "--include-dev-deps",
            "--license-confidence-level", "0.8",
            "-f", "json",
            "-o", output_temp_file_path
        ]
        subprocess.run(sbom_scan_cmd, check=True)
        print("Package and License scan completed successfully.")

        
        # Read the output from the temporary file
        with open(output_temp_file_path, 'r') as file:
            trivy_output = file.read()
            trivy_json_data = json.loads(trivy_output)  
        print("raw_data ", trivy_json_data)
        
        # Clean up temporary files
        os.remove(output_temp_file_path)

        return trivy_output, trivy_json_data

    except subprocess.CalledProcessError as e:
        print(f"Error running Trivy: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: Trivy is not installed or not found in the system path.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to parse Trivy output.")
        return None
    
def set_github_token(access_token, is_private_repo):
    """
    Sets the GITHUB_TOKEN environment variable based on the repository type.

    Args:
        access_token (str): The access token for private repositories.
        is_private_repo (bool): Flag indicating if the repository is private.
    """
    if is_private_repo:
        os.environ["GITHUB_TOKEN"] = access_token
        print("GITHUB_TOKEN set for private repository.")
    else:
        os.environ["GITHUB_TOKEN"] = ''
        print("GITHUB_TOKEN cleared for public repository.")