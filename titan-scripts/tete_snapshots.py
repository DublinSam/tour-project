import sys
from tete_frames import extract_tete_snapshots

root_path = "/users/albanie/scratch/DVD/2014/"

""" use the $TASK_ID variable passed to the script
as an input argument to define the stage number."""
stage = sys.argv[1]
stage_id = str(stage)

"""set the Display Aspect Ratio for snapshots."""
step = 500 # in milliseconds
extract_tete_snapshots(root_path, stage_id, step)
