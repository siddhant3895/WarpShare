import fnmatch
import sys
import click
from pathlib import Path
from rich.console import Console

console = Console()

EXACT_SECRETS = {
    ".env",
    ".npmrc",  # Fixed typo from .nprc
    ".yarnrc",
    ".pypirc",
    ".netrc",
    ".git-credentials",
    "id_rsa",
    "id_ed25519",
    "authorized_keys",
    "secrets.yaml",
    "secrets.yml",
    "terraform.tfvars",
    "wp-config.php",
    "database.yml",
    "service-account.json",
    "gcloud.json",
    "azureprofile.json",  # Lowercase for case-insensitive matching
}

WILDCARD_SECRETS = (
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.crt",
    "*.cer",
    "*.keystore",
    ".env.*",
)


def confirm_to_share_secrets_in_cwd(path: str) -> None:
    base_path = Path(path)
    is_asked = False

    # Use rglob("*") to catch secrets in subdirectories too
    for file_path in base_path.rglob("*"):
        if not file_path.is_file():
            continue

        name_lower = file_path.name.lower()
        rel_path = str(file_path.relative_to(base_path))

        # Combine checks with 'or' / 'elif' so a file is never prompted twice
        is_exact = name_lower in EXACT_SECRETS
        is_wildcard = any(fnmatch.fnmatchcase(name_lower, pattern) for pattern in WILDCARD_SECRETS)

        if is_exact or is_wildcard:
            ask(rel_path, is_asked)
            is_asked = True


def ask(filename: str, is_asked: bool) -> None:
    if not is_asked:
        console.print(
            "\n[bold yellow][Warning][/bold yellow] This directory contains files that may hold secrets, credentials, or private keys."
        )
    else:
        print()

    console.print(f"[bold red][File][/bold red] {filename}")
    console.print("\nAre you sure you want to share it with the receiver? (y/N)", end=" ")
    
    value: str = click.getchar().lower()
    console.print(value)  # Echo the character so the user sees their input

    if value != "y":
        console.print("[bold red]Aborted sharing.[/bold red]")
        sys.exit(1)
