import os
from pathlib import Path

from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems

WORKITEMS = WorkItems()
EXCEL = Files()
ARTIFACTS_DIR = os.getenv("ROBOT_ARTIFACTS")

def main():
    # Get source Excel file from work item.
    # Read rows from Excel.
    # Creates output work items per row.
    WORKITEMS.get_input_work_item()
    destination_path = Path(ARTIFACTS_DIR) / "orders.xlsx"
    filepath = WORKITEMS.get_work_item_file("orders.xlsx", destination_path)
    EXCEL.open_workbook(filepath)
    table = EXCEL.read_worksheet_as_table(header=True)
    for row in table:
        variables = {
            "Name": row["Name"],
            "Zip": row["Zip"],
            "Item": row["Item"],
        }
        WORKITEMS.create_output_work_item(variables=variables, save=True)


if __name__ == "__main__":
    main()