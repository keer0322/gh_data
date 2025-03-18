const core = require("@actions/core");
const github = require("@actions/github");

async function run() {
    try {
        const token = core.getInput("github-token", { required: true });
        const approvers = core.getInput("approvers").split(",");
        const issueTitle = core.getInput("issue-title");
        const issueBody = core.getInput("issue-body");
        const octokit = github.getOctokit(token);
        const { context } = github;

        // Create an issue for manual approval
        const { data: issue } = await octokit.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: issueTitle,
            body: `${issueBody}\n\nApprovers: ${approvers.join(", ")}`,
            labels: ["manual-approval"]
        });

        core.info(`Approval issue created: ${issue.html_url}`);

        // Poll for approval
        let approved = false;
        while (!approved) {
            await new Promise((resolve) => setTimeout(resolve, 60 * 1000)); // Wait 1 min

            const { data: comments } = await octokit.rest.issues.listComments({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number
            });

            approved = comments.some(comment =>
                approvers.includes(comment.user.login) &&
                comment.body.trim().toLowerCase() === "approve"
            );

            core.info("Waiting for approval...");
        }

        core.setOutput("approved", "true");
        core.info("Approval received! Proceeding...");

        // Close the issue after approval
        await octokit.rest.issues.update({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: issue.number,
            state: "closed"
        });

    } catch (error) {
        core.setFailed(`Error: ${error.message}`);
    }
}

run();
