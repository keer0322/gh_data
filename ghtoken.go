package main

import (
	"context"
	"crypto/rsa"
	"crypto/x509"
	"encoding/base64"
	"encoding/pem"
	"fmt"
	"log"
	"time"

	"github.com/dgrijalva/jwt-go/v4"
)

const (
	githubAppID       = "YOUR_APP_ID"          // Replace with your GitHub App ID
	organizationName  = "YOUR_ORG_NAME"        // Replace with your organization name
	base64EncodedKey  = "YOUR_BASE64_ENCODED_PRIVATE_KEY" // Replace with your Base64 encoded private key
)

// LoadPrivateKeyFromBase64 loads a private RSA key from a Base64 encoded string
func LoadPrivateKeyFromBase64(encodedKey string) (*rsa.PrivateKey, error) {
	// Decode the base64 encoded string
	keyData, err := base64.StdEncoding.DecodeString(encodedKey)
	if err != nil {
		return nil, fmt.Errorf("failed to decode base64 string: %v", err)
	}

	// Decode the PEM block
	block, _ := pem.Decode(keyData)
	if block == nil || block.Type != "RSA PRIVATE KEY" {
		return nil, fmt.Errorf("failed to decode PEM block containing private key")
	}

	// Parse the RSA private key
	privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse RSA private key: %v", err)
	}

	return privateKey, nil
}

// GenerateJWT generates a signed JWT token using GitHub App ID and private key
func GenerateJWT(appID string, privateKey *rsa.PrivateKey) (string, error) {
	// JWT expiration time (10 minutes is the maximum GitHub allows)
	expirationTime := time.Now().Add(10 * time.Minute)
	claims := jwt.MapClaims{
		"iat": time.Now().Unix(),
		"exp": expirationTime.Unix(),
		"iss": appID,
	}

	token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
	signedToken, err := token.SignedString(privateKey)
	if err != nil {
		return "", err
	}

	return signedToken, nil
}

// The rest of the code remains the same as before

func main() {
	// Load private key from base64 string
	privateKey, err := LoadPrivateKeyFromBase64(base64EncodedKey)
	if err != nil {
		log.Fatalf("Failed to load private key: %v", err)
	}

	// Generate JWT
	jwtToken, err := GenerateJWT(githubAppID, privateKey)
	if err != nil {
		log.Fatalf("Failed to generate JWT: %v", err)
	}

	// Call GetInstallationToken here to use the generated jwtToken as before

	fmt.Printf("Generated JWT Token: %s\n", jwtToken)
}
