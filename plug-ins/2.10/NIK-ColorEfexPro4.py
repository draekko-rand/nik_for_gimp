#!/usr/bin/env python2

'''
NIK-ColorEfexPro4.py

Mod of ShellOut.py focused on getting Google NIK to work.
ShellOut call an external program passing the active layer as a temp file.
Tested only in Ubuntu 22.04 with Gimp 2.10.30/2.10.33(git) with Nik Collection 1.2.11

Author:
Erico Porto on top of the work of Rob Antonishen
Benoit Touchette modified from Erico Porto

this script is modelled after the mm extern LabCurves trace plugin
by Michael Munzert http://www.mm-log.com/lab-curves-gimp

and thanks to the folks at gimp-chat it has grown a bit ;)

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
import platform
import subprocess
import os, sys
import tempfile

TEMP_FNAME = "ShellOutTempFile"

def plugin_main(image, drawable, visible):
  pdb.gimp_image_undo_group_start(image)

  if visible == 2:
    # duplicate layer and rename
    temp = pdb.gimp_image_get_active_drawable(image)
    newLayer = pdb.gimp_layer_copy(temp, 100)
    pdb.gimp_image_insert_layer(image, newLayer, None, -1)
    pdb.gimp_image_set_active_layer(image, newLayer)
    pdb.gimp_item_set_name(newLayer, "ColorEfexPro4")
    temp = pdb.gimp_image_get_active_drawable(image)
  elif visible == 1:
    # new from visible layer and rename
    temp = pdb.gimp_layer_new_from_visible(image, image, "ColorEfexPro4")
    image.add_layer(temp, 0)
  else:
    # use current layer and do not rename
    temp = pdb.gimp_image_get_active_drawable(image)

  buffer = pdb.gimp_edit_named_copy(temp, "ShellOutTemp")

  #save selection if one exists
  hassel = pdb.gimp_selection_is_empty(image) == 0
  if hassel:
    savedsel = pdb.gimp_selection_save(image)

  tempimage = pdb.gimp_edit_named_paste_as_new_image(buffer)
  pdb.gimp_buffer_delete(buffer)
  if not tempimage:
    raise RuntimeError

  tempdrawable = pdb.gimp_image_get_active_layer(tempimage)

  # Use temp file names from gimp, it reflects the user's choices in gimp.rc
  # change as indicated if you always want to use the same temp file name
  # tempfilename = pdb.gimp_temp_name(progtorun[2])
  tempfiledir = tempfile.gettempdir()
  intempfilename = os.path.join(tempfiledir, TEMP_FNAME + "_in." + "tif")
  outtempfilename = os.path.join(tempfiledir, TEMP_FNAME + "_out." + "tif")

  # !!! Note no run-mode first parameter, and user entered filename is empty string
  pdb.gimp_progress_set_text ("Saving a copy")
  pdb.gimp_file_save(tempimage, tempdrawable, intempfilename, intempfilename)

  # Invoke external command
  print("calling Color Efex Pro 4...")
  pdb.gimp_progress_set_text ("calling Color Efex Pro 4...")
  pdb.gimp_progress_pulse()
  child = subprocess.Popen([ "nik_colorefexpro4",  intempfilename ], shell=False)
  child.communicate()

  #make the annoying richtiffiptc warning go away, convert-im6.q16 the file tif to tif
  #requires imagemagick convert-im6.q16
  try:
    child = subprocess.Popen([ "convert-im6.q16", intempfilename, outtempfilename], shell=False)
    child.communicate()
  except:
    print "missing convert-im6.q16 command from imagemagick"

  # put it as a new layer in the opened image
  try:
    if os.path.exists(outtempfilename):
      newlayer2 = pdb.gimp_file_load_layer(tempimage, outtempfilename)
    else:
      newlayer2 = pdb.gimp_file_load_layer(tempimage, intempfilename)
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
  os.remove(intempfilename)  # delete the temporary file
  if os.path.exists(outtempfilename):
    os.remove(outtempfilename)  # delete the temporary file
  gimp.delete(tempimage)   # delete the temporary image

  # Note the new image is dirty in Gimp and the user will be asked to save before closing.
  pdb.gimp_image_undo_group_end(image)
  gimp.displays_flush()


register(
        "nikfilters_colorefexpro4",
        "Color Efex Pro 4",
        "Color Efex Pro 4",
        "Rob Antonishen (original) & Ben Touchette",
        "(C)2011 Rob Antonishen (original) & (C)2016-2022 Ben Touchette",
        "2011,2016-2022",
        "<Image>/Filters/NIK Collection/Color Efex Pro 4",
        "RGB*, GRAY*",
        [ (PF_RADIO, "visible", "Layer:", 2, (("new from duplicate", 2),("new from visible", 1),("current layer",0))) ],
        [],
        plugin_main,
        )

main()
