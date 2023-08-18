# Example: Python - Complex Producer Consumer Reporter

This template leverages the new Python open-source framework [Robo](https://github.com/robocorp/robo), and [libraries](https://github.com/robocorp/robo#libraries) from the same project.

It provides the structure of a more complex Python project: building automation classes devoted to individual sites or components and combining them together into a task suite. The full suite includes the following features:

* Control Room-based JSON configuration provided via the Asset Storage solution
* A Pytest-based test suite targeting the automation classes, runnable via VSCode test extention, Robocorp Code extension, or `rcc` command in CI/CD.
* A `WebAutomationBase` class which can be extended, allowing for common functionalities between different automations.
* An internal Playwright locator dictionary with IDE support via the `prodict` package.

👉 After running the bot, check out the [*output/log.html*](./output/log.html) file.

This example has a significant amount of example code and comments and caution should be taken if you are adapting this directly into an automation for yourself.

> We recommended checking out the article "[Using work items](https://robocorp.com/docs/development-guide/control-room/work-items)" before diving in.

TODO: Add references to https://robocorp.com/docs/python/framework-intro
# TODO: UPDATE BELOW

## Tasks

The robot is split into two tasks, meant to run as separate steps in Control Room. The first task generates (produces) data, and the second one reads (consumes) and processes that data.

### The first task (the producer)

- Load the example Excel file from work item
- Split the Excel file into work items for the consumer

### The second task (the consumer)

> We recommended checking out the article "[Work item exception handling](https://robocorp.com/docs/development-guide/control-room/work-items#work-item-exception-handling)" before diving in.

- Loop through all work items in the queue and access the payloads from the previous step

## Local testing

For best experience to test the work items in this example we recommend using [our VS Code extensions](https://robocorp.com/docs/developer-tools/visual-studio-code). With the Robocorp Code extension you can simply run and [select the input work items](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features#using-work-items) to use, create inputs to simulate error cases, and so on.

## Extending the template

> The [producer-consumer](https://en.wikipedia.org/wiki/Producer%E2%80%93consumer_problem) model is not limited to two steps, it can continue so that the consumer generates further work items for the next step and so on.

Here's how you can add a third step, let's say a **reporter**, which will collect inputs from the previous one (the **consumer**) and generate a simple report with the previously created data. But first, see below what you need to add extra:

### The `reporter` step code

```python
@task
def reporter():
    """Collect and combine all the consumer outputs into a single report."""
    complete_orders = sum("complete" in item.payload["Order"] for item in workitems.inputs)
    print(f"Complete orders: {complete_orders}")
```

And as you can see, we collect some `"Order"` info from the previously created outputs, but we don't have yet such outputs created in the previous step (the **consumer**), so let's create them:

```python
@task
def consumer():
    """Process all the produced input Work Items from the previous step."""
    for item in workitems.inputs:
        try:
            ...
            workitems.outputs.create(payload={"Order": f"{name} is complete"})
            item.done()
        except KeyError as err:
            ...
```

The magic happens in this single line added right before the `item.done()` part: `workitems.outputs.create(payload={"Order": f"{name} is complete"})`. This creates a new output for every processed input with an `"Order"` field in the payload data. This is retrieved in the next step (**reporter**) through `item.payload["Order"]`.

### The `reporter` task entry

All good on the code side, but we need now to make this new task visible and runnable right in our [*robot.yaml*](./robot.yaml) configuration. So add this under `tasks:`:

```yaml
Reporter:
    shell: python -m robocorp.tasks run tasks.py -t reporter
```

Now you're good to go, just run the **consumer** again (so you'll have output items created), then run the newly introduced 3rd step called **reporter**.

![reporter log](./devdata/reporter-log.png)

----

🚀 Now, you can just get to writing.

For more information, do not forget to checkout the following:
* [Robocorp Documentation site](https://robocorp.com/docs)
* [Portal for more examples](https://robocorp.com/portal)
* [The robo GitHub repository](https://github.com/robocorp/robo)
