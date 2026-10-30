# Desktop identity

This Java 21 desktop component implements HU-08 / DSK-03a. It creates an
ECDSA P-256 key pair, stores the private key and self-signed certificate in
`%ProgramData%\InternetCafe\machine-identity.p12`, and exposes the public key as an EC P-256 JWK
with its RFC 7638 SHA-256 thumbprint. Existing identities are loaded rather than replaced.

On Windows, the module sets an ACL granting full control to the directory/file owner and Local
System, and to Administrators when the group is resolvable. The `Users` group gets read-only
access so the desktop can use the identity under a standard account; if Windows cannot resolve
that group, read-only access is granted to Authenticated Users instead. The JWK contains only
`crv`, `kty`, `x`, and `y`; the private key remains in the PKCS12 store. The keystore password is
supplied by the caller and is not embedded in the source.

Run the unit tests from this directory with `gradle test`.

## QR rotation (DSK-05a)

The QR screen requests a new challenge from `POST /api/v1/machine/challenges`
a few seconds before `rotate_after_s` elapses (default margin: 5 seconds), so the
code on screen stays valid. On success the QR image is regenerated and the
countdown restarts from the new `rotate_after_s`. Backend errors are retried a
limited number of times (default: 3); the last valid QR stays visible until it
expires, and the scheduler does not loop forever. Closing the QR screen stops
the rotation thread. Challenge URLs and tokens are not written to logs.
