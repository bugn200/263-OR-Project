library(sf)
library(spData)
library (tidyverse)
library(tmap)
library(mapedit)
#Read Supermarket location data from the csv
supermarket_raw=read.csv('data/WoolworthsRegion.csv')
#Convert Longitude and Latitude to be a geometry, using EPSG 4326 system
supermarket=st_as_sf(supermarket_raw,coords=c("Long","Lat"),crs=4326)
#Transform coordinate into NZGD2000 coordinate system
supermarket=st_transform(supermarket,2193)
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
South=filter(supermarket,Region%in%c('South','Distribution Centre Auckland'))
South_shape=st_crop(akl_shape,xmin=1758000,xmax=1777000,ymin=5895000,ymax=5913000)
North=filter(supermarket,Region%in%c('North','Distribution Centre Auckland'))
North_shape=st_crop(akl_shape,xmin=1751000,xmax=1764000,ymin=5908000,ymax=5936000)
Central=filter(supermarket,Region%in%c('Central','Distribution Centre Auckland'))
Central_shape=st_crop(akl_shape,xmin=1750000,xmax=1762500,ymin=5907800,ymax=5922000)
East=filter(supermarket,Region%in%c('East','Distribution Centre Auckland'))
East_shape=st_crop(akl_shape,xmin=1759000,xmax=1773000,ymin=5908000,ymax=5918500)
West=filter(supermarket,Region%in%c('West','Distribution Centre Auckland'))
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
ggplot(akl_shape)+geom_sf(data=akl_shape,fill='grey')+geom_sf(data=supermarket,
                                                                            aes(color=Type))+scale_color_brewer(palette="Dark2")+geom_segment(data=tripMatrix,
                                                                                                                                              aes(x=Long,y=Lat,xend=LongEnd,yend=LatEnd),
                                                                                                                                                               arrow=arrow(length=unit(0.2,'cm')),alpha=0.3)+labs(title='Weekday Routes')
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
ggplot(akl_shape)+geom_sf(data=akl_shape,fill='grey')+geom_sf(data=saturday,
                                                              aes(color=Type))+scale_color_brewer(palette="Dark2")+geom_segment(data=satTrip,
                                                                                                                                aes(x=Long,y=Lat,xend=LongEnd,yend=LatEnd),
                                                                                                                                arrow=arrow(length=unit(0.2,'cm')),alpha=0.3)+labs(title='Saturday Routes')
ggsave('Plot/SaturdayRoute.png')
