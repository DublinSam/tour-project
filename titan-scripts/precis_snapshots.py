import sys
from precis import take_precis_snapshots

root_path = "~/scratch/DVD/2012"

""" use the $TASK_ID variable passed to the script
as an input argument to define the stage number."""
stage = sys.argv[1]
stage_id = str(stage)
print(stage_id)
