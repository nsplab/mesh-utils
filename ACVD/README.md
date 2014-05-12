
# Notes on Building ACVD

ACVD is a surface mesh coarsening and resampling utility.
* <http://www.creatis.insa-lyon.fr/site/en/acvd>

Its code repository is located at
* <https://github.com/valette/ACVD>

I compiled the vtk6 branch of ACVD, which uses the latest version of VTK.
Unfortunately, VTK does not yet use Qt5 so I had to install Qt4 on my system too.

This is a summary of the steps I took to get ACVD working on my OS X laptop.

## Compiling and Installing Qt4 on OS X

Qt is a cross-platform application and UI development framework.
* <http://qt-project.org/>

I already have a Qt5 installation in my system directory, so I had to install Qt4 in a place
where it won't conflict with anything else. I chose `$HOME/opt/qt-4.8.6/` as the target directory.

First some setup:

    luis@alpha:~$ cd src/archive
    luis@alpha:~/src/archive$ wget http://download.qt-project.org/official_releases/qt/4.8/4.8.6/qt-everywhere-opensource-src-4.8.6.tar.gz
    luis@alpha:~/src/archive$ cd ~/src
    luis@alpha:~/src$ tar xvfz src/archive/qt-everywhere-opensource-src-4.8.6.tar.gz
    luis@alpha:~/src$ mv qt-everywhere-opensource-src-4.8.6 qt-4.8.6
    luis@alpha:~/src$ cd qt-4.8.6
    luis@alpha:~/src/qt-4.8.6$

Now you can configure, compile, and install. This took about an hour for me:

    luis@alpha:~/src/qt-4.8.6$ ./configure -prefix $HOME/opt/qt-4.8.6 -system-zlib -qt-libtiff -qt-libpng -qt-libjpeg -confirm-license -opensource -nomake demos -nomake examples -cocoa -fast -release -platform unsupported/macx-clang-libc++ -no-qt3support -nomake docs -arch x86_64 -developer-build
    luis@alpha:~/src/qt-4.8.6$ gmake
    luis@alpha:~/src/qt-4.8.6$ gmake install
    
## Compiling and Installing VTK6 on OS X

VTK is an open source visualization toolkit for 3D computer graphics.
* <http://www.vtk.org/Wiki/VTK>
* <http://www.vtk.org/Wiki/VTK/Git/Download>

To check out the development version of VTK:

    luis@alpha:~$ cd ~/dev
    luis@alpha:~/dev$ git clone --depth=1 git://vtk.org/VTK.git
    luis@alpha:~/dev$ git clone --depth=1 git://vtk.org/VTKData.git
    luis@alpha:~/dev$ cd VTK
    luis@alpha:~/dev/VTK$

Note that we've installed Qt4 in a separate directory, we need to tell VTK's build process about it.
Examining `FindQt4.cmake` reveals that cmake relies on Qt4's `qmake` to obtain all the relevant
information about Qt4. So, we just have to make sure cmake finds the right qmake binary. We do this
by placing Qt4's bin directory ahead in our PATH before running a program:

    luis@alpha:~/dev/VTK$ qmake -query QT_VERSION
    5.2.1

    luis@alpha:~/dev/VTK$ PATH=$HOME/opt/qt-4.8.6/bin:$PATH qmake -query QT_VERSION
    4.8.6

With that trick, the following configuration step should work for installing VTK at `$HOME/opt/vtk-6.1.0`.
Note the various occurences of that prefix in a few of the arguments:

    luis@alpha:~/dev/VTK$ mkdir build
    luis@alpha:~/dev/VTK$ cd build

    luis@alpha:~/dev/VTK/build$ PATH=$HOME/opt/qt-4.8.6/bin:$PATH cmake -DCMAKE_INSTALL_PREFIX=$HOME/opt/vtk-6.1.0 -DCMAKE_BUILD_TYPE=None -DCMAKE_FIND_FRAMEWORK=LAST -DCMAKE_VERBOSE_MAKEFILE=ON -Wno-dev -DVTK_REQUIRED_OBJCXX_FLAGS='' -DVTK_USE_CARBON=OFF -DVTK_USE_TK=OFF -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=ON -DIOKit:FILEPATH=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk/System/Library/Frameworks/IOKit.framework -DCMAKE_INSTALL_RPATH:STRING=$HOME/opt/vtk-6.1.0/lib -DCMAKE_INSTALL_NAME_DIR:STRING=$HOME/opt/vtk-6.1.0/lib -DVTK_USE_SYSTEM_EXPAT=ON -DVTK_USE_SYSTEM_LIBXML2=ON -DVTK_USE_SYSTEM_ZLIB=ON -DVTK_Group_Qt=ON -DVTK_USE_COCOA=ON -DModule_vtkInfovisBoost=ON -DModule_vtkInfovisBoostGraphAlgorithms=ON -DModule_vtkRenderingFreeTypeFontConfig=ON -DVTK_USE_SYSTEM_HDF5=ON -DVTK_USE_SYSTEM_JPEG=ON -DVTK_USE_SYSTEM_PNG=ON -DVTK_USE_SYSTEM_TIFF=ON -DVTK_WRAP_PYTHON=ON -DPYTHON_LIBRARY='/usr/local/Cellar/python/2.7.6_1/Frameworks/Python.framework/Versions/2.7/lib/libpython2.7.dylib' -DVTK_INSTALL_PYTHON_MODULE_DIR="$HOME/opt/vtk-6.1.0/lib/python2.7/site-packages" ..

If that worked, you should be able to compile and install VTK. This step is going to take a while!

    luis@alpha:~/dev/VTK/build$ time make
    real    69m17.738s
    user    60m11.281s
    sys     8m16.609s
    luis@alpha:~/dev/VTK$ make install

## Compiling ACVD on OS X

First, let's clone the ACVD repo from github

    luis@alpha:~$ cd ~/dev
    luis@alpha:~/dev$ git clone https://github.com/valette/ACVD.git
    luis@alpha:~/dev$ cd ACVD

Now, let's switch to the `vtk6` remote branch. If you list the branches,
the vtk6 branch should be active.

    luis@alpha:~/dev/ACVD$ git checkout vtk6
    luis@alpha:~/dev/ACVD$ git branch
      master
      * vtk6
    luis@alpha:~/dev/ACVD$

If the simple remote-branch switching didn't work, you might be using an older version of git.
There's a more verbose way to do it with the older versions. Anyway, here's the one I used.

    luis@alpha:~$ git --version
    git version 1.8.5.2 (Apple Git-48)

Now we're almost ready to compile. After digging around a bit, I figured out that you can tell
ACVD the location of VTK by setting the `VTK_DIR` environment variable. Also, there's a bug in the build
specification, but I managed to figure out you can avoid that bug if you turn shared libraries off.

So, this is how I finally configured and compiled ACVD:

    luis@alpha:~/dev/ACVD/build$ VTK_DIR=${HOME}/opt/vtk-6.1.0 cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE=ON -DBUILD_SHARED_LIBS=OFF ..
    luis@alpha:~/dev/ACVD/build$ make

Once that finishes, the `bin` subdirectory should have the `stl2ply` and `ACVD` binaries!

    luis@alpha:~/dev/ACVD/build$ cd bin
    luis@alpha:~/dev/ACVD/build/bin$ ls
    ACVD*                       ExamplevtkSurface*          VolumeCrop*                 mesh2vtk*
    ACVD.json                   ManifoldSimplification*     VolumeMedian*               png2raw*
    ACVDQ*                      Minc2Mhd*                   VolumeSlice*                readimage*
    AnisotropicRemeshing*       RandomTriangulation*        VolumeSubsample*            stl2ply*
    AnisotropicRemeshingQ*      VolumeAnalysis*             libvtkDiscreteRemeshing.a   viewer*
    CheckOrientation*           VolumeAnisotropicDiffusion* libvtkSurface.a             viewer2*
    CleanMesh*                  VolumeCleanLabels*          libvtkVolumeProcessing.a    vtk2ply*

## Running ACVD

There's not much documentation, but the source files are easy enough to consult for most questions.

The `stl2ply` binary takes an STL file as input, and saves the same data as a PLY file called `mesh.ply`:

    luis@alpha:~/dev/ACVD/build/bin$ ./stl2ply ~/dev/sloc/meshes/brain01.stl
    load : /Users/luis/dev/sloc3/meshes/brain01.stl
    conversion to mesh.ply finished!

This `mesh.ply` still has the same 72,198 vertices as the original `brain01.stl`. To reduce the number
of vertices down to, say 1000 vertices, we can use `ACVD`.

    luis@alpha:~/dev/ACVD/build/bin$ ./ACVD
    Usage : ACVD file nvertices gradation [options]
    nvertices is the desired number of vertices
    gradation defines the influence of local curvature (0=uniform meshing)

    Optionnal arguments :
    -s threshold : defines the subsampling threshold i.e. the input mesh will be subdivided until its number
    -o directory : sets the output directory
    -of file : sets the output file name
    of vertices is above nvertices*threshold (default=10)
    -d 0/1/2 : enables display (default : 0)
    -q 0/1/2 : set the number of eigenvalues for quadrics post-processing (default : 3)
    -cd file : set custom imagedata file containing density information
    -cmin value : set minimum custom indicator value
    -cmax value : set maximum custom indicator value
    -cf value : set custom indicator multiplication factor
    -m 0/1 : enforce a manifold output ON/OFF (default : 0)
    -sf spare_factor : sets the spare factor
    -sc number_of_spare_clusters : sets the number of spare clusters 

So the first argument should be `mesh.ply`, the second argument 1000, the third argument 0, and
we also want `-d 0` to skip the interactive mode (it gets stuck otherwise):

    luis@alpha:~/dev/ACVD/build/bin$ ./ACVD mesh.ply 1000 0 -d 0
    load : mesh.ply
    PLY file type = 3
    *****************************************************************************
    Mesh with 144275 polygons, 72198 points, 216414 edges
    Bounding Box: [-61.5016, -207.031, -199.932]
                [69.5644, -47.09, -36.9999]
    The mesh is made of 144275 triangles
    3 non-manifold edges and 3 boundary edges
    The mesh has 30 connected components
    Valences entropy: 2.77839
    0 disconnected vertices, 72198 connected vertices
    76.5354 percent of irregular vertices
    Mesh geometry quality:
    AngleMin=0.00305121
    AverageMinAngle=32.8883
    Qmin=9.11218e-05
    Qav=0.617615
    P30=13.338
    *****************************************************************************
    Display=0
    Input mesh: 72198 vertices      and     144275 faces
    Clustering......

    WARNING : The number    of uncorrectly assigned Items was reduced from 6142 to 115 Problems
    Loop 22, duration : 0 s., 67 Modifications
    Trigerring early convergence for speed increase
    WARNING : The number    of uncorrectly assigned Items was reduced from 119 to 115 Problems

    Convergence: 4 disconnected classes
    *Loop 40, duration : 0 s., 0 Modifications
    WARNING : The number    of uncorrectly assigned Items was reduced from 115 to 115 Problems

    Convergence: 0 disconnected classes
    The clustering took :0.317987 seconds.
    Number of loops:        41
    *****************************************************************************
    Mesh with 1980 polygons, 1000 points, 2970 edges
    Bounding Box: [-60.8956, -206.695, -199.498]
                [68.5071, -47.393, -44.9108]
    The mesh is made of 1980 triangles
    0 non-manifold edges and 0 boundary edges
    The mesh has 9 connected components
    Valences entropy: 1.5089
    8 disconnected vertices, 992 connected vertices
    39.9194 percent of irregular vertices
    Mesh geometry quality:
    AngleMin=31.0596
    AverageMinAngle=49.7916
    Qmin=0.498878
    Qav=0.870136
    P30=0
    *****************************************************************************
    115 Items with wrong cluster association
    After Quadrics Post-processing :
    *****************************************************************************
    Mesh with 1980 polygons, 1000 points, 2970 edges
    Bounding Box: [-60.8956, -206.695, -199.498]
                [68.5071, -47.393, -44.9108]
    The mesh is made of 1980 triangles
    0 non-manifold edges and 0 boundary edges
    The mesh has 9 connected components
    Valences entropy: 1.5089
    8 disconnected vertices, 992 connected vertices
    39.9194 percent of irregular vertices
    Mesh geometry quality:
    AngleMin=30.2752
    AverageMinAngle=49.6928
    Qmin=0.496904
    Qav=0.869777
    P30=0
    *****************************************************************************

This creates two files: `simplification.ply` and `smooth_simplification.ply`.

Unfortunately, if you load these in MeshLab, you'll notice that the mesh appears dark instead of shiny.
This is likely because the triangle vertices are saved in the wrong order, and MeshLab is displaying
back-facing triangles as dark because the normals have been flipped.

Luckily, MeshLab can reverse those normals via the menu options

    Filters > Normals, Curvature, and Orientation > Invert Faces Orientation

![MeshLab flip-normals menu](https://raw.githubusercontent.com/nsplab/mesh-utils/master/ACVD/images/meshlab-flip-normals-menu.png)

If you enable the wireframe, you can see that ACVD did indeed produce a very uniform mesh.

![Uniform version of brain01.stl](https://raw.githubusercontent.com/nsplab/mesh-utils/master/ACVD/images/brain01-1000-uniform.png)

Finally, now you can use MeshLab to save the PLY file in STL format!

