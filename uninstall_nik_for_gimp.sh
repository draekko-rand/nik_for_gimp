#!/usr/bin/env bash

delete_file() {
  if [ -e "$1" ]; then
    rm "$1"
  fi
}

sudo_delete_file() {
  if [ -e "$1" ]; then
    sudo rm "$1"
  fi
}

delete_dir() {
  if [ -e "$1" ]; then
    rmdir "$1"
  fi
}

# removing NIK Software wine installation
echo "removing NIK Software wine installation"
WINEPREFIX=${HOME}/.wine.nik
delete_file -fr $WINEPREFIX

GIMP_210_PLUGINS=${HOME}/.config/GIMP/2.10/plug-ins/
GIMP_299_PLUGINS=${HOME}/.config/GIMP/2.99/plug-ins/

# removing plugins for GIMP 2.99
echo "removing plugins for GIMP 2.99"
installation_dir="${GIMP_299_PLUGINS}"
cd $installation_dir
delete_file NIK-ColorEfexPro4/NIK-ColorEfexPro4.py
delete_file NIK-HDREfexPro2/NIK-HDREfexPro2.py
delete_file NIK-SilverEfexPro2/NIK-SilverEfexPro2.py
delete_file NIK-AnalogEfexPro2/NIK-AnalogEfexPro2.py
delete_file NIK-Dfine2/NIK-Dfine2.py
delete_file NIK-OS-SharpenerPro3/NIK-OS-SharpenerPro3.py
delete_file NIK-PR-SharpenerPro3/NIK-PR-SharpenerPro3.py
delete_file NIK-Viveza2/NIK-Viveza2.py
cd ..
delete_dir $installation_dir/NIK-ColorEfexPro4/locale
delete_dir $installation_dir/NIK-HDREfexPro2/locale
delete_dir $installation_dir/NIK-SilverEfexPro2/locale
delete_dir $installation_dir/NIK-AnalogEfexPro2/locale
delete_dir $installation_dir/NIK-Dfine2/locale
delete_dir $installation_dir/NIK-OS-SharpenerPro3/locale
delete_dir $installation_dir/NIK-PR-SharpenerPro3/locale
delete_dir $installation_dir/NIK-Viveza2/locale
delete_dir $installation_dir/NIK-ColorEfexPro4
delete_dir $installation_dir/NIK-HDREfexPro2
delete_dir $installation_dir/NIK-SilverEfexPro2
delete_dir $installation_dir/NIK-AnalogEfexPro2
delete_dir $installation_dir/NIK-Dfine2
delete_dir $installation_dir/NIK-OS-SharpenerPro3
delete_dir $installation_dir/NIK-PR-SharpenerPro3
delete_dir $installation_dir/NIK-Viveza2

# removing plugins for GIMP 2.10
echo "removing plugins for GIMP 2.10"
installation_dir="${GIMP_210_PLUGINS}"
cd $installation_dir
delete_file NIK-ColorEfexPro4.py
delete_file NIK-HDREfexPro2.py
delete_file NIK-SilverEfexPro2.py
delete_file NIK-AnalogEfexPro2.py
delete_file NIK-Dfine2.py
delete_file NIK-OS-SharpenerPro3.py
delete_file NIK-PR-SharpenerPro3.py
delete_file NIK-Viveza2.py

# removing launcher scripts
echo "removing launcher scripts"
installation_dir="/usr/local/bin"
cd $installation_dir
sudo_delete_file nik_analogefexpro2
sudo_delete_file nik_hdrefexpro2
sudo_delete_file nik_viveza2
sudo_delete_file nik_colorefexpro4
sudo_delete_file nik_sharpenerpro3_pr
sudo_delete_file nik_sharpenerpro3_os
sudo_delete_file nik_sharpenerpro3pr
sudo_delete_file nik_sharpenerpro3os
sudo_delete_file nik_dfine2
sudo_delete_file nik_silverefexpro2


# removing desktop icons images
echo "removing desktop icons images"
installation_dir="${HOME}/.icons"
cd $installation_dir
delete_file analog_efex_pro_2.png
delete_file dfine_2.png
delete_file sharpener_pro_3_os.png
delete_file sharpener_pro_3_pr.png
delete_file viveza_2.png
delete_file color_efex_pro_4.png
delete_file hdr_efex_pro_2.png
delete_file silver_efex_pro_3.png

installation_dir="${HOME}/.local/share/icons"
cd $installation_dir
delete_file analog_efex_pro_2.png
delete_file dfine_2.png
delete_file sharpener_pro_3_os.png
delete_file sharpener_pro_3_pr.png
delete_file viveza_2.png
delete_file color_efex_pro_4.png
delete_file hdr_efex_pro_2.png
delete_file silver_efex_pro_3.png

# removing desktop icons
echo "removing desktop icons"
installation_dir="${HOME}/.local/share/applications"
cd $installation_dir
delete_file  analog_efex_pro_2.desktop
delete_file dfine_2.desktop
delete_file sharpener_pro_3_pr.desktop
delete_file sharpener_pro_3_os.desktop
delete_file viveza_2.desktop
delete_file color_efex_pro_4.desktop
delete_file hdr_efex_pro_2.desktop
delete_file silver_efex_pro_3.desktop

installation_dir="${HOME}/Desktop"
cd $installation_dir
delete_file  analog_efex_pro_2.desktop
delete_file dfine_2.desktop
delete_file sharpener_pro_3_pr.desktop
delete_file sharpener_pro_3_os.desktop
delete_file viveza_2.desktop
delete_file color_efex_pro_4.desktop
delete_file hdr_efex_pro_2.desktop
delete_file silver_efex_pro_3.desktop

echo "Done"

