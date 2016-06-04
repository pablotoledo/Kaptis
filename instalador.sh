
echo "Instalador de Kaptis para Raspbian"
echo "Actualizando dispositivo"
sudo apt-get update
sudo apt-get -y upgrade
sudo rpi-update

echo "Instalando dependencias de Kaptis"
sudo apt-get -y install build-essential python-opencv libopencv-dev

echo "Instalando Kaptis"
mkdir -p $HOME"/Kaptis/"
cp -r * $HOME"/Kaptis/"


echo "Programando ejecución de Kaptis en el arranque de la Raspberry Pi"
sudo cp scriptCamara.sh /etc/init.d/
sudo chmod 755 /etc/init.d/scriptCamara.sh
sudo update-rc.d scriptCamara.sh defaults