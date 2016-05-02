# reflect

## Python module dependencies:

* imageio 1.5
* numpy 1.10.1
* opencv-python 3.0.0
  * Win64: http://www.lfd.uci.edu/~gohlke/pythonlibs/bofhrmxk/opencv_python-3.1.0-cp34-none-win_amd64.whl
  * Linux: http://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/
* pygame 1.9.2a0
  * Linux: http://stackoverflow.com/questions/17869101/unable-to-install-pygame-using-pip
* scipy 0.16.1
* pywin32-220.win-amd64-py3.4
* watchdog 0.8.3
* tkinter
  * Linux: sudo apt-get install python3-tk

## Installing on linux

* Get pip3: `sudo apt-get install python3-pip`
* Install tkinter: `sudo apt-get install python3-tk`
* Install graphviz: `sudo apt-get install graphviz`
* Install pygame:

        sudo apt-get build-dep python-pygame
        sudo apt-get install mercurial
        sudo pip3 install hg+http://bitbucket.org/pygame/pygame

* Install numpy: `sudo pip3 install numpy`
* Install opencv 3.1.0: http://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/

        sudo apt-get update
        sudo apt-get upgrade
        sudo apt-get install build-essential cmake git pkg-config
        sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev
        sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
        sudo apt-get install libgtk2.0-dev
        sudo apt-get install libatlas-base-dev gfortran
        sudo apt-get install python3.4-dev

        cd ~
        git clone https://github.com/Itseez/opencv.git
        cd opencv
        git checkout 3.1.0

        cd ~
        git clone https://github.com/Itseez/opencv_contrib.git
        cd opencv_contrib
        git checkout 3.1.0

        cd ~/opencv
        mkdir build
        cd build
        cmake -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D INSTALL_C_EXAMPLES=OFF \
          -D INSTALL_PYTHON_EXAMPLES=ON \
          -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
          -D BUILD_EXAMPLES=ON ..

        make -j4

        sudo make install
        sudo ldconfig

* Go to the `reflect` directory (containing `setup.py`) and run: `sudo pip3 install -e .`
* Run e.g. `python3 start.py -f examples/example1_slideshow.py -V graph.png`

## Controls

In the console:
* `q` – Quit
* `space` – Force reload

In the preview window:
* Middle click on the video area to play/pause
* Press the spacebar to play/pause




