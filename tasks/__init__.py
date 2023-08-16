"""This package provides for the primary Production and Consumer task
entry points. This utilizes the robocorp.tasks framework as 
well as the robocorp.log facility to log additional information.
"""
import os
from pathlib import Path

from robocorp import log, workitems, vault, storage
from robocorp.tasks import task

# The Excel library may be ported to `robocorp` in the future, which
# would allow for a more consistent experience. For now, we use the
# rpaframework library.
from RPA.Excel.Files import Files

from web.swaglabs import Swaglabs

ARTIFACTS_DIR = os.getenv("ROBOT_ARTIFACTS", "output")


### SHARED FUNCTIONS ###
def _setup_log_from_environ() -> None:
    """Tries to use the LOG_LEVEL environment variable to set the log level.
    If the value is not valid, the default is "info".
    """
    log_level = os.getenv("LOG_LEVEL", "info")
    try:
        log_level = log.FilterLogLevel(log_level)
    except ValueError:
        log_level = log.FilterLogLevel.INFO
    log.setup_log(output_log_level=log_level)


### PRODUCER FUNCTIONS ###
@task
def producer():
    _setup_log_from_environ()
    excel = Files()
    log.info("Producer task started.")
    # utilize work item file to create child work items
    # Often times, a producer bot needs to go get work items from
    # some report, but in this example, we utilize the work item
    # file to create child work items.
    work_item = workitems.inputs.current
    destination_path = Path(ARTIFACTS_DIR) / "orders.xlsx"
    input_filepath = work_item.get_file("orders.xlsx", destination_path)
    excel.open_workbook(str(input_filepath))
    table = excel.read_worksheet_as_table(header=True)
    customers = table.group_by_column("Name")
    log.info(f"Found {len(table)} rows in the worksheet. Creating work items.")
    for customer in customers:
        log.info(f"Creating work items for {customer[0]['Name']}")
        work_item_vars = {
            "Name": customer[0]["Name"],
            "Zip": customer[0]["Zip"],
            "Items": [],
        }
        for row in table:
            work_item_vars["Items"].append(row["Item"])
        workitems.outputs.create(work_item_vars)
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
    """
    mapping = storage.get_json("system_credential_index")
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
    swaglabs.open()
    swaglabs.clear_cart()
    swaglabs.go_to_order_screen()
    log.info(f"Adding items to cart for work item {work_item.id}")
    payload = work_item.payload
    assert isinstance(payload, dict)
    items = payload.get("Items", [])
    for item in items:
        swaglabs.add_item_to_cart(item)
    log.info(f"Submitting order for work item {work_item.id}")
    first_name = payload.get("Name", "").split(" ")[0]
    last_name = payload.get("Name", "").split(" ")[1]
    swaglabs.submit_order(first_name, last_name, payload.get("Zip", ""))
    log.info(f"Order submitted for work item {work_item.id}")


@task
def consumer():
    _setup_log_from_environ()
    log.info("Consumer task started.")
    credentials = _get_secret("swaglabs")
    with Swaglabs(
        credentials["username"], credentials["password"], credentials["url"]
    ) as swaglabs:
        for work_item in workitems.inputs:
            with work_item:
                _process_order(swaglabs, work_item)
