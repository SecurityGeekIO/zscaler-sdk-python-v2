# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import pytest
import hashlib
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from tests.integration.zpa.mocks import MockZPAClient, modify_request, modify_response


@pytest.fixture
def fs():
    yield


class TestCertificates:
    """
    Integration Tests for the Certificates
    """

    @pytest.mark.vcr(before_record_response=modify_response, before_record_request=modify_request)
    @pytest.mark.asyncio
    async def test_certificates_crud(self, fs):
        # Instantiate Mock Client
        client = MockZPAClient(fs)
        errors = []
        certificate = None
        try:
            cert_bytes, key_bytes = generate_self_signed_cert("example.com")
            cert_pem = pem_encode(cert_bytes, "CERTIFICATE")
            key_pem = pem_encode(key_bytes, "RSA PRIVATE KEY")
            certificate = client.certificates.add_certificate(
                name="itest-certificate",
                cert_blob=f"{key_pem}\n{cert_pem}",
                description="Self-signed certificate for testing",
            )
            assert certificate.id is not None and certificate.id != ""
            assert certificate.name == "itest-certificate"
        except Exception as exc:
            errors.append(exc)

        try:
            remote_cert = client.certificates.get_certificate(certificate_id=certificate.id)
            assert remote_cert.name == certificate.name
        except Exception as exc:
            errors.append(exc)

        try:
            certs = client.certificates.list_all_certificates()
            assert len(certs) > 0
        except Exception as exc:
            errors.append(exc)

        try:
            status = client.certificates.delete_certificate(certificate_id=certificate.id)
            assert status > 200 and status < 299
        except Exception as exc:
            errors.append(exc)
        assert len(errors) == 0


def generate_self_signed_cert(cert_name):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    public_key = private_key.public_key()

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(
        x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Jose"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "BD-HashiCorp"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "ITDepartment"),
                x509.NameAttribute(NameOID.COMMON_NAME, cert_name),
            ]
        )
    )
    builder = builder.issuer_name(
        x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Jose"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "BD-HashiCorp"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "ITDepartment"),
                x509.NameAttribute(NameOID.COMMON_NAME, cert_name),
            ]
        )
    )
    builder = builder.not_valid_before(datetime.datetime.now())
    builder = builder.not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))  # 1 year
    builder = builder.serial_number(int(hashlib.sha1(cert_name.encode()).hexdigest(), 16))
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    builder = builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,
            key_encipherment=True,
            data_encipherment=True,
            key_agreement=True,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=True,
            decipher_only=True,
        ),
        critical=True,
    )
    builder = builder.add_extension(
        x509.ExtendedKeyUsage(
            [
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]
        ),
        critical=True,
    )

    certificate = builder.sign(private_key=private_key, algorithm=hashes.SHA256(), backend=default_backend())

    return certificate.public_bytes(serialization.Encoding.PEM), private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


def pem_encode(der_bytes, pem_type):
    return der_bytes.decode("utf-8")
