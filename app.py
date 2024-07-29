import streamlit as st
import boto3
import os
import subprocess
import en

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def upload_file_to_s3(file_path, bucket_name, access_key, access_secret, file_key):
    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=access_secret)
    s3.upload_file(file_path, bucket_name, file_key)
    print("File uploaded successfully!")

def list_virtualbox_vms(vboxmanage_path):
    try:
        result = subprocess.run([vboxmanage_path, "list", "vms"], capture_output=True, text=True, check=True)
        vm_list = result.stdout.splitlines()
        return vm_list
    except subprocess.CalledProcessError as e:
        print(f"Error listing VirtualBox VMs: {e}")
        return []

def export_virtualbox_vm(vboxmanage_path, vm_name, local_dir):
    export_file = vm_name + ".ova"
    export_path = os.path.join(local_dir, export_file)
    print(f"Exporting '{vm_name}' to '{export_path}'...")

    try:
        subprocess.run([vboxmanage_path, "export", vm_name, "--output", export_path], check=True)
        print(f"Exported '{vm_name}' to '{export_path}' successfully.")
        return export_path
    except subprocess.CalledProcessError as e:
        print(f"Error exporting '{vm_name}': {e}")
        return None

def import_virtualbox_vm(vboxmanage_path, ova_path):
    try:
        subprocess.run([vboxmanage_path, "import", ova_path], check=True)
        print(f"Imported '{ova_path}' successfully.")
        
        imported_vm_name = os.path.splitext(os.path.basename(ova_path))[0]
        subprocess.run([vboxmanage_path, "unregistervm", imported_vm_name, "--delete"], check=True)
        print(f"Removed '{imported_vm_name}' after import.")
    except subprocess.CalledProcessError as e:
        print(f"Error importing '{ova_path}': {e}")

def download_file_from_s3(access_key, secret_key, s3_bucket, s3_key, local_directory):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    try:
        s3_client.download_file(s3_bucket, s3_key, local_directory)
        print(f"Downloaded file from S3 to {local_directory}")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        exit(1)

def fetch_s3_keys(access_key, secret_key, s3_bucket):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    keys = []
    try:
        bucket = s3.Bucket(s3_bucket)
        for obj in bucket.objects.all():
            keys.append(obj.key)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return keys

def get_user_input():
    friend_access_key = "AKIA244HY7VOKJHIYXRL"
    friend_secret_key = "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"
    friend_s3_bucket = "capston1.0"
    return friend_access_key, friend_secret_key, friend_s3_bucket

def app(keys):
    friend_access_key, friend_secret_key, friend_s3_bucket = get_user_input()
    st.title("VM and File Management Capstone Project")
    tab1, tab2 = st.tabs(["Upload", "Download"])

    with tab1:
        uploaded_file = st.file_uploader("Upload Your .ova or .txt File", type=["ova", "txt"])
        if uploaded_file:
            save_path = os.path.join("uploads", uploaded_file.name)
            ensure_directory_exists("uploads")
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            encrypt_file = st.checkbox("Encrypt file before upload")
            if encrypt_file:
                key_str = st.text_input("Enter encryption key")
                if key_str:
                    encryption_key = bytes.fromhex(key_str)
                    encrypted_data = en.encrypt_file(save_path, encryption_key)
                    encrypted_path = os.path.splitext(save_path)[0] + ".enc"
                    with open(encrypted_path, 'wb') as f:
                        f.write(encrypted_data)
                    upload_path = encrypted_path
                    file_key = os.path.basename(encrypted_path)
                else:
                    st.warning("Please enter an encryption key.")
            else:
                upload_path = save_path
                file_key = os.path.splitext(os.path.basename(save_path))[0] + ".enc"

            if st.button("Upload to S3"):
                upload_file_to_s3(upload_path, friend_s3_bucket, friend_access_key, friend_secret_key, file_key)
                st.success("File uploaded successfully to S3.")
                if encrypt_file:
                    os.remove(encrypted_path)

    with tab2:
        key = st.selectbox("Select File", ["Select"] + keys)
        if key.endswith(".enc"):
            local_path = os.path.join("downloads", key)
            decrypt_key = st.text_input("Provide key to decrypt")
            flag = True
        else:
            local_path = os.path.join("downloads", key)
            flag = False

        if st.button("Download"):
            ensure_directory_exists("downloads")
            with st.spinner("Downloading in progress..."):
                download_file_from_s3(friend_access_key, friend_secret_key, friend_s3_bucket, key, local_path)
            if flag:
                decrypted_data = en.decrypt_file(local_path, bytes.fromhex(decrypt_key))
                decrypted_path = os.path.splitext(local_path)[0] + (".ova" if key.endswith(".ova.enc") else ".txt")
                with open(decrypted_path, 'wb') as f:
                    f.write(decrypted_data)
                st.success(f"Downloaded and decrypted successfully.")
            else:
                st.success(f"Downloaded successfully.")

    vboxmanage_path = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
    loca_dir = r"C:\Users\dipes\Downloads\final capstron"
    real = list_virtualbox_vms(vboxmanage_path)
    with tab1:
        vm_img = st.selectbox("Select VM Image to Export", ["Select"] + real)
        if vm_img and vm_img != "Select":
            selected_vm_name = vm_img.split()[0].strip('"')
            encrypt_file = st.checkbox("Encrypt VM before upload")
            key_str = ""
            if encrypt_file:
                key_str = st.text_input("Enter encryption key")

            if st.button("Export and Upload VM"):
                with st.spinner("Exporting..."):
                    export_path = export_virtualbox_vm(vboxmanage_path, selected_vm_name, loca_dir)
                    if export_path:
                        st.success(f"Exported {selected_vm_name} successfully to {export_path}")
                        if encrypt_file:
                            if key_str:
                                encryption_key = bytes.fromhex(key_str)
                                encrypted_data = en.encrypt_file(export_path, encryption_key)
                                encrypted_path = os.path.splitext(export_path)[0] + ".enc"
                                with open(encrypted_path, 'wb') as f:
                                    f.write(encrypted_data)
                                upload_path = encrypted_path
                                file_key = os.path.basename(encrypted_path)
                                os.remove(export_path)  # Remove the unencrypted file
                            else:
                                st.warning("Please enter an encryption key.")
                                return
                        else:
                            upload_path = export_path
                            file_key = os.path.splitext(os.path.basename(export_path))[0] + ".enc"

                        upload_file_to_s3(upload_path, friend_s3_bucket, friend_access_key, friend_secret_key, file_key)
                        st.success("VM uploaded successfully to S3.")
                        if encrypt_file:
                            os.remove(encrypted_path)

if __name__ == "__main__":
    friend_access_key, friend_secret_key, friend_s3_bucket = get_user_input()
    keys = fetch_s3_keys(friend_access_key, friend_secret_key, friend_s3_bucket)
    app(keys)