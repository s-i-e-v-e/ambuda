#
# Github automation
#
import yaml


def __pull_request(branches):
    return {
        "branches": branches,
        "types": ["opened", "reopened", "synchronize"],
    }


def __ssh_exec(cmd):
    return [
        {
            "name": "Checkout",
            "uses": "actions/checkout@v4",
            "with": {"sparse-checkout": "\nar\nrunner"},
        },
        {
            "name": "Exec",
            "run": cmd,
            "env": {
                "SSH_HOST": "${{ secrets.SSH_HOST }}",
                "SSH_KEY": "${{ secrets.SSH_KEY }}",
                "SSH_KNOWN_HOSTS": "${{ secrets.SSH_KNOWN_HOSTS }}",
            },
        },
    ]


def __remote_job(cmd, needs=""):
    d = {
        "runs-on": "ubuntu-latest",
        "steps": __ssh_exec("\ncd ${{ github.workspace }}\n`pwd`ar remotely " + cmd),
    }
    if needs:
        d["needs"] = needs

    return d


def __job_pr_comment(needs):
    return {
        "name": "PR comment",  # This job only runs on PR open or reopen
        "needs": needs,
        "if": "${{ github.event.issue.pull_request.opened || github.event.issue.pull_request.reopened }}",
        "runs-on": "ubuntu-latest",
        "steps": [
            {
                "name": "Create comment",
                "uses": "peter-evans/create-or-update-comment@v2",
                "with": {
                    "issue-number": "${{ github.event.pull_request.number }}",
                    "body": "Your pull request is open. Reviewers will review the pullrequest at the earliest.",
                    "reactions": "+1",
                },
            }
        ],
    }


def __get_external_pr_open_workflow():
    return {
        "name": "Build image",
        "on": {"pull_request": __pull_request(["development", "main"])},
        "jobs": {
            "build": __remote_job("build"),
            "pr_commented": __job_pr_comment("build"),
        },
    }


def __get_release_pr_open_workflow():
    return {
        "name": "Build release image and deploy on staging environment",
        "on": {"workflow_dispatch": {}, "pull_request": __pull_request(["release"])},
        "jobs": {
            "build": __remote_job("build"),
            "run": __remote_job("run", needs="build"),
            "pr_commented": __job_pr_comment("build"),
        },
    }


def __get_release_pr_merged_workflow():
    return {
        "name": "Teardown staging deployment",
        "on": {
            "workflow_dispatch": {},
            "pull_request": {
                "branches": ["release"],
                "types": ["closed"],
            },
        },
        "jobs": {
            "destroy": __remote_job("destroy"),
            "comment_pr_merged": {
                "name": "PR comment",  # This job only runs on PR open or reopen
                "needs": "destroy",
                "if": "github.event.pull_request.merged == true",
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Create comment",
                        "uses": "peter-evans/create-or-update-comment@v2",
                        "with": {
                            "issue-number": "${{ github.event.pull_request.number }}",
                            "body": "Your pull request has been successfully merged.",
                            "reactions": "+1",
                        },
                    }
                ],
            },
        },
    }


def __dump_workflow(file, data):
    file_name = f".github/workflows/{file}"
    print(f"Writing {file_name}")
    doc = "##### AUTOMATICALLY GENERATED BY ambuda runner. DO NOT MODIFY #####"
    doc += "\n"
    doc += yaml.dump(data, default_flow_style=False)
    with open(file_name, "w") as yaml_file:
        yaml_file.write(doc)


def gh_generate_workflows(args):
    __dump_workflow("rel-pr-merged.yml", __get_release_pr_merged_workflow())
    __dump_workflow("rel-pr-open.yml", __get_release_pr_open_workflow())
    __dump_workflow("external-pr-open.yml", __get_external_pr_open_workflow())