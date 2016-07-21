#!/usr/bin/env python

'''
NIK-DFine2.py

Mod of ShellOut.py focused on getting Google NIK to work.
ShellOut call an external program passing the active layer as a temp file.
Tested only in Ubuntu 16.04 with Gimp 2.9.5 (git) with Nik Collection 1.2.11

Author:
Erico Porto on top of the work of Rob Antonishen
Benoit Touchette modified from Erico Porto

this script is modelled after the mm extern LabCurves trace plugin
by Michael Munzert http://www.mm-log.com/lab-curves-gimp

and thanks to the folds at gimp-chat has grown a bit ;)

License:

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

The GNU Public License is available at
http://www.gnu.org/copyleft/gpl.html

'''

from gimpfu import *
import shutil
import subprocess
import os, sys
import tempfile

TEMP_FNAME = "ShellOutTempFile"

def plugin_main(image, drawable, visible):
  pdb.gimp_image_undo_group_start(image)

  # Copy so the save operations doesn't affect the original
  if visible == 0:
    # Save in temporary.  Note: empty user entered file name
    temp = pdb.gimp_image_get_active_drawable(image)
  else:
    # Get the current visible
    temp = pdb.gimp_layer_new_from_visible(image, image, "Visible")
    image.add_layer(temp, 0)

  buffer = pdb.gimp_edit_named_copy(temp, "ShellOutTemp")

  #save selection if one exists
  hassel = pdb.gimp_selection_is_empty(image) == 0
  if hassel:
    savedsel = pdb.gimp_selection_save(image)

  tempimage = pdb.gimp_edit_named_paste_as_new(buffer)
  pdb.gimp_buffer_delete(buffer)
  if not tempimage:
    raise RuntimeError
  pdb.gimp_image_undo_disable(tempimage)

  tempdrawable = pdb.gimp_image_get_active_layer(tempimage)
  
  # Use temp file names from gimp, it reflects the user's choices in gimp.rc
  # change as indicated if you always want to use the same temp file name
  # tempfilename = pdb.gimp_temp_name(progtorun[2])
  tempfiledir = tempfile.gettempdir()
  tempfilename = os.path.join(tempfiledir, TEMP_FNAME + "." + "tif")

  # !!! Note no run-mode first parameter, and user entered filename is empty string
  pdb.gimp_progress_set_text ("Saving a copy")
  pdb.gimp_file_save(tempimage, tempdrawable, tempfilename, tempfilename)

  # Invoke external command
  print("calling Dfine 2...")
  pdb.gimp_progress_set_text ("calling Dfine 2...")
  pdb.gimp_progress_pulse()
  child = subprocess.Popen([ "nik_dfine2",  tempfilename ], shell=False)
  child.communicate()

  # put it as a new layer in the opened image
  try:
    newlayer2 = pdb.gimp_file_load_layer(tempimage, tempfilename)
  except:
    RuntimeError

  tempimage.add_layer(newlayer2,-1)
  buffer = pdb.gimp_edit_named_copy(newlayer2, "ShellOutTemp")

  if visible == 0:
    drawable.resize(newlayer2.width,newlayer2.height,0,0)
    sel = pdb.gimp_edit_named_paste(drawable, buffer, 1)
    drawable.translate((tempdrawable.width-newlayer2.width)/2,(tempdrawable.height-newlayer2.height)/2)
  else:
    temp.resize(newlayer2.width,newlayer2.height,0,0)
    sel = pdb.gimp_edit_named_paste(temp, buffer, 1)
    temp.translate((tempdrawable.width-newlayer2.width)/2,(tempdrawable.height-newlayer2.height)/2)

  pdb.gimp_buffer_delete(buffer)
  pdb.gimp_edit_clear(temp)
  pdb.gimp_floating_sel_anchor(sel)

  #load up old selection
  if hassel:
    pdb.gimp_selection_load(savedsel)
    image.remove_channel(savedsel)

  # cleanup
  os.remove(tempfilename)  # delete the temporary file
  gimp.delete(tempimage)   # delete the temporary image

  # Note the new image is dirty in Gimp and the user will be asked to save before closing.
  pdb.gimp_image_undo_group_end(image)
  gimp.displays_flush()


register(
        "nikfilters_dfine2",
        "Dfine 2",
        "Dfine 2",
        "Rob Antonishen (original) & Ben Touchette",
        "(C)2011 Rob Antonishen (original) & (C)2016 Ben Touchette",
        "2016",
        "<Image>/Filters/NIK Collection/Dfine 2",
        "RGB*, GRAY*",
        [ (PF_RADIO, "visible", "Layer:", 1, (("new from visible", 1),("current layer",0))) ],
        [],
        plugin_main,
        )

main()
