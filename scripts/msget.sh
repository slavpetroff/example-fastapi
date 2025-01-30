#!/bin/bash

# Check if an extension ID is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <extension_id>"
  echo "Example: $0 ms-python.python"
  exit 1
fi

# Set downloads directory
DOWNLOADS_DIR="$HOME/Downloads"

extension_id="$1"

# Extract the publisher name and extension name from the ID
publisher=$(echo "$extension_id" | cut -d'.' -f1)
package=$(echo "$extension_id" | cut -d'.' -f2)

# Construct the download URL
download_url="https://${publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/${publisher}/extension/${package}/latest/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"

# Construct the filename with full path
vsix_filename="${DOWNLOADS_DIR}/${extension_id}.vsix"

# Download the VSIX file using the constructed URL
echo "Downloading ${extension_id}..."
curl -L -o "$vsix_filename" "$download_url"

if [ $? -eq 0 ]; then
  echo "Successfully downloaded: $vsix_filename"
else
  echo "Failed to download the extension"
  exit 1
fi
