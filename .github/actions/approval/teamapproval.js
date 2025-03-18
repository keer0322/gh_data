const core = require("@actions/core");
const github = require("@actions/github");

async function run() {
    try {
        const token = core.getInput("github-token", { required: true });
        const teamSlug = core.getInput("team-slug", { required: true }); // Team slug (e.g., "devops")
        const org = core.getInput("org", { required: true }); // GitHub organization name
        const issueTitle = core.getInput("issue-title");
        const issueBody = core.getInput("issue-body");
        const octokit = github.getOctokit(token);
        const { context } = github;
        const workflowTriggerUser = context.actor;

        // Get team members
        const { data: teamMembers } = await octokit.rest.teams.listMembersInOrg({
            org,
            team_slug: teamSlug
        });

        const teamApprovers = teamMembers.map(member => member.login);
        core.info(`Team Members: ${teamApprovers.join(", ")}`);

        // Create an issue for manual approval
        const { data: issue } = await octokit.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: issueTitle,
            body: `${issueBody}\n\n✅ **Approvers:** ${teamApprovers.join(", ")}\n\n❗ **${workflowTriggerUser} cannot approve this workflow.**\n\n💬 **To approve, comment:**\n\`approve <input>\` (e.g., \`approve v1.2.3\`)`,
            labels: ["manual-approval"]
        });

        core.info(`Approval issue created: ${issue.html_url}`);

        let approved = false;
        let userInput = "";

        while (!approved) {
            await new Promise((resolve) => setTimeout(resolve, 60 * 1000)); // Wait 1 min

            const { data: comments } = await octokit.rest.issues.listComments({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number
            });

            for (const comment of comments) {
                const match = comment.body.trim().match(/^approve\s+(.+)/i); // Extract input
                if (
                    match &&
                    teamApprovers.includes(comment.user.login) && // Must be in the team
                    comment.user.login !== workflowTriggerUser // Executor cannot approve
                ) {
                    approved = true;
                    userInput = match[1]; // Capture input
                    core.info(`Approval received from ${comment.user.login}: ${userInput}`);
                    break;
                }
            }

            core.info("Waiting for approval...");
        }

        core.setOutput("approved", "true");
        core.setOutput("user-input", userInput);
        core.info(`Approval confirmed with input: ${userInput}`);

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
