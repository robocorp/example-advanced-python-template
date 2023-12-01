"""This module provides for the producer task
entry point. This utilizes the robocorp.tasks framework as 
well as the robocorp.log facility to log additional information.
"""
from pathlib import Path

from robocorp import log, workitems, excel
from robocorp.tasks import task
from robocorp.excel import tables

from . import ARTIFACTS_DIR, setup_log


INPUT_FILE_NAME = "orders.csv"


@task
def producer():
    setup_log()
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
