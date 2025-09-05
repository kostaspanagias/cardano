# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 09:16:18 2025

@author: kpanagias
"""

import requests
import json
import os
import subprocess
import tempfile

def download_ipfs_file(ipfs_url, output_path):
    """
    Downloads a file from an IPFS URL and saves it to a specified path.
    """
    print(f"Attempting to download file from: {ipfs_url}")
    try:
        # Use a public IPFS gateway to access the file
        gateway_url = f"https://ipfs.io/ipfs/{ipfs_url.split('/ipfs/')[-1]}"
        response = requests.get(gateway_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"File successfully downloaded and saved to {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during download: {e}")
        return False

def extract_markdown_body(json_file_path):
    """
    Reads a JSON file, extracts all key-value pairs from the 'body' object,
    and returns them as a single formatted markdown string.
    """
    print(f"Reading and parsing JSON from: {json_file_path}")
    markdown_content = ""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if the "body" key exists and is a dictionary
        if "body" in data and isinstance(data["body"], dict):
            body_dict = data["body"]
            print("Successfully found and processing the 'body' dictionary.")

            # Iterate through all keys in the body dictionary
            # and format them as markdown headers with their values.
            for key, value in body_dict.items():
                markdown_content += f"# {key.capitalize()}\n\n"
                
                # Check if the value is a string or a more complex object
                if isinstance(value, str):
                    markdown_content += f"{value}\n\n"
                else:
                    # For non-string values, convert to a pretty JSON string
                    json_string = json.dumps(value, indent=2)
                    markdown_content += f"```json\n{json_string}\n```\n\n"
            
            return markdown_content
        else:
            print("Error: 'body' field not found or is not a dictionary in the JSON data.")
            return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from the file: {e}")
        return None
    except FileNotFoundError:
        print(f"Error: The file {json_file_path} was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during JSON parsing: {e}")
        return None

def convert_markdown_to_file(markdown_text, output_path, output_format):
    """
    Converts a markdown string to a specified file format (e.g., pdf, docx) using Pandoc.
    """
    print(f"Converting markdown to {output_format}: {output_path}")
    
    # Use a temporary file to handle the markdown content
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8', suffix='.md') as temp_md_file:
        temp_md_file.write(markdown_text)
        temp_md_file_path = temp_md_file.name

    try:
        # Use `--from markdown+hard_line_breaks` to ensure single newlines are respected
        subprocess.run(
            ["pandoc", "--from", "markdown+hard_line_breaks", "-o", output_path, temp_md_file_path],
            check=True
        )
        print(f"Successfully converted to {output_path}")
        return True
    except FileNotFoundError:
        print("Error: Pandoc was not found. Please ensure it's installed and in your system's PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error during Pandoc conversion:")
        print(f"Standard output: {e.stdout.decode('utf-8')}")
        print(f"Standard error: {e.stderr.decode('utf-8')}")
        return False
    finally:
        # Clean up the temporary markdown file
        os.remove(temp_md_file_path)

if __name__ == "__main__":
    # Example usage: Replace with your actual IPFS URL and desired output file name
    ipfs_url = "https://nftstorage.link/ipfs/bafkreidaclhjkzz6xj2fqjir2c2ppxm6uga246sd3gnf72j33ejzimux7q"  
    downloaded_file = "downloaded_file.json"
    output_md = "output_markdown.md"
    output_docx = "output_document.docx"
    output_pdf = "output_document.pdf"

    # Step 1: Download the file
    if download_ipfs_file(ipfs_url, downloaded_file):
        # Step 2: Extract the body
        markdown_text = extract_markdown_body(downloaded_file)
        if markdown_text:
            # Save the raw markdown to a file for review
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            print(f"Successfully saved extracted markdown to {output_md}")
            
            # Step 3: Convert the markdown to both DOCX and PDF
            convert_markdown_to_file(markdown_text, output_docx, "docx")
            #convert_markdown_to_file(markdown_text, output_pdf, "pdf")
    
    # Optional: Clean up the downloaded JSON file
    if os.path.exists(downloaded_file):
        os.remove(downloaded_file)
        print(f"Cleaned up downloaded file: {downloaded_file}")
