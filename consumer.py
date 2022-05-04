import random

from RPA.Robocorp.WorkItems import WorkItems, State, Error

WORKITEMS = WorkItems()


def login():
    # Simulates a login that fails 1/5 times to highlight APPLICATION exception handling.
    # In this example login is performed only once for all work items.
    login_as_james_bond = random.randint(1,5)
    if login_as_james_bond != 1:
        print("Logged in as Bond. James Bond.")
        return True
    else:
        raise ValueError("Login failed.")

def action_for_item(payload):
    # Simulates handling of one work item that fails 1/5 times to
    # highlight BUSINESS exception handling.
    item_action_ok = random.randint(1,5)
    if item_action_ok != 1:
        print(f"Did a thing item for: {payload}")
    else:
        raise ValueError(f"Failed to handle item for: {payload}")

def handle_item():
    # Error handling around one work item.
    payload = WORKITEMS.get_work_item_payload()
    try:
        action_for_item(payload)
        WORKITEMS.release_input_work_item(State.DONE)
    except ValueError as err:
        print(str(err))
        WORKITEMS.release_input_work_item(
            state=State.FAILED,
            exception_type=Error.BUSINESS,
            message=str(err)
        )

def main():
    # Login and then cycle through work items.
    WORKITEMS.get_input_work_item()
    try:
        login()
    except ValueError as err:
        error_message = "Unable to login to target system. Please check that the site/application is up and available."
        print(error_message)
        WORKITEMS.release_input_work_item(
            state=State.FAILED,
            exception_type=Error.APPLICATION,
            message=error_message
        )
    WORKITEMS.for_each_input_work_item(handle_item)

if __name__ == "__main__":
    main()