"""This package provides for the primary Production and Consumer task
entry points. This utilizes the robocorp.tasks framework as 
well as the robocorp.log facility to log additional information.
"""
from robocorp import log
from robocorp.tasks import task


# example of how to set logging to console for all info level and above
@task
def log_example():
    log.setup_log(output_log_level="info")

    log.debug("Can't see this in console")
    log.info("But can see this")
