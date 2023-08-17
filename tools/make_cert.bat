@echo off
echo Generating a self-signed SSL certificate and private key...
openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -days 365 -out server.crt -subj "/C=US/ST=NC/L=Chcowinity/O=CompAces/OU=Dev/CN=localhost"
echo Certificate and private key generated successfully!
pause
