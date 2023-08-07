## Developing with Visual Studio Code + devcontainer

The easiest way to get started with custom integration development is to use Visual Studio Code with devcontainers. This approach will create a preconfigured development environment with all the tools you need.

**Prerequisites**

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- Docker
  -  For Linux, macOS, or Windows 10 Pro/Enterprise/Education use the [current release version of Docker or Podman](https://docs.docker.com/install/)
  -   Windows 10 Home requires [WSL 2](https://docs.microsoft.com/windows/wsl/wsl2-install) and the current Edge version of Docker Desktop (see instructions [here](https://docs.docker.com/docker-for-windows/wsl-tech-preview/)). This can also be used for Windows Pro/Enterprise/Education.
- [Visual Studio code](https://code.visualstudio.com/)
- [Remote - Containers (VSC Extension)][extension-link]

[More info about requirements and devcontainer in general](https://code.visualstudio.com/docs/remote/containers#_getting-started)

[extension-link]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers

**Getting started:**

1. Fork the repository.
2. Clone the repository to your computer.
3. Copy the devcontainer-template.json to .devcontainer.json in the root directory
4. Edit the .devcontainer.json depending on podman or docker
5. Re-Open the repository using Visual Studio code.

NOTE: Podman requires additional setup to tell VS Code that you are using Podman and not Docker.

When you open this repository with Visual Studio code you are asked to "Reopen in Container", this will start the build of the container.

_If you don't see this notification, open the command palette and select `Remote-Containers: Reopen Folder in Container`._

### Step by Step debugging

You can run the Unit Tests or if you open the Main Folder you can use Run->Start Debugging to debug the main folder, but to do this effectively you need to have a launch.json file in your .vscode folder.  this is an example for debuging using the main command line function.

This will also disable coverage reporting in the testing within VS Code.


```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Tests",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "purpose": [
                "debug-test"
            ],
            "console": "integratedTerminal",
            "justMyCode": true,
            "env": {
                "PYTEST_ADDOPTS": "--no-cov"
            },
            "args": [
                "get",
                "--user",
                "demo",
                "--password",
                "mt-demo",
                "--api-ver",
                "v1",
                "data",
                "0",
                "1"
            ]
        },
        {
            "name": "Python: Attach using Process Id",
            "type": "python",
            "request": "attach",
            "processId": "${command:pickProcess}",
            "justMyCode": true
        }
    ]
}

