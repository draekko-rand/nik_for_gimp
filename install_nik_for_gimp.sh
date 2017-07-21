#!/usr/bin/env bash

#
# Tested on Ubuntu 17.04
#
# Required:
#   Gimp 2.9.5 or better (from git)
#   wine-staging (1.9.14 or better)
#   7z
#

export PACKAGE1="wine-staging"
export PACKAGE2="p7zip-full"
export PACKAGE3="imagemagick-6.q16"

export WINEPREFIX=${HOME}/.wine.nik
export WINEARCH=win32

export VERSIONCHECK="2.9.5"
export GIMPVERSION=`gimp --version | awk '{print $NF}'`

export TMP=/tmp/nik_tmp
export NIK_COLLECTION=/tmp/nikcollection-full-1.2.11.exe
export PROGRAMFILES="Program Files"

pwd > /tmp/.nikisntalldir

versioncheck() {
   [ "$1" == "$2" ] && return 10

   ver1front=`echo $1 | cut -d "." -f -1`
   ver1back=`echo $1 | cut -d "." -f 2-`
   ver2front=`echo $2 | cut -d "." -f -1`
   ver2back=`echo $2 | cut -d "." -f 2-`

   if [ "$ver1front" != "$1" ] || [ "$ver2front" != "$2" ]; then
       [ "$ver1front" -gt "$ver2front" ] && return 11
       [ "$ver1front" -lt "$ver2front" ] && return 9

       [ "$ver1front" == "$1" ] || [ -z "$ver1back" ] && ver1back=0
       [ "$ver2front" == "$2" ] || [ -z "$ver2back" ] && ver2back=0
       versioncheck "$ver1back" "$ver2back"
       return $?
   else
           [ "$1" -gt "$2" ] && return 11 || return 9
   fi
}

confirm() {
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            echo "exiting"
            exit 1
            ;;
    esac
}

confirmyn() {
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY])
            sudo apt install $PACKAGE3
            ;;
        *)
            ;;
    esac
}

#Verify the GIMP version installed
versioncheck "$GIMPVERSION" "$VERSIONCHECK"
if [ "$?" -lt 10 ]; then
  echo "Found GIMP version $GIMPVERSION, required version $VERSIONCHECK"
  confirm "Are you sure you want to continue? <y/N>"
fi

# Verify that wine-staging packages are installed
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $PACKAGE1 | grep "ok installed")
if [ "" == "$PKG_OK" ]; then
  confirm "Missing Debian package $PACKAGE1 missing, download and install? <y/N>"
  curl https://dl.winehq.org/wine-builds/Release.key > /tmp/Release.key
  sudo apt-key add /tmp/Release.key
  sudo apt-add-repository 'https://dl.winehq.org/wine-builds/ubuntu/'
  sudo apt update
  sudo apt install $PACKAGE1
  rm /tmp/Release.key
fi

# Verify that the 7z package is installed
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $PACKAGE2 | grep "ok installed")
if [ "" == "$PKG_OK" ]; then
  confirm "Missing Debian package $PACKAGE2, download and install? <y/N>"
  sudo apt install $PACKAGE2
fi

# Verify that the imagemagick-6.q16 package is installed. We need the convert
# command to fix the problem with the tifs generate by several of the plugins.
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $PACKAGE3 | grep "ok installed")
if [ "" == "$PKG_OK" ]; then
  confirmyn "Missing Debian package $PACKAGE3. The package is required to make certain plugin warnings disappear. Download and install? <y/N>"
fi

if [ -d ${TMP} ]; then
    rm -fr ${TMP}
fi

if [ -d ${WINEPREFIX} ]; then
    rm -fr ${WINEPREFIX}
fi

echo "Creating wine setup in $WINEPREFIX and configuring it"
rm -fr ${WINEPREFIX}
wineboot -u &> /dev/null

if [ ! -f ${NIK_COLLECTION} ]; then
    echo "Downloading Nik Collection"
    curl https://dl.google.com/edgedl/photos/nikcollection-full-1.2.11.exe > ${NIK_COLLECTION}
fi
rm -fr ${TMP}
mkdir ${TMP}
cd ${TMP}

echo "Extracting files and folders"
7z x -onik -y ${NIK_COLLECTION} > /dev/null

echo "Moving data"
cd "${TMP}/nik/\$APPDATA"
if [ ! -d "${WINEPREFIX}/drive_c/users/Public/Application Data/" ]; then
  mkdir -p "${WINEPREFIX}/drive_c/users/Public/Application Data/"
fi
if [ ! -d "${WINEPREFIX}/drive_c/users/Public/Local Settings/Application Data/" ]; then
  mkdir -p "${WINEPREFIX}/drive_c/users/Public/Local Settings/Application Data/"
fi
cp -r Google "${WINEPREFIX}/drive_c/users/Public/Local Settings/Application Data/"
cp -r Google "${WINEPREFIX}/drive_c/users/Public/Application Data/"
NIK_FIL_ARRAY=("Analog Efex Pro 2" "Color Efex Pro 4" "Dfine 2" "HDR Efex Pro 2" "Sharpener Pro 3" "Silver Efex Pro 2" "Viveza 2")
NIK_RES_ARRAY=("common" "comparisonStatePresets" "cursors" "filters" "lng" "plugin_common" "presets" "resolutions" "styles" "textures")
for item in "${NIK_FIL_ARRAY[@]}"; do
    for jtem in "${NIK_RES_ARRAY[@]}"; do
        rm -fr "${WINEPREFIX}/drive_c/users/Public/Local Settings/Application Data/Google/${item}/resource/${jtem}"
    done
done

NIK_FIL_ARRAY=("Analog Efex Pro 2" "Color Efex Pro 4" "Dfine 2" "HDR Efex Pro 2" "Sharpener Pro 3" "Silver Efex Pro 2" "Viveza 2")
for item in "${NIK_FIL_ARRAY[@]}"; do
    mkdir -p "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/${item}"
done

cd "${TMP}/nik/Analog Efex Pro 2"
cp *.8bf "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Analog Efex Pro 2"
cp *.exe "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Analog Efex Pro 2"

cd "${TMP}/nik/Color Efex Pro 4"
cp *.8bf "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Color Efex Pro 4"
cp *.exe "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Color Efex Pro 4"

cd "${TMP}/nik/Dfine 2"
cp *.8bf "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Dfine 2"
cp *.exe "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Dfine 2"

cd "${TMP}/nik/HDR Efex Pro 2"
cp *.8bf "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/HDR Efex Pro 2"
cp *.exe "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/HDR Efex Pro 2"

cd "${TMP}/nik/Sharpener Pro 3"
cp *.8bf "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Sharpener Pro 3"
cp *.exe "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Sharpener Pro 3"

cd "${TMP}/nik/Silver Efex Pro 2"
cp *.8bf "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Silver Efex Pro 2"
cp *.exe "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Silver Efex Pro 2"

cd "${TMP}/nik/Viveza 2"
cp *.8bf "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Viveza 2"
cp *.exe "${WINEPREFIX}/drive_c/Program Files/Google/Nik Collection/Viveza 2"

#Let's create config files for each filter.
echo "Creating config files"
NIK_ARRAY=("Analog Efex Pro 2" "Dfine 2" "Color Efex Pro 4" "HDR Efex Pro 2" "Sharpener Pro 3" "Viveza 2" "Nik Collection" "Silver Efex Pro 2")
for item in "${NIK_ARRAY[@]}"; do
    NIK_F=$item
    NIK_F_NW="$(echo -e "${NIK_F}" | tr -d '[[:space:]]')"
    NIK_F_DIR="${WINEPREFIX}/drive_c/users/${USER}/Local Settings/Application Data/Google/${NIK_F}"
    mkdir -p "${NIK_F_DIR}"
    cat <<EOL >"${NIK_F_DIR}/${NIK_F_NW}.cfg"
<configuration>
    <group name="Language">
	<key name="Language" type="string" value="en"/>
    </group>
</configuration>
EOL
done

mkdir -p "${WINEPREFIX}/drive_c/users/Public/Application Data/Google/Nik Collection/"
cat <<EOF >"${WINEPREFIX}/drive_c/users/Public/Application Data/Google/Nik Collection/NikCollection.cfg"
<configuration>
    <group name="Update">
	<key name="Version" type="string" value="1.2.11"/>
    </group>
    <group name="Installer">
	<key name="LicensePath" type="string" value="C:\Program Files\Google\Nik Collection"/>
	<key name="Version" type="string" value="1.2.11"/>
	<key name="identifier" type="string" value="1415926535"/>
	<key name="edition" type="string" value="full"/>
    </group>
    <group name="Instrumentation">
	<key name="ShowInstrumentationScreen" type="bool" value="0"/>
	<key name="AllowSending" type="bool" value="0"/>
    </group>
</configuration>
EOF

cd `cat /tmp/.nikisntalldir`

GIMP_PLUGINS=${HOME}/.config/GIMP/2.9/plug-ins

echo "Install gimp nik plugin"
if [ ! -d "${GIMP_PLUGINS}" ]; then
    echo "Create  directories"
    sudo mkdir -p "${GIMP_PLUGINS}"
    sudo chmod -R $USER.$USER "${GIMP_PLUGINS}"
fi
installation_dir="${GIMP_PLUGINS}"
install -m 755 plug-ins/NIK-ColorEfexPro4.py $installation_dir
install -m 755 plug-ins/NIK-HDREfexPro2.py $installation_dir
install -m 755 plug-ins/NIK-SilverEfexPro2.py $installation_dir
install -m 755 plug-ins/NIK-AnalogEfexPro2.py $installation_dir
install -m 755 plug-ins/NIK-Dfine2.py $installation_dir
install -m 755 plug-ins/NIK-OS-SharpenerPro3.py $installation_dir
install -m 755 plug-ins/NIK-PR-SharpenerPro3.py $installation_dir
install -m 755 plug-ins/NIK-Viveza2.py $installation_dir
if [ -f "$installation_dir/NIK-OS-SharpenerPro3.py" ]; then
    rm -f "$installation_dir/NIK-SharpenerPro3.py"
fi

echo "Install wine nik scripts"
installation_dir="/usr/local/bin"
sudo install -m 755 scripts/nik_analogefexpro2 $installation_dir
sudo install -m 755 scripts/nik_hdrefexpro2 $installation_dir
sudo install -m 755 scripts/nik_viveza2 $installation_dir
sudo install -m 755 scripts/nik_colorefexpro4 $installation_dir
sudo install -m 755 scripts/nik_sharpenerpro3_pr $installation_dir
sudo install -m 755 scripts/nik_sharpenerpro3_os $installation_dir
sudo install -m 755 scripts/nik_dfine2 $installation_dir
sudo install -m 755 scripts/nik_silverefexpro2 $installation_dir
if [ -f "$installation_dir/nik_sharpenerpro3" ]; then
    sudo rm -f "$installation_dir/nik_sharpenerpro3"
fi

echo "Installing icons and desktop shortcuts"
installation_dir="${HOME}/Desktop"
install -m 755 desktop/analog_efex_pro_2.desktop $installation_dir
install -m 755 desktop/dfine_2.desktop $installation_dir
install -m 755 desktop/sharpener_pro_3_pr.desktop $installation_dir
install -m 755 desktop/sharpener_pro_3_os.desktop $installation_dir
install -m 755 desktop/viveza_2.desktop $installation_dir
install -m 755 desktop/color_efex_pro_4.desktop $installation_dir
install -m 755 desktop/hdr_efex_pro_2.desktop $installation_dir
install -m 755 desktop/silver_efex_pro_3.desktop $installation_dir
if [ -f "$installation_dir/sharpener_pro_3.desktop" ]; then
    rm -f "$installation_dir/sharpener_pro_3.desktop"
fi

installation_dir="${HOME}/.local/share/applications"
install -m 755 desktop/analog_efex_pro_2.desktop $installation_dir
install -m 755 desktop/dfine_2.desktop $installation_dir
install -m 755 desktop/sharpener_pro_3_pr.desktop $installation_dir
install -m 755 desktop/sharpener_pro_3_os.desktop $installation_dir
install -m 755 desktop/viveza_2.desktop $installation_dir
install -m 755 desktop/color_efex_pro_4.desktop $installation_dir
install -m 755 desktop/hdr_efex_pro_2.desktop $installation_dir
install -m 755 desktop/silver_efex_pro_3.desktop $installation_dir
if [ -f "$installation_dir/sharpener_pro_3.desktop" ]; then
    rm -f "$installation_dir/sharpener_pro_3.desktop"
fi

if [ ! -d "${HOME}/.icons" ]; then
    mkdir -p ${HOME}/.icons
fi
installation_dir="${HOME}/.icons"
install -m 644 desktop/analog_efex_pro_2.png $installation_dir
install -m 644 desktop/dfine_2.png $installation_dir
install -m 644 desktop/sharpener_pro_3_os.png $installation_dir
install -m 644 desktop/sharpener_pro_3_pr.png $installation_dir
install -m 644 desktop/viveza_2.png $installation_dir
install -m 644 desktop/color_efex_pro_4.png $installation_dir
install -m 644 desktop/hdr_efex_pro_2.png $installation_dir
install -m 644 desktop/silver_efex_pro_3.png $installation_dir
if [ -f "$installation_dir/sharpener_pro_3.png" ]; then
    rm -f "$installation_dir/sharpener_pro_3.png"
fi

installation_dir="${HOME}/.local/share/icons"
install -m 644 desktop/analog_efex_pro_2.png $installation_dir
install -m 644 desktop/dfine_2.png $installation_dir
install -m 644 desktop/sharpener_pro_3_os.png $installation_dir
install -m 644 desktop/sharpener_pro_3_pr.png $installation_dir
install -m 644 desktop/viveza_2.png $installation_dir
install -m 644 desktop/color_efex_pro_4.png $installation_dir
install -m 644 desktop/hdr_efex_pro_2.png $installation_dir
install -m 644 desktop/silver_efex_pro_3.png $installation_dir
if [ -f "$installation_dir/sharpener_pro_3.png" ]; then
    rm -f "$installation_dir/sharpener_pro_3.png"
fi

#echo "Removing installation files"
if [ -f ${NIK_COLLECTION} ]; then
  rm ${NIK_COLLECTION}
fi
if [ -d ${TMP} ]; then
    rm -fr ${TMP}
fi
if [ -f /tmp/.nikisntalldir ]; then
  rm /tmp/.nikisntalldir
fi

echo "Done"

