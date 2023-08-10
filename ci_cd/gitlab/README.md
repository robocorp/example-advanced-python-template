# GitLab Pipeline for Python-based Automations

This section of the example explains how to setup a GitLab pipeline which will run your unit tests when Pull Requests are opened against the `main`, `test`, and `dev` branches. There is also a pipeline which can deploy to Control Room if you prefer to use that instead of the [Robocorp Control Room GitLab integration](https://robocorp.com/docs/control-room/technical-architecture-and-security/version-control). This readme describes how you would set up your environments within GitLab to automatically utilize the correct pipeline and workspace within Control Room.

This readme assumes the following:

* A Robocorp Control Room Organization exists with three different workspaces with the following names:
    * `Production`: which we will link with the `main` branch
    * `Test`: which we will link with the `test` branch
    * `Dev`: which we will link with the `dev` branch
* An Ubuntu-based runner exists within your GitLab instance which can execute the script

## Creating Environments

