# QGIS_to_CEA_Migration_Script
Select buildings in QGIS and export them to CEA, bypassing gaps and hiatus in CEA, by using your own shapefiles to geo-reference on OpenStreetmaps.

**1. Introduction**

Usually, if you need to upload buildings not presente on the database of CEA, you have not much options left, but back-engineer the right files according to the structure ingested by CEA.
While CEA works selecting the contour and highlighting the buildings insite it (basically with a convex hull), in QGIS, this process must be done separately, however it is not sufficient.
In fact, aside exporting from QGIS the selected building as shapefile, you need precisely the following files to make them visible and geographically referenced in CEA: 

  1) The "site" ones (.cpg, .dbf, .prj, .shp and .shx): it expresses the convex hull that is the zone in CEA you contour to select the buildings;
  2) The "zone" ones (.cpg, .dbf, .prj, .shp and .shx): it represents the buildings that are physically inside the area selected;
  3) Typology.dbf: a file containing some mandatory attributes which CEA uses to load all the different capabilities(archetypes mapper, solar irradiation and so on and so forth).

**2. Methodology**

This script, bypasses the possible mistakes that can occur by manually edit the fiels and gran the inheritance of the table of attributes fields inside CEA database view, instead of basing the initial fields only on the CEA archetypes mapper information.
The logic is reverting the process CEA follows to work seamlessly in QGIS and created the needed files authomatically under a specified path. Instead of creating a contour and selecting the buildings inside the areas (CEA-wise) the script create a convex hollow enveloping the selected buildings constraining it to the farthest vertexes of the boundary polygons, basically reverting the process.

Two methodological steps are of a certain importance:

  1) Setting up correctly the structure of the folders where to copy paste the generated files, considering that everytime (if the main directory stands the same) they will be overwritten.
  2) Using the right command to execute the script with the right pattern on QGIS Python plugin interface.

    **2.1 Setting up the working directory**
    
    Typilcally the directory tree of a complete CEA project ("Esempio") shows the following structure:**
    
    C:.
    ├───Esempio
        ├───inputs
        │   ├───building-geometry
        │   ├───building-properties
        │   │   └───schedules
        │   ├───inputs
        │   │   └───networks
        │   ├───networks
        │   ├───technology
        │   │   ├───archetypes
        │   │   │   └───use_types
        │   │   ├───assemblies
        │   │   └───components
        │   ├───topography
        │   └───weather
        └───outputs
            └───data
                ├───costs
                ├───demand
                ├───occupancy
                ├───optimization
                │   └───master
                └───solar-radiation
                    └───radiance_geometry_pickle
                        ├───surroundings
                        └───zone
    
    The usual structure of the files contained in the folder "building-geometry" is as follows:
    
    
        **85 site.dbf
        401 site.prj
        364 site.shp
        108 site.shx**
        10 surroundings.cpg
        4,945 surroundings.dbf
        401 surroundings.prj
        2,796 surroundings.shp
        204 surroundings.shx
        **10 zone.cpg
        6,903 zone.dbf
        401 zone.prj
        2,444 zone.shp
        140 zone.shx**
    
    The bolded fonts files are the ones that make the entities in CEA and that the script generates.
    
    Together with these files, the file **typology.dbf** is generated and should go into the folder "Building-properties"
    
    Each project has its unique set of these three groups of file as above.
    
    **2.1 How-to use the script in QGIS**
    
    Using the script in QGIS is easy and it needs the following steps to be implemented:
    
    First of all, create a folder named as you wish under a directory where you have full writing right as administrator (i.e., C:\CEAQGIS\[your_folder_name]) and copy paste the file "qgis_to_cea_export" 
    you can download from the repository.

        Then you can follow the steps:

        1) Open QGIS;
        2) Open the shapefiles with the related buildings;
        3) Project the layer as WGS84 EPSG: 4326, by reprojecting the files with the toolbox function "re-project" (and not by simply assigning the geographic reference system;
        4) Select the buildings you want to use as a project in CEA and be sure the layer (the reprojected on or the one originally in WGS84 EPSG: 4326, is kept active (it appears highlighted);
        ||||The algorithm will export only the selected buildings in the active layer each time, overwriting the files previously generated--> consider to change directory every time you want to 
        have separate back-up copies;
        5) Under the menu "plugins" open python console;
        6) Start the script with the following command in the python console (second white space with the >>>) with the following command by pressing enter, and replace [your_folder_name] with the 
        chosen name, by copy pasting: 
        
        exec(open(r'C:\[your_folder_name]\qgis_to_cea_export.py').read()); run_from_qgis()

        7) Go to the folder C:\CEAQGIS and locate the following files:

                  1) The "site" ones (.cpg, .dbf, .prj, .shp and .shx);
                  2) The "zone" ones (.cpg, .dbf, .prj, .shp and .shx);
                  3) Typology.dbf.
                  
        8) Copy paste the files at point 1) and 2) in the CEA folder project in the "building-Geometry" folder;
        9) Copy paste the file "typology.dbf" 3) in the "building-properties" folder;
        10) Open CEA Dashboard (it works with CEA 3.39.4 - not tested yet with the new beta Version CEA 4);
        11) Open project by assigning the folder C:\CEAQGIS as location.
        12) load all the features and process your buildings by changing the attributes in the fields as you prefer.

**3. Results**

The project will show the buildings exported from QGIS and imported in CEA, with all their attribute in the table of attributes. It works well and smoothly run.
The most common errors are in the set up of the directory of the files or in python extensions not yet installed in your system, or not correctly pipelined. In this case, consider adding the right 
path to your variables of environment.
The CRS (Central Reference System) mismatch is one of the most common issues occurring during this procedure and it can be reduced or avoided, by reprojecting the file as explained above and not simply re-assigning the CRS (usually made by right-clicling on a layer and selecting the right option).

**4. Conclusion**

This simple Python console in QGIS, let the user have more operativity and freedom as far as importing buildings not present or badly digitized in CEA are concerne. The output and related trials gave the 100% of succes in obtaining results in CEA bypassing the contour methodology and retro-importing it by using the convex hollow function.
        
        
