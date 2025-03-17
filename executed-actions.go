package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/google/go-github/v56/github"
	"golang.org/x/oauth2"
	"gopkg.in/yaml.v3"
)

const (
	githubToken = "your_github_token"
	orgName     = "your_org_name"
)

// Workflow structure to parse YAML
type Workflow struct {
	Jobs map[string]struct {
		Steps []struct {
			Uses string `yaml:"uses"`
		} `yaml:"steps"`
	} `yaml:"jobs"`
}

// Get all repositories in the organization
func getOrgRepos(client *github.Client) ([]*github.Repository, error) {
	var allRepos []*github.Repository
	opt := &github.RepositoryListByOrgOptions{Type: "all", ListOptions: github.ListOptions{PerPage: 50}}

	for {
		repos, resp, err := client.Repositories.ListByOrg(context.Background(), orgName, opt)
		if err != nil {
			return nil, err
		}
		allRepos = append(allRepos, repos...)
		if resp.NextPage == 0 {
			break
		}
		opt.Page = resp.NextPage
	}

	return allRepos, nil
}

// Get workflow runs for a repo
func getWorkflowRuns(client *github.Client, repo *github.Repository) ([]*github.WorkflowRun, error) {
	opt := &github.ListWorkflowRunsOptions{ListOptions: github.ListOptions{PerPage: 50}}
	runs, _, err := client.Actions.ListRepositoryWorkflowRuns(context.Background(), orgName, *repo.Name, opt)
	if err != nil {
		return nil, err
	}
	return runs.WorkflowRuns, nil
}

// Get workflow content from a past run
func getWorkflowContent(client *github.Client, repo *github.Repository, workflowID int64) (string, error) {
	workflow, _, err := client.Actions.GetWorkflowByID(context.Background(), orgName, *repo.Name, workflowID)
	if err != nil {
		return "", err
	}

	content, _, _, err := client.Repositories.GetContents(context.Background(), orgName, *repo.Name, *workflow.Path, nil)
	if err != nil {
		return "", err
	}

	decodedContent, err := base64.StdEncoding.DecodeString(*content.Content)
	if err != nil {
		return "", err
	}

	return string(decodedContent), nil
}

// Extract actions from workflow file
func extractActionsFromYaml(yamlContent string) []string {
	var workflow Workflow
	err := yaml.Unmarshal([]byte(yamlContent), &workflow)
	if err != nil {
		log.Printf("Error parsing YAML: %v", err)
		return nil
	}

	var actions []string
	for _, job := range workflow.Jobs {
		for _, step := range job.Steps {
			if step.Uses != "" {
				actions = append(actions, step.Uses)
			}
		}
	}
	return actions
}

func main() {
	ctx := context.Background()
	ts := oauth2.StaticTokenSource(&oauth2.Token{AccessToken: githubToken})
	tc := oauth2.NewClient(ctx, ts)
	client := github.NewClient(tc)

	repos, err := getOrgRepos(client)
	if err != nil {
		log.Fatalf("Error fetching repositories: %v", err)
	}

	actionSet := make(map[string]struct{})

	for _, repo := range repos {
		fmt.Printf("Checking executed workflows in repo: %s\n", *repo.Name)
		runs, err := getWorkflowRuns(client, repo)
		if err != nil {
			log.Printf("No workflow runs found for %s: %v", *repo.Name, err)
			continue
		}

		for _, run := range runs {
			content, err := getWorkflowContent(client, repo, run.GetWorkflowID())
			if err != nil {
				log.Printf("Error fetching workflow content for %s: %v", *repo.Name, err)
				continue
			}

			actions := extractActionsFromYaml(content)
			for _, action := range actions {
				actionSet[action] = struct{}{}
			}
		}
	}

	fmt.Println("\nAll Actions Used in Executed Workflows:")
	for action := range actionSet {
		fmt.Println(action)
	}
}
