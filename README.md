# Full Stack FastAPI Template

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3ATest" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test/badge.svg" alt="Test"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
    - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
    - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components.
    - 🤖 An automatically generated frontend client.
    - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.
    - 🦇 Dark mode support.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

### Dashboard Login

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Create User

[![API docs](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - User Settings

[![API docs](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## How To Use It

You can **just fork or clone** this repository and use it as is.

✨ It just works. ✨

### How to Use a Private Repository

If you want to have a private repository, GitHub won't allow you to simply fork it as it doesn't allow changing the visibility of forks.

But you can do the following:

- Create a new GitHub repo, for example `my-full-stack`.
- Clone this repository manually, set the name with the name of the project you want to use, for example `my-full-stack`:

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git my-full-stack
```

- Enter into the new directory:

```bash
cd my-full-stack
```

- Set the new origin to your new repository, copy it from the GitHub interface, for example:

```bash
git remote set-url origin git@github.com:octocat/my-full-stack.git
```

- Add this repo as another "remote" to allow you to get updates later:

```bash
git remote add upstream git@github.com:fastapi/full-stack-fastapi-template.git
```

- Push the code to your new repository:

```bash
git push -u origin master
```

### Update From the Original Template

After cloning the repository, and after doing changes, you might want to get the latest changes from this original template.

- Make sure you added the original repository as a remote, you can check it with:

```bash
git remote -v

origin    git@github.com:octocat/my-full-stack.git (fetch)
origin    git@github.com:octocat/my-full-stack.git (push)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (fetch)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (push)
```

- Pull the latest changes without merging:

```bash
git pull --no-commit upstream master
```

This will download the latest changes from this template without committing them, that way you can check everything is right before committing.

- If there are conflicts, solve them in your editor.

- Once you are done, commit the changes:

```bash
git merge --continue
```

### Configure

You can then update configs in the `.env` files to customize your configurations.

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

Read the [deployment.md](./deployment.md) docs for more details.

### Generate Secret Keys

Some environment variables in the `.env` file have a default value of `changethis`.

You have to change them with a secret key, to generate secret keys you can run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as password / secret key. And run that again to generate another secure key.

## How To Use It - Alternative With Copier

This repository also supports generating a new project using [Copier](https://copier.readthedocs.io).

It will copy all the files, ask you configuration questions, and update the `.env` files with your answers.

### Install Copier

You can install Copier with:

```bash
pip install copier
```

Or better, if you have [`pipx`](https://pipx.pypa.io/), you can run it with:

```bash
pipx install copier
```

**Note**: If you have `pipx`, installing copier is optional, you could run it directly.

### Generate a Project With Copier

Decide a name for your new project's directory, you will use it below. For example, `my-awesome-project`.

Go to the directory that will be the parent of your project, and run the command with your project's name:

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

If you have `pipx` and you didn't install `copier`, you can run it directly:

```bash
pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

**Note** the `--trust` option is necessary to be able to execute a [post-creation script](https://github.com/fastapi/full-stack-fastapi-template/blob/master/.copier/update_dotenv.py) that updates your `.env` files.

### Input Variables

Copier will ask you for some data, you might want to have at hand before generating the project.

But don't worry, you can just update any of that in the `.env` files afterwards.

The input variables, with their default values (some auto generated) are:

- `project_name`: (default: `"FastAPI Project"`) The name of the project, shown to API users (in .env).
- `stack_name`: (default: `"fastapi-project"`) The name of the stack used for Docker Compose labels and project name (no spaces, no periods) (in .env).
- `secret_key`: (default: `"changethis"`) The secret key for the project, used for security, stored in .env, you can generate one with the method above.
- `first_superuser`: (default: `"admin@example.com"`) The email of the first superuser (in .env).
- `first_superuser_password`: (default: `"changethis"`) The password of the first superuser (in .env).
- `smtp_host`: (default: "") The SMTP server host to send emails, you can set it later in .env.
- `smtp_user`: (default: "") The SMTP server user to send emails, you can set it later in .env.
- `smtp_password`: (default: "") The SMTP server password to send emails, you can set it later in .env.
- `emails_from_email`: (default: `"info@example.com"`) The email account to send emails from, you can set it later in .env.
- `postgres_password`: (default: `"changethis"`) The password for the PostgreSQL database, stored in .env, you can generate one with the method above.
- `sentry_dsn`: (default: "") The DSN for Sentry, if you are using it, you can set it later in .env.

## Automated Project Documentation and Task Management

This project includes a set of scripts to automate the generation of project documentation and the creation of development tasks. These scripts can significantly speed up the initial phases of a project by automatically creating:

-   **Product Requirements Document (PRD):** Generated from a high-level project description.
-   **Technical System Design (TSD):** Generated from the PRD.
-   **Technical Requirements Document (TRD):** Generated from the PRD.
-   **Development Tasks:** A detailed list of tasks and sub-tasks derived from the generated documentation.
-   **Gantt Chart:** An interactive Gantt chart to visualize the project timeline.
-   **Jira Tasks:** Automatically create tasks and sub-tasks in your Jira project.

For detailed instructions on how to use these automation scripts, please refer to the [documentation in the scripts directory](./backend/app/scripts/README.md).

## CI/CD Automation with Jira

Your project is configured with a comprehensive set of GitHub Actions workflows that automate the integration between your GitHub repository and your Jira project. These automations streamline your development process by keeping your Jira tickets synchronized with your code changes, pull requests, and branches.

Here's a detailed breakdown of each automation:

### 1. `jira-comment-on-push.yml`

**Purpose:** Automatically adds a comment to a Jira ticket every time a commit is pushed to any branch.

**How it works:**

1.  **Triggers on Push:** The workflow runs whenever a `git push` is detected.
2.  **Extracts Information:** It inspects the commit message to find one or more Jira ticket IDs (e.g., `PROJ-123`).
3.  **Posts to Jira:** If a Jira ID is found, it posts a comment to the corresponding ticket with the commit message, the author, and a direct link to the commit on GitHub.

**Benefit:** This keeps the Jira ticket updated with a real-time log of all the commits related to it, providing clear traceability from the task to the code.

### 2. `jira-link-on-pr-open.yml`

**Purpose:** Links a pull request to a Jira ticket and transitions the ticket to "In Review" when a PR is opened or edited.

**How it works:**

1.  **Triggers on Pull Request:** The workflow is activated when a pull request is opened or its title/body is edited.
2.  **Finds Jira ID:** It searches the pull request's title and body for a Jira ticket ID.
3.  **Links PR to Jira:** If an ID is found, it posts a comment on the Jira ticket with a link to the pull request.
4.  **Transitions Ticket:** It then automatically transitions the Jira ticket to your "In Review" status (or a similar status you've configured), signaling that the work is ready for review.

**Benefit:** This automation saves developers the manual step of updating the Jira ticket's status and ensures that reviewers have a direct link from the Jira ticket to the code they need to review.

### 3. `jira-transition-on-branch-create.yml`

**Purpose:** Transitions a Jira ticket to "In Progress" as soon as a developer creates a new branch for that ticket.

**How it works:**

1.  **Triggers on Branch Creation:** The workflow runs when a new branch is created in the repository.
2.  **Extracts Jira ID from Branch Name:** It expects the branch name to contain the Jira ticket ID (e.g., `feature/PROJ-123-new-login-flow`).
3.  **Updates Jira:** If an ID is found, it posts a comment to the Jira ticket with a link to the new branch and transitions the ticket to "In Progress."

**Benefit:** This provides immediate visibility in Jira that work has started on a task, without the developer having to manually update the ticket.

### 4. `jira-transition-on-pr-merge.yml`

**Purpose:** Transitions a Jira ticket to "Done" when a pull request is merged.

**How it works:**

1.  **Triggers on PR Merge:** The workflow is activated when a pull request is merged.
2.  **Finds Jira ID:** It searches for the Jira ticket ID in the branch name, PR title, and PR body.
3.  **Posts Merge Info:** It posts a comment to the Jira ticket with a link to the merge commit, confirming that the code has been integrated.
4.  **Closes Ticket:** It then automatically transitions the Jira ticket to your "Done" status (or a similar status), marking the task as complete.

**Benefit:** This closes out the development loop automatically, ensuring that the Jira board accurately reflects the state of your project without any manual intervention.

In summary, these CI/CD automations create a seamless and efficient workflow between your code repository and your project management tool. They reduce administrative overhead, improve communication, and provide a clear and consistent record of your development process.

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.

## Release Notes

Check the file [release-notes.md](./release-notes.md).

## License

The Full Stack FastAPI Template is licensed under the terms of the MIT license.
