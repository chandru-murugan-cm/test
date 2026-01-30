import os, re, json, shutil, subprocess
from datetime import datetime, timezone
from openai import OpenAI
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set your OpenAI API key
client = OpenAI(api_key=openai_api_key)


def detect_imported_dependencies(temp_dir):
        """
        Parse all Solidity files in temp_dir to detect imported libraries or dependencies.
        """
        dependencies = set()
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".sol"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as sol_file:
                        content = sol_file.read()
                        # Match both named and standard imports and capture the full import path
                        imports = re.findall(r'import\s+(?:\{[^}]+\}\s+from\s+)?["\']([^"\']+)["\']', content)
                        for imp in imports:
                            if not imp.startswith("./") and not imp.startswith("../"):
                                # Add the full import path as a dependency
                                dep_parts = imp.split('/')
                                if len(dep_parts) > 1:
                                    root_dep = '/'.join(dep_parts[:2])  # Capture the root-level dependency
                                    dependencies.add(root_dep)
                                else:
                                    dependencies.add(imp)
        return dependencies

def install_dependencies(temp_dir, dependencies):
    """Install Solidity dependencies and ensure a compatible Node.js version (18). Automatically handles Solidity contract compilation using Hardhat."""

    def install_node(version, temp_dir):
        """Install Node.js in a temporary directory without requiring sudo permissions."""
        node_install_dir = os.path.join(temp_dir, "nodejs")
        node_bin_dir = os.path.join(node_install_dir, "bin")
        node_path = os.path.join(node_bin_dir, "node")
        npm_path = os.path.join(node_bin_dir, "npm")

        if os.path.exists(node_path) and os.path.exists(npm_path):
            print(f"INFO: Node.js already installed at {node_bin_dir}.")
            os.environ["PATH"] = f"{node_bin_dir}:{os.environ['PATH']}"
            return

        platform = "darwin" if "darwin" in os.uname().sysname.lower() else "linux"
        node_version_url = f"https://nodejs.org/dist/v{version}/node-v{version}-{platform}-x64.tar.xz"
        tarball_path = os.path.join(temp_dir, f"node-v{version}-{platform}-x64.tar.xz")

        try:
            subprocess.run(["curl", "-fsSL", node_version_url, "-o", tarball_path], check=True)
            subprocess.run(["tar", "-xJf", tarball_path, "-C", temp_dir], check=True)
            extracted_dir = next(d for d in os.listdir(temp_dir) if d.startswith(f"node-v{version}"))
            os.rename(os.path.join(temp_dir, extracted_dir), node_install_dir)
            os.environ["PATH"] = f"{node_bin_dir}:{os.environ['PATH']}"
            print(f"INFO: Node.js {version} installed successfully.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error during Node.js installation: {e}")

    try:
        node_version_output = subprocess.check_output(["node", "-v"], text=True).strip()
        node_version = node_version_output.lstrip("v").split(".")[0]
        if int(node_version) != 18:
            print(f"WARNING: Incompatible Node.js version: {node_version_output}. Required: 18.")
            install_node("18.15.0", temp_dir)
    except FileNotFoundError:
        print("INFO: Node.js is not installed. Installing Node.js version 18.")
        install_node("18.15.0", temp_dir)
    except Exception as e:
        print(f"ERROR: Failed to verify Node.js version: {e}")
        raise RuntimeError("Failed to ensure Node.js availability.")

    package_json_path = os.path.join(temp_dir, "package.json")
    if not os.path.exists(package_json_path):
        package_json_content = {
            "name": "contracts",
            "version": "1.0.0",
            "scripts": {
                "compile": "npx hardhat compile"
            }
        }
        with open(package_json_path, "w", encoding="utf-8") as package_file:
            json.dump(package_json_content, package_file, indent=4)

    try:
        print("INFO: Initializing npm project.")
        subprocess.run(["npm", "init", "-y"], cwd=temp_dir, check=True)
        print("INFO: Installing Hardhat locally.")
        subprocess.run(["npm", "install", "--save-dev", "hardhat", "@nomiclabs/hardhat-waffle", "ethereum-waffle", "chai", "glob"], cwd=temp_dir, check=True)

        hardhat_config_path = os.path.join(temp_dir, "hardhat.config.js")
        if not os.path.exists(hardhat_config_path):
            with open(hardhat_config_path, "w", encoding="utf-8") as config_file:
                config_file.write(
                    """require('@nomiclabs/hardhat-waffle');
const glob = require('glob');
const fs = require('fs');

// Helper to extract Solidity pragma versions
function getRequiredCompilerVersions() {
// Add a default version to ensure compatibility
const versionSet = new Set(['0.8.20']);

// Scan all Solidity files in the contracts folder
const files = glob.sync('./contracts/**/*.sol');
files.forEach((file) => {
const content = fs.readFileSync(file, { encoding: 'utf8' });
const match = content.match(/pragma solidity \^?([\d.]+);/);
if (match) {
    versionSet.add(match[1]); // Add the version (e.g., '0.8.17') to the set
}
});

// Map unique versions to compiler settings
return Array.from(versionSet).map((version) => ({
version: version,
settings: {
    optimizer: {
    enabled: true,
    runs: 200,
    },
},
}));
}

module.exports = {
solidity: {
compilers: getRequiredCompilerVersions(), // Dynamically add compilers
},
};
"""
                )
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install Hardhat or dependencies: {e}")
        raise

    # Create contracts directory
    contracts_dir = os.path.join(temp_dir, "contracts")
    os.makedirs(contracts_dir, exist_ok=True)

    for root, dirs, files in os.walk(temp_dir):
        if "node_modules" in dirs:
            dirs.remove("node_modules")  # Skip node_modules directory

        for file in files:
            if file.endswith(".sol"):
                # Construct the full file path
                file_path = os.path.join(root, file)
                
                # Determine the relative path to preserve folder structure
                relative_path = os.path.relpath(root, temp_dir)
                target_dir = os.path.join(contracts_dir, relative_path)
                
                # Create the target subdirectory if it doesn't exist
                os.makedirs(target_dir, exist_ok=True)
                
                # Move the file to the target directory, preserving structure
                shutil.move(file_path, os.path.join(target_dir, file))

    # Install additional dependencies
    try:
        print("INFO: Installing additional dependencies.")
        
        for dependency in dependencies:
            # Skip hardhat as it's already installed
            if "hardhat" in dependency:
                print(f"INFO: Skipping pre-installed dependency: {dependency}")
                continue
            if dependency.startswith('@'):
                # Ensure specific versions of OpenZeppelin contracts
                if '@openzeppelin/contracts-upgradeable' in dependency:
                    dependency = '@openzeppelin/contracts-upgradeable@latest'
                if dependency == '@openzeppelin/contracts':
                    dependency = '@openzeppelin/contracts@latest'
                
                subprocess.run(["npm", "install", dependency], cwd=temp_dir, check=True)

            elif "github.com" in dependency:
                repo_name = dependency.split('/')[-1].replace(".git", "")
                target_path = os.path.join(temp_dir, "node_modules", repo_name)
                
                if not os.path.exists(target_path):
                    subprocess.run(["git", "clone", dependency, target_path], check=True)
                    print(f"INFO: Cloned GitHub dependency: {dependency}")
                else:
                    print(f"WARNING: Dependency already exists: {dependency}")
            
            else:
                # Handle general npm dependencies like truffle
                subprocess.run(["npm", "install", dependency], cwd=temp_dir, check=True)
                print(f"INFO: Installed general npm dependency: {dependency}")

        print("INFO: Additional dependencies installed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        raise

    # Compile contracts using Hardhat
    try:
        print("INFO: Compiling contracts using Hardhat.")
        subprocess.run(["npx", "hardhat", "compile"], cwd=temp_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to compile contracts: {e}")
        raise

    print("INFO: Dependencies installed and contracts compiled successfully.")

def resolve_local_imports(temp_dir):
    """
    Resolve and validate local imports by ensuring all referenced files exist.
    """
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".sol"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as sol_file:
                    content = sol_file.read()
                    imports = re.findall(r'import\s+"([^"]+)"', content)
                    for imp in imports:
                        if imp.startswith('./') or imp.startswith('../'):
                            # Resolve relative path
                            import_path = os.path.normpath(os.path.join(root, imp))
                            if not os.path.exists(import_path):
                                print(f"ERROR: Missing local import: {imp} in {file_path}")
                                raise FileNotFoundError(f"Local import not found: {imp}")

def set_solc_version(version):
    """
    Set the Solidity compiler version using the solc-select command.
    If the version is not installed, install it first.
    """
    try:
        # Check if the requested version is already installed
        result = subprocess.run(
            ["solc-select", "versions"], capture_output=True, text=True, check=True
        )
        installed_versions = result.stdout.splitlines()

        if version not in installed_versions:
            print(f"Solidity version {version} not found. Installing...")
            # Install the requested version
            subprocess.run(["solc-select", "install", version], check=True)
            print(f"Installed Solidity version {version}")

        # Switch to the desired Solidity version
        subprocess.run(["solc-select", "use", version], check=True)
        print(f"Switched to Solidity version {version}")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to set Solidity version to {version}: {e}")
        raise Exception(f"Error setting Solidity version to {version}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def extract_solidity_version(file_content):
    """
    Extract the Solidity version from the pragma statement in the file content.
    Removes the extra characters like '^' and ';'.
    """
    match = re.search(r'pragma\s+solidity\s+([^\s;]+)', file_content)
    if match:
        version = match.group(1)
        # Remove the caret (^) if present
        return version.lstrip('^')
    return None

def rename_directories_with_spaces(temp_dir):
    """
    Renames directories with spaces (or other problematic characters) to valid names.
    This can be used for any directory in the `temp_dir` path.
    """
    for root, dirs, files in os.walk(temp_dir):
        for dir_name in dirs:
            # Replace spaces with underscores and other problematic characters (you can extend this logic)
            new_dir_name = dir_name.replace(" ", "_")  # Replace spaces with underscores
            
            # Rename the directory if necessary
            if new_dir_name != dir_name:
                os.rename(os.path.join(root, dir_name), os.path.join(root, new_dir_name))
                print(f"INFO: Renamed '{dir_name}' to '{new_dir_name}'.")

def chunk_data(slither_raw_data):
    detectors = slither_raw_data.get("results", {}).get("detectors", [])
    chunks = []

    for detector in detectors:
        chunks.append(detector)

    return chunks
    
def process_smart_contract_with_gpt(slither_data, length_of_findings):
    """Processes Slither data using OpenAI to structure it into JSON format."""
    # Prepare OpenAI API prompt
    prompt = f"""
    Given the following raw Slither scan output, process the information and return it in a valid structured JSON format.

    Raw Scan Output:
    {slither_data}

    Desired JSON Format:
    [
        {{
            "finding_name": "<Summary of the issue>",
            "issue_detail": "<Details of the issue within 255 characters>",
            "issue_background": "<Technical background and implications>",
            "issue_remediation": "<Steps to resolve the issue within 255 characters>",
            "references": "<Relevant documentation links or external references>",
            "vulnerability_classifications": "<CWE or related codes>",
            "status": "open",
            "risk_level": "<Severity level: critical, high, medium, low, informational>",
            "severity_range": <Severity score (an integer between 1 and 100)>,
            "source_scanner": "Slither",
            "scan_date": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "detailed_findings": [
                {{
                    "issue_type": "<Type of issue>",
                    "line_number": <Line number (string) where the issue occurs, or null if unavailable>,
                    "contract": "<Name of the contract where the issue was found>",
                    "function": "<Name of the affected function or null>",
                    "source_code_snippet": "<Relevant code snippet>",
                    "cwe_id": "<CWE ID or null>",
                    "references": "<Additional references or links>"
                }}
            ]
        }},
        ...
    ]

    Guidelines:
    1. **JSON Formatting**: Use valid JSON formatting with double quotes (`""`) for all values. Ensure no extraneous characters.(**Strict check**)
    2. **Field Population**: Replace placeholders (e.g., `<...>`) with actual data from the Slither output. Use `null` for missing optional fields.
    3. **Field Lengths**: Truncate `issue_detail` and `issue_remediation` fields to 255 characters while maintaining clarity.
    4. **Line Number**: line_number should be always in string format.
    5. **List Findings Names**: Extract and include the `finding_name` from the Slither output. Use Slither's standard naming conventions for common issues. Examples include:
        - "Reentrancy Vulnerability"
        - "Low-Level Call Vulnerability"
        - "Integer Overflow/Underflow"
        - "Missing Zero Check"
        - "Solidity Version Issues"
        - "Unreachable Code Detected"
        - "Redundant Storage Reads"
        - "Delegatecall to Untrusted Contract"
    6. **Output Consistency**: For {length_of_findings} Slither outputs, provide an equal number of structured JSON entries, uniquely identified and free of duplication.

    Please process the input and return the structured JSON strictly adhering to these rules.
    """

    print("INFO: Sending raw Slither output to OpenAI for structuring.")

    try:
        # Generate structured findings using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
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
        print("INFO: Successfully parsed structured JSON.")
        return findings_data

    except json.JSONDecodeError as e:
        print(f"ERROR: JSON decoding error: {e}")
        print(f"DEBUG: Problematic JSON: {cleaned_results}")
        return {'error': f"Error parsing structured JSON: {e}"}, 500
    except Exception as e:
        print(f"ERROR: OpenAI processing error: {e}")
        return {'error': f"Error processing with OpenAI: {e}"}, 500