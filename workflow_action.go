package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"log"
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

// Get workflow files from a repo
func getWorkflowFiles(client *github.Client, repo *github.Repository) ([]*github.RepositoryContent, error) {
	contents, _, _, err := client.Repositories.GetContents(context.Background(), orgName, *repo.Name, ".github/workflows", nil)
	if err != nil {
		return nil, err
	}
	var workflows []*github.RepositoryContent
	for _, file := range contents {
		if strings.HasSuffix(*file.Name, ".yml") || strings.HasSuffix(*file.Name, ".yaml") {
			workflows = append(workflows, file)
		}
	}
	return workflows, nil
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
		fmt.Printf("Checking repo: %s\n", *repo.Name)
		workflows, err := getWorkflowFiles(client, repo)
		if err != nil {
			log.Printf("No workflows found for %s: %v", *repo.Name, err)
			continue
		}

		for _, file := range workflows {
			content, err := file.GetContent()
			if err != nil {
				log.Printf("Error reading %s: %v", *file.Path, err)
				continue
			}

			actions := extractActionsFromYaml(content)
			for _, action := range actions {
				actionSet[action] = struct{}{}
			}
		}
	}

	fmt.Println("\nAll Actions Used:")
	for action := range actionSet {
		fmt.Println(action)
	}
}
