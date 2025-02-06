#!/usr/bin/env python

import os
import sys
import json
import base64
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
import shutil
from datetime import datetime

def get_encryption_key():
    """Generate encryption key using CONSUL_HTTP_TOKEN"""
    consul_token = os.environ.get('CONSUL_HTTP_TOKEN')
    if not consul_token:
        raise ValueError("CONSUL_HTTP_TOKEN environment variable is required for state decryption")

    hashed = hashlib.sha256(consul_token.encode()).digest()
    key = base64.urlsafe_b64encode(hashed)
    return key

def decrypt_backup(backup_path=None, view_only=False):
    """Decrypt the Terraform state backup and restore it by default

    Args:
        backup_path: Optional path to backup file
        view_only: If True, only prints the decrypted state without modifying files
    """
    terraform_dir = os.environ.get('ANSIBLE_TF_DIR', os.getcwd())

    if not backup_path:
        backup_path = Path(terraform_dir) / '.terraform' / 'terraform.tfstate.backup'
    else:
        backup_path = Path(backup_path)

    if not backup_path.exists():
        print(f"Error: Backup file not found at {backup_path}")
        sys.exit(1)

    restored_path = Path(terraform_dir) / '.terraform' / 'terraform.tfstate.restored'

    try:
        encrypted_data = backup_path.read_bytes()
        key = get_encryption_key()
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)
        state = json.loads(decrypted_data.decode())

        if view_only:
            print(json.dumps(state, indent=2))
        else:
            restored_path.write_text(json.dumps(state, indent=2))
            restored_path.chmod(0o600)
            print(f"Successfully restored decrypted state to: {restored_path}")

    except ValueError as ve:
        print(f"Error: {str(ve)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing backup: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Decrypt and restore Terraform state backup')
    parser.add_argument('--file', '-f', help='Path to backup file (optional)')
    parser.add_argument('--view', '-v', action='store_true',
                        help='Only view the decrypted state without restoring')

    args = parser.parse_args()

    decrypt_backup(args.file, args.view)
