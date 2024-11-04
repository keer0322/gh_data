package main

import (
	"context"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"github.com/dgrijalva/jwt-go/v4"
)

const (
	githubAppID        = "YOUR_APP_ID"             // Replace with your GitHub App ID
	organizationName   = "YOUR_ORG_NAME"           // Replace with your organization name
	privateKeyFilePath = "path/to/private-key.pem" // Path to your GitHub App private key file
)

// LoadPrivateKey loads a private RSA key from a PEM file
func LoadPrivateKey(filePath string) (*rsa.PrivateKey, error) {
	keyData, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(keyData)
	if block == nil || block.Type != "RSA PRIVATE KEY" {
		return nil, fmt.Errorf("failed to decode PEM block containing private key")
	}

	privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	if err != nil {
		return nil, err
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

// GetInstallationToken retrieves the installation access token for a GitHub App
func GetInstallationToken(jwtToken, orgName string) (string, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", fmt.Sprintf("https://api.github.com/orgs/%s/installation", orgName), nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+jwtToken)
	req.Header.Set("Accept", "application/vnd.github+json")

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("failed to get installation ID, status: %s", resp.Status)
	}

	// Parse the installation ID from the response
	var result struct {
		ID int `json:"id"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	// Now use the installation ID to request an access token
	req, err = http.NewRequest("POST", fmt.Sprintf("https://api.github.com/app/installations/%d/access_tokens", result.ID), nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+jwtToken)
	req.Header.Set("Accept", "application/vnd.github+json")

	resp, err = client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		return "", fmt.Errorf("failed to create access token, status: %s", resp.Status)
	}

	// Parse the access token from the response
	var tokenResult struct {
		Token string `json:"token"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&tokenResult); err != nil {
		return "", err
	}

	return tokenResult.Token, nil
}

func main() {
	// Load private key
	privateKey, err := LoadPrivateKey(privateKeyFilePath)
	if err != nil {
		log.Fatalf("Failed to load private key: %v", err)
	}

	// Generate JWT
	jwtToken, err := GenerateJWT(githubAppID, privateKey)
	if err != nil {
		log.Fatalf("Failed to generate JWT: %v", err)
	}

	// Get Installation Token
	installationToken, err := GetInstallationToken(jwtToken, organizationName)
	if err != nil {
		log.Fatalf("Failed to get installation token: %v", err)
	}

	fmt.Printf("Installation Access Token: %s\n", installationToken)
}
