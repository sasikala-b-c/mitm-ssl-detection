from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CERTS_DIR = Path(__file__).parent


def create_self_signed_cert(common_name: str, cert_path: Path, key_path: Path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Demo"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    san = x509.SubjectAlternativeName([
        x509.DNSName("localhost"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(minutes=1))
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(san, critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


if __name__ == "__main__":
    CERTS_DIR.mkdir(parents=True, exist_ok=True)
    create_self_signed_cert("server.local", CERTS_DIR / "server.crt", CERTS_DIR / "server.key")
    create_self_signed_cert("proxy.local", CERTS_DIR / "proxy.crt", CERTS_DIR / "proxy.key")
    print("Generated certs in:", CERTS_DIR)
