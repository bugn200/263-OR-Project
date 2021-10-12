library(sf)
library(spData)
library (tidyverse)
library(tmap)
library(mapedit)
library(OpenStreetMap)
library(raster)
library(rgdal)
library(osrm)
#Read Supermarket location data from the csv
supermarket_raw=read.csv('data/WoolworthsRegion.csv')
#Convert Longitude and Latitude to be a geometry, using EPSG 4326 system
supermarket1=st_as_sf(supermarket_raw,coords=c("Long","Lat"),crs=4326)
#Transform coordinate into NZGD2000 coordinate system
supermarket=st_transform(supermarket1,2193)
#Set tmap mode to plot
tmap_mode("plot")
#Read the shape file for New Zealand for territorial authorities
nz_shape=st_read("Shape_files/TA_2018_clipped")
#Get the shape of Auckland
akl_shape=nz_shape%>%filter(TA2018_V_1=="Auckland")
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

#Get the coordinate of supermarket in each region and the extent coordinates
South=filter(supermarket1,Region%in%c('South','Distribution Centre Auckland'))
South_shape=st_crop(akl_shape,xmin=1758000,xmax=1777000,ymin=5895000,ymax=5913000)
North=filter(supermarket1,Region%in%c('North','Distribution Centre Auckland'))
North_shape=st_crop(akl_shape,xmin=1751000,xmax=1766000,ymin=5908000,ymax=5936000)
Central=filter(supermarket1,Region%in%c('Central','Distribution Centre Auckland'))
Central_shape=st_crop(akl_shape,xmin=1750000,xmax=1765000,ymin=5907800,ymax=5922000)
East=filter(supermarket1,Region%in%c('East','Distribution Centre Auckland'))
East_shape=st_crop(akl_shape,xmin=1759000,xmax=1773000,ymin=5906800,ymax=5918500)
West=filter(supermarket1,Region%in%c('West','Distribution Centre Auckland'))
West_shape=st_crop(akl_shape,xmin=1741100,xmax=1762000,ymin=5908000,ymax=5928000)



#Read the route file for weekday route and save as a png
weekdayRoute=readLines('data/WeekdayRouteStores.txt')
#Create a matrix to save data
tripMatrix=matrix(0,65,4)
colnames(tripMatrix)=c('Long','Lat','LongEnd','LatEnd')
#Initialise for the number of node(will be used to plot)
nodeReach=1
for(i in 1:length(weekdayRoute)) {
  #Initialise start point and split the string
  route=as.vector(st_coordinates(filter(supermarket,Store=='Distribution Centre Auckland')$geometry))
  weekdayR=strsplit(weekdayRoute[i],split=',')
  for(j in 1:length(weekdayR[[1]])) {
    #Add coordinate to the start and the end point of the arrows
    tripMatrix[,'Long'][nodeReach]=route[1]
    tripMatrix[,'Lat'][nodeReach]=route[2]
    #Add coordinate to the end point of arrows
    route1=as.vector(st_coordinates(filter(supermarket,Store==weekdayR[[1]][j])$geometry))
    tripMatrix[,'LongEnd'][nodeReach]=route1[1]
    tripMatrix[,'LatEnd'][nodeReach]=route1[2]
    route=route1
    nodeReach=nodeReach+1
  }
}
#change tripMatrix to a dataframe
tripMatrix=as.data.frame(tripMatrix)
#Plot the route and save as png
ggplot(akl_shape)+
  geom_sf(data=akl_shape,fill='grey')+
  geom_sf(data=supermarket,aes(color=Type))+
  scale_color_brewer(palette="Dark2")+
  geom_segment(data=tripMatrix,aes(x=Long,y=Lat,xend=LongEnd,yend=LatEnd),
               arrow=arrow(length=unit(0.2,'cm')),alpha=0.3)+
  labs(title='Weekday Routes')
ggsave('Plot/WeekdayRoute.png')
#Read the route file for Saturday route and save as a png
saturdayRoute=readLines('data/SaturdayRouteStores.txt')
#Create a matrix to save the data
satTrip=matrix(0,53,4)
colnames(satTrip)=c('Long','Lat','LongEnd','LatEnd')
#Initialise number of node Reach
nodeReach=1
for(i in 1:length(saturdayRoute)) {
  #Initialise the start point and split the string
  route=as.vector(st_coordinates(filter(supermarket,Store=='Distribution Centre Auckland')$geometry))
  satRoute=strsplit(saturdayRoute[i],split=',')
  for(j in 1:length(satRoute[[1]])) {
    #Add the start point to the matrix
    satTrip[,'Long'][nodeReach]=route[1]
    satTrip[,'Lat'][nodeReach]=route[2]
    #Add the end point coordinate to the matrix
    route1=as.vector(st_coordinates(filter(supermarket,Store==satRoute[[1]][j])$geometry))
    satTrip[,'LongEnd'][nodeReach]=route1[1]
    satTrip[,'LatEnd'][nodeReach]=route1[2]
    route=route1
    nodeReach=nodeReach+1
  }
}
#Convert satTrip to a data frame
satTrip=as.data.frame(satTrip)
#Plot the map and save it as a png
ggplot(akl_shape)+
  geom_sf(data=akl_shape,fill='grey')+
  geom_sf(data=saturday,aes(color=Type))+
  scale_color_brewer(palette="Dark2")+
  geom_segment(data=satTrip,aes(x=Long,y=Lat,xend=LongEnd,yend=LatEnd),
               arrow=arrow(length=unit(0.2,'cm')),alpha=0.3)+
  labs(title='Saturday Routes')
ggsave('Plot/SaturdayRoute.png')
#Transform all the region shape to 4326 to plot the regional route map
North_shape=st_transform(North_shape,4326)
South_shape=st_transform(South_shape,4326)
East_shape=st_transform(East_shape,4326)
West_shape=st_transform(West_shape,4326)
Central_shape=st_transform(Central_shape,4326)
#Classify region for weekdayRoute
w=as.data.frame(weekdayRoute)
colnames(w)='Route'
w$Region='Unknown'
#classify region and the route it is in
for(i in 1:nrow(w)) {
  #split the string for the route
  route=str_split(w[i,1],',')
  w[i,2]=filter(supermarket,Store==route[[1]][1])$Region
}
#Do the same thing for Saturday routes
s=as.data.frame(saturdayRoute)
colnames(s)='Route'
s$Region='Unknown'
for(i in 1:nrow(s)) {
  #split the string for the route
  route=str_split(s[i,1],',')
  s[i,2]=filter(supermarket,Store==route[[1]][1])$Region
}

#Put each route region into a new data frame
North_route=filter(w,Region=='North')
South_route=filter(w,Region=='South')
East_route=filter(w,Region=='East')
West_route=filter(w,Region=='West')
Central_route=filter(w,Region=='Central')
North_sat_route=filter(s,Region=='North')
South_sat_route=filter(s,Region=='South')
East_sat_route=filter(s,Region=='East')
West_sat_route=filter(s,Region=='West')
Central_sat_route=filter(s,Region=='Central')
#Save the North shape as a raster for reusability
akl_North=openmap(as.numeric(st_bbox(North_shape))[c(4,1)],as.numeric(st_bbox(North_shape))[c(2,3)],type='osm')
akl_North=openproj(akl_North)
North_raster=raster(akl_North)
North_raster=writeRaster(North_raster,'Shape_files/North.tif',format='GTiff',overwrite=TRUE)
#If the file is available in Shape_files, run this command only
North_raster=raster('Shape_files/North.tif')
#Plot the map of the Northern region and the supermarkets
tm_shape(North_raster)+tm_rgb()+tm_shape(North)+tm_dots(col='Type',palette='Dark2',size=0.3)

#Save the South shape as a raster for reusability
akl_South=openmap(as.numeric(st_bbox(South_shape))[c(4,1)],as.numeric(st_bbox(South_shape))[c(2,3)],type='osm')
akl_South=openproj(akl_South)
South_raster=raster(akl_South)
South_raster=writeRaster(South_raster,'Shape_files/South.tif',format='GTiff')
#If the file is available in Shape_files,run this command only
South_raster=raster('Shape_files/South.tif')
#Plot the map of the Southern region and the supermarkets
tm_shape(South_raster)+tm_rgb()+tm_shape(South)+tm_dots(col='Type',palette='Dark2',size=0.3)

#Save the East shape as a raster for reusability
akl_East=openmap(as.numeric(st_bbox(East_shape))[c(4,1)],as.numeric(st_bbox(East_shape))[c(2,3)],type='osm')
akl_East=openproj(akl_East)
East_raster=raster(akl_East)
East_raster=writeRaster(East_raster,'Shape_files/East.tif',format='GTiff')
#If the file is available in Shape_files,run this command only
East_raster=raster('Shape_files/East.tif')
#Plot the map of the Southern region and the supermarkets
tm_shape(East_raster)+tm_rgb()+tm_shape(East)+tm_dots(col='Type',palette='Dark2',size=0.3)

#Save the West shape as a raster for reusability
akl_West=openmap(as.numeric(st_bbox(West_shape))[c(4,1)],as.numeric(st_bbox(West_shape))[c(2,3)],type='osm')
akl_West=openproj(akl_West)
West_raster=raster(akl_West)
West_raster=writeRaster(West_raster,'Shape_files/West.tif',format='GTiff')
#If the file is saved in Shape_files,run this command only
West_raster=raster('Shape_files/West.tif')
#Plot the map of the Southern region and the supermarkets
a2=tm_shape(West_raster)+tm_rgb()+tm_shape(West)+tm_dots(col='Type',palette='Dark2',size=0.3)

#Save the Central shape as a raster for reusability
akl_Central=openmap(as.numeric(st_bbox(Central_shape))[c(4,1)],as.numeric(st_bbox(Central_shape))[c(2,3)],type='osm')
akl_Central=openproj(akl_Central)
Central_raster=raster(akl_Central)
Central_raster=writeRaster(Central_raster,'Shape_files/Central.tif',format='GTiff')
#If the file is saved in Shape_files,run this command only
Central_raster=raster('Shape_files/Central.tif')
#Plot the map of the Southern region and the supermarkets
a1=tm_shape(Central_raster)+tm_rgb()+tm_shape(Central)+tm_dots(col='Type',palette='Dark2',size=0.3)

source('regionalRoute.R')
North_map=regionalRoute(regional_raster= North_raster,regional_trips = North_route,regional_sat_trips = North_sat_route,region_stores = North)
tmap_save(North_map,'Plot/North_routes.png',width = 2100,height=1200)
South_map=regionalRoute(regional_raster= South_raster,regional_trips = South_route,regional_sat_trips = South_sat_route,region_stores = South)
tmap_save(South_map,'Plot/South_routes.png',width = 2500,height=900)
East_map=regionalRoute(regional_raster= East_raster,regional_trips = East_route,regional_sat_trips = East_sat_route,region_stores = East)
tmap_save(East_map,'Plot/East_routes.png',width = 2500,height=850)
West_map=regionalRoute(regional_raster= West_raster,regional_trips = West_route,regional_sat_trips = West_sat_route,region_stores = West)
tmap_save(East_map,'Plot/West_routes.png',width = 2500,height=850)
Central_map=regionalRoute(regional_raster= Central_raster,regional_trips = Central_route,regional_sat_trips = Central_sat_route,region_stores = Central)
tmap_save(Central_map,'Plot/Central_routes.png',width = 2500,height=900)
