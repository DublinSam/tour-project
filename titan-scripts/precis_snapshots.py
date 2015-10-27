import sys
from precis import take_precis_snapshots

root_path = "/users/albanie/scratch/DVD/2013/"

""" use the $TASK_ID variable passed to the script
as an input argument to define the stage number."""
stage = sys.argv[1]
stage_id = str(stage)

"""set the Display Aspect Ratio for snapshots."""
DAR = 16.0/9.0
take_precis_snapshots(root_path, stage_id, DAR)
