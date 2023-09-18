"""This module shows how you can easily call tasks by name within
the `tasks` directory from within the robot.yaml file.
"""
from datetime import datetime

from robocorp import log, workitems
from robocorp.tasks import task

from . import ARTIFACTS_DIR, DEVDATA, _setup_log


@task
def reporter():
    _setup_log()
    log.info("Reporter task started.")

    # Reporters should generally be the last step in a Control Room
    # process and should have the setting "Start Only After all work
    # items from previous steps are either done or failed" set to true.
    # This will ensure that the reporter is only called once all of the
    # work items have been processed.
    results = []
    for work_item in workitems.inputs:
        with work_item:
            # This is a simple example of how you can pull out
            # information from the set of completed work items.
            log.info(f"Processing work item ID {work_item.id}")
            payload = work_item.payload
            assert isinstance(payload, dict)
            name = payload.get("Name", "")
            items = payload.get("Items", [])
            order_number = payload.get("OrderNumber", "")
            results.append(
                {
                    "name": name,
                    "order_length": len(items),
                    "order_number": order_number,
                }
            )

    # The results are saved as a single output work item as a final
    # output of the process. These outputs will be available in the
    # Control Room UI and in the future additional features may
    # be added to make it easier to work with the results. Currently,
    # one feature available is to receive this final output via webhook.
    #
    # Alternatively, you could save the results to a file or generate
    # an email or other notification.
    output = workitems.outputs.create()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output.payload = {"run_timestamp": timestamp, "results": results}
    output.save()
