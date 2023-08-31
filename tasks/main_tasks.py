"""This module provides for the primary Production and Consumer task
entry points. This utilizes the robocorp.tasks framework as 
well as the robocorp.log facility to log additional information.
"""
import json
from pathlib import Path

from robocorp import log, workitems, vault, storage, excel
from robocorp.tasks import task
from robocorp.excel import tables

from . import ARTIFACTS_DIR, DEVDATA, _setup_log

from web.swaglabs import Swaglabs


INPUT_FILE_NAME = "orders.csv"


### PRODUCER FUNCTIONS ###
@task
def producer():
    _setup_log()
    log.info("Producer task started.")

    # Often times, a producer bot needs to go get work items from
    # some report, but in this example, we utilize the work item
    # file to create child work items.
    work_item = workitems.inputs.current
    destination_path = Path(ARTIFACTS_DIR) / INPUT_FILE_NAME
    input_filepath = work_item.get_file(INPUT_FILE_NAME, destination_path)
    log.info(f"Reading orders from {input_filepath}")
    # this call will likely be modified soon with updates to robocorp-excel.
    table = tables.Tables().read_table_from_csv(
        str(input_filepath), encoding="utf-8-sig"
    )
    customers = table.group_by_column("Name")
    log.info(f"Found {len(table)} rows in the worksheet. Creating work items.")
    for customer in customers:
        assert isinstance(customer, excel.Table)
        log.info(f"Creating work items for {customer.get_column('Name')[0]}")
        work_item_vars = {
            "Name": customer.get_column("Name")[0],
            "Zip": customer.get_column("Zip")[0],
            "Items": [],
        }
        for row in customer:
            work_item_vars["Items"].append(row["Item"])
        workitems.outputs.create(work_item_vars, save=True)
    log.info("Producer task completed.")


### CONSUMER FUNCTIONS ###
def _get_secret(system: str) -> vault.SecretContainer:
    """Gets the appropriate secret from the vault based on
    the system name and the mapping within the Control Room
    asset storage. This is a simple example of how you can
    use the asset storage system to configure your bots.

    In this example, the mapping should be stored in the asset storage
    as a JSON object named "system_credential_index" with the following
    structure:
        {
            "system_name": "secret_name",
            ...
        }

    For the sake of this example, this function loads a mapping from
    a file named "system_credential_index.json" in the devdata directory,
    but if you are using the Control Room, you can create this asset
    in your Workspace and it will use that instead.
    """
    try:
        mapping = storage.get_json("system_credential_index")
    except (storage.AssetNotFound, RuntimeError, KeyError):
        # If the asset is not found, use the local file instead.
        with (DEVDATA / "system_credential_index.json").open() as file:
            mapping = json.load(file)
    try:
        assert isinstance(mapping, dict)
        secret_name = mapping[system]
    except KeyError:
        raise KeyError(f"System {system} not found in mapping.")
    except (TypeError, AssertionError):
        raise TypeError("Mapping is not a dictionary-like JSON object.")
    assert isinstance(secret_name, str)
    return vault.get_secret(secret_name)


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
        for work_item in workitems.inputs:
            with work_item:
                _process_order(swaglabs, work_item)
            log.info(f"Work item was released with state '{work_item.state}'.")
