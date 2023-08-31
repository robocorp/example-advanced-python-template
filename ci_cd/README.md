# Implementing CI/CD via Common Online Services

As part of most enterprise deployments, you may wish to implement a CI/CD pipeline that tests and deploys your code as you see fit. Included in this section is a set of pipeline files for the four major online code hosting and project hosting providers. Each pipeline file provides for both testing and deploying automatically when changes or pull requests are opened on specific branches.

> Read the [Robot Development Lifecycle documentation](https://robocorp.com/docs/development-guide/control-room/implementing-sdlc) before jumping in!

## GitHub

The Control Room provides a direct integration with GitHub cloud hosting that allows you to deploy changes to Control Room robots whenever a tracked branch changes... but if you need more control, or if you want to include testing, you should read more [here](./github/README.md)

## GitLab

The Control Room also allows for direct integration with GitLab cloud and self-hosted instances that can deploy changes to Robots based on changes to tracked branches, but again, if you need more control or testing, checkout [this readme](./gitlab/README.md).

## BitBucket

The Control Room does not yet offer a direct integration with BitBucket, but you can configure a full test and deploy pipeline by following [this guide](./bitbucket/README.md).

## Azure DevOps

Unfortunately, the Control Room does not have a direct integration for Azure DevOps yet either, but we've got you covered with [this doc](./azure_devops/README.md).