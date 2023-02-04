#!/usr/bin/env python3

#Tested only in Ubuntu 22.10 with Gimp 2.99/3.0 (git) with NIK Collection 1.2.11
#
#Updated for GIMP git (2.99+) and Python 3
#
#Author: Draekko
#
#License:
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; version 3 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#The GNU Public License is available at
#http://www.gnu.org/copyleft/gpl.html


'''
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
import sys, os
import shutil
import subprocess
import tempfile
'''

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
import sys, os
import shutil
import subprocess
import tempfile

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

class Duplicate():
    name = _("New from duplicate")
    position = 0

class Visible():
    name = _("New from visible")
    position = 1

class Current():
    name = _("Current layer")
    position = 2

plugin_name = "Analog Efex Pro 2"
internal_name = plugin_name.replace(" ", "")
script_name = internal_name.lower()
RESPONSE_TYPE_RESET = 99
layer_modes = [Duplicate(), Visible(), Current()]
                
class NIKAnalogEfexPro2 (Gimp.PlugIn):

    __gproperties__ = {
        "selected_layer_mode" : (int,
                        _("Layer mode { New from duplicate (0), New from visible (1), Current layer (2) }"),
                        _("Layer mode { New from duplicate (0), New from visible (1), Current layer (2) }"),
                        0, 2, 0,
                        GObject.ParamFlags.READWRITE),
        "remember" : (bool,
                      _("Remember setting"),
                      _("Remember setting"),
                      False,
                      GObject.ParamFlags.READWRITE)
    }

    selected_layer_mode = 0
    local_config = None
    remember = False

    def layer_mode_changed(self, val):
        layermode = val.get_active()
        self.selected_layer_mode = layermode
        if (self.remember):
            if(self.local_config is not None):
                self.local_config.set_property('selected_layer_mode', layermode)

    def checkbox_changed(self, val):
        status = val.get_active()
        self.remember = status
        if(self.local_config is not None):
            self.local_config.set_property('remember', status)
        if (status):
            self.local_config.set_property('selected_layer_mode', self.selected_layer_mode)

    def launch(self, procedure, run_mode, image, n_drawables, drawables, args, data):
        Gimp.context_push()
        image.undo_group_start()
    
        actives = image.list_selected_layers()
        active = actives[0]

        if (self.selected_layer_mode == Duplicate.position):
            #Use duplicate layer
            active = image.get_active_layer()
            newLayer = Gimp.Layer.copy(active)
            image.insert_layer(newLayer, None, -1)
            image.set_selected_layers([newLayer])
            Gimp.Item.set_name(newLayer, plugin_name)
            temp = image.get_active_drawable()
        elif (self.selected_layer_mode == Visible.position):
            #Use new from visible layer
            result = Gimp.get_pdb().run_procedure('gimp-layer-new-from-visible', [
                GObject.Value(Gimp.Image, image),
                GObject.Value(Gimp.Image, image),
                GObject.Value(GObject.TYPE_STRING, plugin_name)
            ]) 
            if (result.index(0) != Gimp.PDBStatusType.SUCCESS):
                raise RuntimeError
            temp = result.index(1)
            image.insert_layer(temp, active.get_parent(), 0)
        elif (self.selected_layer_mode == Current.position):
            #Use the current layer
            temp = image.get_selected_drawables()[0]
        else:
            raise RuntimeError

        buffer = Gimp.edit_named_copy([ temp ], internal_name+"-Temp-Layer")
        tempimage = Gimp.edit_named_paste_as_new_image(buffer)
        Gimp.buffer_delete(buffer)

        if not tempimage:
            raise RuntimeError

        tempdrawable = tempimage.get_selected_drawables()[0]
        tempfilename = os.path.join('/tmp', internal_name+'_TEMP.tif')
        Gimp.progress_set_text ("Saving a copy")
        tempfileOut = Gio.File.new_for_path(tempfilename)
        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, tempimage, [ tempdrawable ], tempfileOut)
    
        #Launch NIK windows app through wine
        child = subprocess.Popen([ "nik_"+script_name,  tempfilename ], shell=False)
        child.communicate()

        tempfileIn = Gio.File.new_for_path(tempfilename)
        newlayer2 = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, tempimage, tempfileIn)
        tempimage.insert_layer(newlayer2, active.get_parent(), 0)
        buffer = Gimp.edit_named_copy([ newlayer2 ], plugin_name)
        sel = Gimp.edit_named_paste(temp, buffer, 1)
        Gimp.floating_sel_anchor(sel)
        Gimp.buffer_delete(buffer)
        os.remove(tempfilename)
        tempimage.delete()

        Gimp.displays_flush()
        image.undo_group_end()
        Gimp.context_pop()
        
    def process_image(self, procedure, run_mode, image, n_drawables, drawables, args, data):
        config = procedure.create_config()
        config.begin_run(image, run_mode, args)
    
        self.local_config = config
        
        self.selected_layer_mode = config.get_property('selected_layer_mode')
        self.remember = config.get_property('remember')

        if run_mode == Gimp.RunMode.INTERACTIVE:
            GimpUi.init('nik'+internal_name+'-python')

            use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
            dialog = GimpUi.Dialog(use_header_bar=use_header_bar, title=plugin_name)
            
            dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("_Reset", RESPONSE_TYPE_RESET)
            dialog.add_button("_OK", Gtk.ResponseType.OK)

            hom=False
            spac=10
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=hom, spacing=spac)
            dialog.get_content_area().add(hbox)
            hbox.show()

            table = Gtk.Grid()
            table.set_column_homogeneous(False)
            table.set_border_width(spac)
            table.set_column_spacing(spac)
            table.set_row_spacing(spac)

            label = Gtk.Label(label=_("Layer Mode"))
            label.set_xalign(0.0)
            label.set_yalign(0.5)
            label.set_tooltip_text(_("Layer mode selection to use when calling NIK plugin"))
            table.attach(label, 0, 0, 1, 1)
            label.show()

            combo = Gtk.ComboBoxText.new()
            for txt in [ct.name for ct in layer_modes]:
                combo.append_text(txt)
            combo.set_halign(Gtk.Align.FILL)
            table.attach(combo, 1, 0, 1, 1)
            combo.set_active(self.selected_layer_mode)
            combo.show()
            combo.connect("changed", self.layer_mode_changed)

            checkbox = Gtk.CheckButton(label=_("Remember current setting"))
            checkbox.set_tooltip_text(_("When checked the layer mode will be set for the next use"))
            checkbox.set_border_width(spac)
            checkbox.set_sensitive(True)
            checkbox.set_active(self.remember)
            checkbox.show()
            checkbox.connect("toggled", self.checkbox_changed)
            table.attach(checkbox, 0, 1, 1, 1)

            hbox.add(table)
            table.show()
            
            while (True):
                response = dialog.run()
                if response == RESPONSE_TYPE_RESET:
                    self.selected_layer_mode = 0
                    combo.set_active(self.selected_layer_mode)
                    self.remember = False
                    checkbox.set_active(self.remember)
                    if(self.local_config is not None):
                        self.local_config.set_property('remember', self.remember)
                        self.local_config.set_property('selected_layer_mode', self.selected_layer_mode)
                elif response == Gtk.ResponseType.OK:
                    dialog.destroy()
                    self.launch(procedure, run_mode, image, n_drawables, drawables, args, data)
                    config.end_run(Gimp.PDBStatusType.SUCCESS)
                    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
                elif response == Gtk.ResponseType.CANCEL:
                    dialog.destroy()
                    config.end_run(Gimp.PDBStatusType.CANCEL)
                    return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
                else:
                    dialog.destroy()
                    return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                                        GLib.Error())

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None
        
    def do_query_procedures(self):
        return [ "nik-"+internal_name+"-python" ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.process_image, None)
        procedure.set_image_types("RGB*, GRAY*");
        procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                        Gimp.ProcedureSensitivityMask.DRAWABLES)
        procedure.set_documentation("NIK Collections "+plugin_name+" GIMP Plugin",
                                    "NIK Collections Plugins (v1.2.11)",
                                    name);
        procedure.set_menu_label(plugin_name)
        procedure.set_attribution("Draekko", "Draekko", "2022");
        procedure.add_menu_path('<Image>/Filters/NIK Collection v1/');

        procedure.add_argument_from_property(self, "selected_layer_mode")
        procedure.add_argument_from_property(self, "remember")
        
        return procedure

Gimp.main(NIKAnalogEfexPro2.__gtype__, sys.argv)
