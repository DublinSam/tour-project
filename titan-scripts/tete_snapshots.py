import sys
from tete_frames import extract_tete_snapshots
from camera import CameraFocus

root_path = "/users/albanie/scratch/DVD/2012/"

""" use the $TASK_ID variable passed to the script
as an input argument to define the stage number."""
stage = sys.argv[1]
stage_id = str(stage)

"""First extract  the camera focus for each stage"""
camera_focus = CameraFocus(root_path, stage_id)
camera_focus.get_camera_states()
camera_focus.save_camera_states()

"""set the Display Aspect Ratio for snapshots."""
step = 500 # in milliseconds
extract_tete_snapshots(root_path, stage_id, step)
