#!/bin/bash

echo "🔐 Generating SSL Certificate for Jim TTS Server"
echo "================================================"

# Get local IP
if [[ "$OSTYPE" == "darwin"* ]]; then
    LOCAL_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
else
    echo "Unable to detect OS. Please enter your IP manually:"
    read LOCAL_IP
fi

echo "Your local IP: $LOCAL_IP"
echo ""

# Create config file
cat > cert_config.cnf << EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
C = US
ST = State
L = City
O = JimTTS
OU = Development
CN = $LOCAL_IP

[v3_req]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = localhost
DNS.2 = *.local
IP.1 = $LOCAL_IP
IP.2 = 127.0.0.1
EOF

# Generate certificate
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout certs/key.pem \
    -out certs/cert.pem \
    -days 365 \
    -config cert_config.cnf \
    -extensions v3_req

echo ""
echo "✅ Certificate generated successfully!"
echo ""
echo "Files created:"
echo "  - certs/cert.pem (certificate)"
echo "  - certs/key.pem (private key)"
echo ""
echo "📱 For iOS:"
echo "  Visit https://$LOCAL_IP:8000/download-cert in Safari"
echo "  Install the certificate profile"
echo "  Trust it in Settings"
echo ""

# Clean up
rm cert_config.cnf
