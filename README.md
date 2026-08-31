[![Dynamic DevOps Roadmap](https://img.shields.io/badge/Dynamic_DevOps_Roadmap-559e11?style=for-the-badge&logo=Vercel&logoColor=white)](https://devopsroadmap.io/getting-started/)
[![Community](https://img.shields.io/badge/Join_Community-%23FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://newsletter.devopsroadmap.io/subscribe)
[![Telegram Group](https://img.shields.io/badge/Telegram_Group-%232ca5e0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/DevOpsHive/985)
[![Fork on GitHub](https://img.shields.io/badge/Fork_On_GitHub-%2336465D?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DevOpsHiveHQ/devops-hands-on-project-hivebox/fork)

# HiveBox - DevOps End-to-End Hands-On Project

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox" style="display: block; padding: .5em 0; text-align: center;">
    <img alt="HiveBox - DevOps End-to-End Hands-On Project" border="0" width="90%" src="https://devopsroadmap.io/img/projects/hivebox-devops-end-to-end-project.png" />
  </a>
</p>

> [!CAUTION]
> **[Fork](https://github.com/DevOpsHiveHQ/devops-hands-on-project-hivebox/fork)** this repo, and create PRs in your fork, **NOT** in this repo!

> [!TIP]
> If you are looking for the full roadmap, including this project, go back to the [getting started](https://devopsroadmap.io/getting-started) page.

This repository is the starting point for [HiveBox](https://devopsroadmap.io/projects/hivebox/), the end-to-end hands-on project.

You can fork this repository and start implementing the [HiveBox](https://devopsroadmap.io/projects/hivebox/) project. HiveBox project follows the same Dynamic MVP-style mindset used in the [roadmap](https://devopsroadmap.io/).

The project aims to cover the whole Software Development Life Cycle (SDLC). That means each phase will cover all aspects of DevOps, such as planning, coding, containers, testing, continuous integration, continuous delivery, infrastructure, etc.

Happy DevOpsing ♾️

## Before you start

Here is a pre-start checklist:

- ⭐ <a target="_blank" href="https://github.com/DevOpsHiveHQ/dynamic-devops-roadmap">Star the **roadmap** repo</a> on GitHub for better visibility.
- ✉️ <a target="_blank" href="https://newsletter.devopsroadmap.io/subscribe">Join the community</a> for the project community activities, which include mentorship, job posting, online meetings, workshops, career tips and tricks, and more.
- 🌐 <a target="_blank" href="https://t.me/DevOpsHive/985">Join the Telegram group</a> for interactive communication.

## Preparation

- [Create GitHub account](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) (if you don't have one), then [fork this repository](https://github.com/DevOpsHiveHQ/devops-hands-on-project-hivebox/fork) and start from there.
- [Create GitHub project board](https://docs.github.com/en/issues/planning-and-tracking-with-projects/creating-projects/creating-a-project) for this repository (use `Kanban` template).
- Each phase should be presented as a pull request against the `main` branch. Don’t push directly to the main branch!
- Document as you go. Always assume that someone else will read your project at any phase.
- You can get senseBox IDs by checking the [openSenseMap](https://opensensemap.org/) website. Use 3 senseBox IDs close to each other (you can use the following [5eba5fbad46fb8001b799786](https://opensensemap.org/explore/5eba5fbad46fb8001b799786), [5c21ff8f919bf8001adf2488](https://opensensemap.org/explore/5c21ff8f919bf8001adf2488), and [5ade1acf223bd80019a1011c](https://opensensemap.org/explore/5ade1acf223bd80019a1011c)). Just copy the IDs, you will need them in the next steps.

<br/>
<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://img.shields.io/badge/Get_Started_Now-559e11?style=for-the-badge&logo=Vercel&logoColor=white" />
  </a><br/>
</p>

---

## Implementation

### Project Approach

HiveBox will be developed using kanban. Work will be reflected as github issues and tracked on the HiveBox kanban board. 

### Initial SenseBox IDs

- '5eba5fbad46fb8001b799786'
- '5c21ff8f919bf8001adf2488'
- '5ade1acf223bd80019a1011c'

### Phase 2: Application

Initial HiveBox application is version v0.0.1. It prints the current application version and then exits. 

#### Build Docker Image

```shell
docker build -t hivebox:v0.0.1 .
```

#### Run Container

```shell
docker run --rm hivebox:v0.0.1
```

Expected output:

```text
v0.0.1
```

#### Verify the output

Check to ensure app exited:

```text
echo $?
```

Expected output:

```text
0
```

### Phase 3

HiveBox is a FastAPI application that retrieves environmental sensor data from the openSenseMap API.

#### API endpoints

##### `GET /version`

Returns the deployed application version.

Example:

```json
{
  "version": "v0.0.1"
}
```

##### `GET /temperature`

Returns the average of the configured senseBoxes' current Celsius temperature measurements.

Only measurements from the previous hour are included.

Example:

```json
{
  "average": 21.4,
  "unit": "°C",
  "measurements": 3
}
```

If no current measurements are available, the endpoint returns HTTP status `503`:

```json
{
  "detail": "No temperature measurements from the last hour"
}
```

#### Local setup

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

#### Run the application

Start the FastAPI application with Uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Test the version endpoint:

```bash
curl -sS http://127.0.0.1:8000/version | jq
```

Test the temperature endpoint:

```bash
curl -sS http://127.0.0.1:8000/temperature | jq
```

The temperature request may take some time because it depends on the external openSenseMap API.

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Stop the application by pressing `Ctrl+C`.

#### Run the unit tests

Run pytest from the repository root:

```bash
python3 -m pytest -v
```

The unit tests use controlled sample data instead of contacting the live openSenseMap API. This keeps the tests predictable and prevents them from failing when the external API is slow or unavailable.

#### Run Pylint

Check the Python code:

```bash
pylint app.py tests
```

#### Run Hadolint

Check the Dockerfile:

```bash
docker run --rm -i hadolint/hadolint:v2.14.0 < Dockerfile
```

#### Build the Docker image

```bash
docker build -t hivebox:v0.0.1 .
```

#### Run the Docker container

```bash
docker run --rm --publish 8000:8000 hivebox:v0.0.1
```

The application is available at:

```text
http://127.0.0.1:8000
```

Open another terminal to test the running container:

```bash
curl -sS http://127.0.0.1:8000/version | jq
```

Stop the container by pressing `Ctrl+C` in the terminal where it is running.

#### Continuous integration

The GitHub Actions CI pipeline runs whenever a pull request targets the `main` branch.

The pipeline:

1. Installs Python and the project dependencies.
2. Checks the Python code with Pylint.
3. Runs the unit tests with pytest.
4. Checks the Dockerfile with Hadolint.
5. Builds the Docker image.
6. Starts the container.
7. Verifies that `/version` returns `v0.0.1`.

### Phase 4 
#### Adds temperature environment variables, status fields, prometheus, and kubernetes

#### API endpoints

##### `Updated GET /version`

Returns the updated deployed application version.

Example:

```json
{
  "version": "v0.1.0"
}
```

HiveBox reads a "status" field based on the temperature average value.

    Less than 10: Too Cold
    Between 11-36: Good
    More than 37: Too Hot


#### Prometheus
`/metrics` returns prometheus metrics about the app


#### Containers
Created a KIND config to run with Ingress-Nginx
- config file found under kind/kind-config.yaml


Created and deployed HiveBox app using Kubernetes core manifests


#### CI
Ran SonarQube for code quality, security, and static analysis

Ran Terrascan for Kubernetes manifest misconfigurations and vulnerabilities

#### CD
Created a GitHub Actions workflow for CD under: `.github/workflows/cd.yml`
Added step to release by pushing a versioned Docker image to a container registry