library(sf)
library(sf)
library(spData)
library (tidyverse)
library(tmap)
library(mapedit)
library(leaflet)
#Read Supermarket location data from the csv
supermarket_raw=read.csv('data/WoolworthsLocations.csv')
#Convert Longitude and Latitude to be a geometry, using EPSG 4326 system
supermarket=st_as_sf(supermarket_raw,coords=c("Long","Lat"),crs=4326)
#Transform coordinate into NZGD2000 coordinate system
supermarket=st_transform(supermarket,2193)
#Set tmap mode to plot
tmap_mode("plot")
#Read the shape file for New Zealand for territorial authorities
nz_shape=st_read("Shape_files/TA_2018_clipped")
#Get the shape of Auckland
akl_shape=nz_shape|>filter(TA2018_V_1=="Auckland")
#Crop the map for the area of interest
akl_shape=st_crop(akl_shape,xmin=1740000,xmax=1781000,ymin=5890000,ymax=5940000)
#Initially visualise data for weekdays
data_vis=tm_shape(akl_shape)+tm_polygons()+tm_shape(supermarket)+tm_dots(col='Type',palette='Dark2',size=0.3)+ tm_layout(legend.position = c("right", "top"), 
                                                                                                                         title= 'Woolworth supermarkets location', 
                                                                                                                         title.position = c('right', 'top'),legend.frame = TRUE)
#Save the plot above as png
tmap_save(data_vis,'Plot/locations.png')
#Create supermarket data for Saturday(Only Countdowns and the Distribution center included)
saturday=filter(supermarket,Type%in%c('Countdown','Distribution Centre'))
#Initially visualise data for weekdays
data_vis_sat=tm_shape(akl_shape)+tm_polygons()+tm_shape(saturday)+tm_dots(col='Type',palette='Dark2',size=0.3)+tm_layout(legend.position = c("right", "top"), 
                                                                                                                         title= 'Woolworth supermarkets locations (Saturday demands)', 
                                                                                                                         title.position = c('right', 'top'),legend.frame = TRUE)
#Save the plot as png
tmap_save(data_vis_sat,'Plot/Saturday.png')
#Create an interactive map for the supermarket data set to draw polygon for the path
colorFac = colorFactor("Dark2",supermarket_raw$type)
path=leaflet(supermarket_raw) %>% addTiles() %>%
  addCircleMarkers(radius=5,color=~colorNum(supermarket_raw$Type))%>%editMap()
