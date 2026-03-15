"""
Custom SMTP Email Backend for Django CFG.

Supports SMTP with unverified SSL certificates for development environments.
"""

import smtplib
import ssl

from django.core.mail.backends.smtp import EmailBackend as DjangoSMTPBackend


class UnverifiedSSLEmailBackend(DjangoSMTPBackend):
    """
    SMTP backend that accepts self-signed SSL certificates.

    WARNING: Only use in development! In production, use proper SSL certificates
    with the standard Django SMTP backend.

    This backend disables SSL certificate verification, which makes it vulnerable
    to man-in-the-middle attacks. It's designed for dev environments where you
    control the mail server and use self-signed certificates.
    """

    def open(self):
        """
        Open connection with unverified SSL context.

        Overrides parent to use unverified SSL context for self-signed certs.
        """
        if self.connection:
            # Already have a connection
            return False

        connection_params = {'timeout': self.timeout}
        if self.ssl_keyfile:
            connection_params['keyfile'] = self.ssl_keyfile
        if self.ssl_certfile:
            connection_params['certfile'] = self.ssl_certfile

        if self.use_ssl:
            # Create unverified SSL context (accepts self-signed certs)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connection_params['context'] = ssl_context
            self.connection = smtplib.SMTP_SSL(
                self.host, self.port, **connection_params
            )
        else:
            self.connection = smtplib.SMTP(
                self.host, self.port, **connection_params
            )

            if self.use_tls:
                # Create unverified SSL context for STARTTLS too
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                self.connection.ehlo()
                self.connection.starttls(context=ssl_context)
                self.connection.ehlo()

        if self.username and self.password:
            self.connection.login(self.username, self.password)

        return True
