package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

func getWorkflowRuns(repoOwner, repoName, workflowName, accessToken string) ([]map[string]interface{}, error) {
	url := fmt.Sprintf("https://api.github.com/repos/%s/%s/actions/workflows/%s/runs", repoOwner, repoName, workflowName)

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+accessToken)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var runs map[string]interface{}
	if err := json.Unmarshal(body, &runs); err != nil {
		return nil, err
	}

	return runs["workflow_runs"].([]map[string]interface{}), nil
}

func getWorkflowJobDetails(repoOwner, repoName string, runID int, accessToken string) ([]map[string]interface{}, error) {
	url := fmt.Sprintf("https://api.github.com/repos/%s/%s/actions/runs/%d/jobs", repoOwner, repoName, runID)

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+accessToken)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var jobs map[string]interface{}
	if err := json.Unmarshal(body, &jobs); err != nil {
		return nil, err
	}

	return jobs["jobs"].([]map[string]interface{}), nil
}

func main() {
	// Replace with your GitHub organization, repository, workflow, and access token
	repoOwner := "your_organization"
	repoName := "your_repository"
	workflowName := "your_workflow"
	accessToken := "your_access_token"

	workflowRuns, err := getWorkflowRuns(repoOwner, repoName, workflowName, accessToken)
	if err != nil {
		fmt.Println("Error fetching workflow runs:", err)
		os.Exit(1)
	}

	for _, run := range workflowRuns {
		runID := int(run["id"].(float64))
		jobDetails, err := getWorkflowJobDetails(repoOwner, repoName, runID, accessToken)
		if err != nil {
			fmt.Println("Error fetching job details:", err)
			os.Exit(1)
		}

		fmt.Printf("Workflow: %s, Run ID: %d\n", workflowName, runID)

		for _, job := range jobDetails {
			fmt.Printf("  - Job: %s\n", job["name"].(string))
		}
	}
}
