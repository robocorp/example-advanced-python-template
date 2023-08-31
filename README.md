# Example: Advanced Python Template

This template leverages the new Python open-source framework [Robo](https://github.com/robocorp/robo), and [libraries](https://github.com/robocorp/robo#libraries) from the same project.

It provides the structure of an advanced Python project: building automation classes devoted to individual sites or components and combining them together into a task suite. The full suite includes the following features:

* Control Room-based JSON configuration provided via the Asset Storage solution
* A Pytest-based test suite targeting the automation classes, runnable via VSCode test extention, Robocorp Code extension, or `rcc` command in CI/CD, with Robocorp Log integration (see output folder after tests run).
* A `WebAutomationBase` class which can be extended, allowing for common functionalities between different automations.
* An internal Playwright locator dictionary with IDE support via the `prodict` package.

👉 After running or testing the automation, check out the [*output/log.html*](./output/log.html) file.

This example has a significant amount of example code and comments and caution should be taken if you are adapting this directly into an automation for yourself.

> We recommended checking out the article "[Python Framework Introduction](https://robocorp.com/docs/python/framework-intro)" before diving in.

## Automation Classes

The example includes a package called `libs` which includes examples of an Automation Class designed to automation the saucedemo.com test website. It inherits an abstract base class that describes some common methods any web automation class should have, such as `login`. The abstract base class can be found in `libs/web/__init__.py`.

Includes in the `libs` package is an `errors` module that creates an inheritence tree based on the base `ApplicationException` and `BusinessException` classes defined in `robocorp-workitems`. By using these bases for all of the different errors within the automation, it is possible to automatically release errors from the automation to the Control Room without additional code.

## Tasks

The robot is split into three tasks, meant to run as separate steps in Control Room. The first task generates (produces) data, the second one reads (consumes) and processes that data, and the third reports on the orders submitted.

The overall task package provides examples of the following features:

- A package of task modules, each with one or more tasks in it.
- A set of shared functions/constants in the package root, including a shared function that configures logging to log to console based on an environment variable called "LOG_LEVEL".

### The first task (the producer)

The producer is located within the `tasks.main_tasks` module.

- Load the example CSV file from work item
- Split the Excel file into work items for the consumer
- Provides an example of how to create output workitems with no inputs.

### The second task (the consumer)

The consumer is located within the `tasks.main_tasks` module.

> We recommended checking out the article "[robocorp-workitems](https://robocorp.com/docs/python/robocorp/robocorp-workitems)" before diving in.

- Get credentials from the Control Room vault for the website based on a mapping within the Control Room Asset Storage
- Utilize the `Swaglabs` web automation class as a context manager to automatically handle login and logout to the website.
- Loop through all work items in the queue as context managers, automatically handling errors raised within the process so they are released to the Control Room and do not cause the bot to completely crash in the middle of processing a queue of work items.
- Process each work item as a set of orders for a specific customer.
- Create an output work item summarizing the results for the reporter.

### The third taks (the reporter)

The reporter is located within the `tasks.report` module.

The reporter step should be configured in the Control Room with the setting `Start Only After all work items from previous steps are either done or failed` because reporters generally are tasked with collating all work item results from previous steps.

- Loop through all Work Items in the queue, collecting key metrics from each.
- Create a final result output work item.

Final output work items can be used several ways within the Control Room, but primarily, they are useful as payloads in webhooks configured to be sent back to triggering systems at the end of 

## Local testing

For best experience to test the work items in this example we recommend using [our VS Code extensions](https://robocorp.com/docs/developer-tools/visual-studio-code). With the Robocorp Code extension you can simply run and [select the input work items](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features#using-work-items) to use, create inputs to simulate error cases, and so on.

Additionally, the Automation Classes are optimized to be tested via Pytest using the VS Code test extension, you can read more about how that works [here](https://code.visualstudio.com/docs/python/testing).

## CI/CD Pipelines

In addition to local testing, included in the example is a set of pipeline files written for the four major online repository/project hosting sites, see the [CI/CD readme](./ci_cd/README.md) for more information!

## Extending the template

> The [producer-consumer](https://en.wikipedia.org/wiki/Producer%E2%80%93consumer_problem) model is not limited to two steps, it can continue so that the consumer generates further work items for the next step and so on.

----

🚀 Now, you can just get to writing.

For more information, do not forget to checkout the following:
* [Robocorp Documentation site](https://robocorp.com/docs)
* [Portal for more examples](https://robocorp.com/portal)
* [The robo GitHub repository](https://github.com/robocorp/robo)
