# VM Migration App

This application facilitates the migration of VirtualBox VMs and file management using AWS S3.

## Features

- **Upload Files to S3**: Upload `.ova` or `.txt` files to an S3 bucket with optional encryption.
- **Download Files from S3**: Download files from an S3 bucket to a local directory.
- **List VirtualBox VMs**: List all VirtualBox VMs available on the host machine.
- **Export VirtualBox VMs**: Export VirtualBox VMs to `.ova` files.
- **Import VirtualBox VMs**: Import `.ova` files into VirtualBox.

## Requirements

- Python 3.x
- Streamlit
- Boto3
- VirtualBox

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ariyansahoo212/VM_Migration.git
   cd VM_Migration

2. Install the required packages:
   ```bash
   pip install -r requirements.txt

## Usage

- Run the Streamlit app:
  ```bash
  streamlit run app.py

- Follow the on-screen instructions to upload, download, list, export, and import VMs.

## Configuration

- Update the get_user_input function in app.py with your AWS credentials and S3 bucket name.
