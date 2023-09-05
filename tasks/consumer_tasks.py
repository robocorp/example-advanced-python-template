"""This module provides for the Consumer task
entry point. This utilizes the robocorp.tasks framework as 
well as the robocorp.log facility to log additional information.
"""
from robocorp import log, workitems
from robocorp.tasks import task

from . import _setup_log, _get_secret

from libs.web.swaglabs import Swaglabs


INPUT_FILE_NAME = "orders.csv"


def _process_order(swaglabs: Swaglabs, work_item: workitems.Input) -> None:
    """Processes an order (a single work item).

    Args:
        swaglabs (Swaglabs): The Swaglabs library instance, which should
            already be logged in. Providing this from a context manager
            ensures that the library is logged out when the context
            manager exits.
        work_item (workitems.Input): The order to process. Providing this
            from a context manager ensures that the work item is marked
            as completed when the context manager exits.
    """
    log.info(f"Processing work item {work_item.id}")
    # Return to the main page with an empty cart.
    swaglabs.clear_cart()
    swaglabs.go_to_order_screen()
    payload = work_item.payload
    assert isinstance(payload, dict)
    set_items = set(payload.get("Items", []))
    log.info(f"Ordering {len(set_items)} items for {payload.get('Name')}")
    for item in set_items:
        swaglabs.add_item_to_cart(item)
    log.info(f"Submitting order for work item {work_item.id}")
    first_name = payload.get("Name", "").split(" ")[0]
    last_name = payload.get("Name", "").split(" ")[1]
    order_number = swaglabs.submit_order(first_name, last_name, payload.get("Zip", ""))
    log.info(f"Order submitted for work item {work_item.id}")

    # Create work items for reporter step.
    output = work_item.create_output()
    output.payload = {
        "Name": payload.get("Name"),
        "Items": list(set_items),
        "OrderNumber": order_number,
    }
    output.save()


@task
def consumer():
    _setup_log()
    log.info("Consumer task started.")
    credentials = _get_secret("swaglabs")
    with Swaglabs(
        credentials["username"], credentials["password"], credentials["url"]
    ) as swaglabs:
        # This loop is the most important in the Consumer.
        for work_item in workitems.inputs:
            with work_item:
                _process_order(swaglabs, work_item)
            log.info(f"Work item was released with state '{work_item.state}'.")
