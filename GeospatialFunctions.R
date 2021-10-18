arrowRoute=function(routeFilename,storeDf) {
  #This function should draw a map with the arrow for the direction between stores
  #Input:   routeFilename: String
  #         the LP output file name that we will use
  #         storeDf: dataframe
  #         The data frame for supermarket location either on weekday or Saturday
  #Output:  map: ggplot
  #         The map with the direction between each stores, excluding the final arc going back to the Distribution Centre   

  #Identify which kind of map should be shown and put on label
  if(identical(storeDf,supermarket)) {
    name='Weekday '
  } else {
    name='Saturday '
  }
  #Read the route file
  usedRoute=readLines(routeFilename)
  #Create matrix to store the route file
  tripMatrix=matrix(0,nrow(storeDf)-1,4)
  colnames(tripMatrix)=c('Long','Lat','LongEnd','LatEnd')
  #Initialise node reach(the row for the matrix)
  nodeReach=1
  for(i in 1:length(usedRoute)) {
    #Initialise start point and split the string
    route=as.vector(st_coordinates(filter(storeDf,Store=='Distribution Centre Auckland')$geometry))
    used=strsplit(usedRoute[i],split=', ')
    for(j in 1:length(used[[1]])) {
      #Add coordinate to the start and the end point of the arrows
      tripMatrix[,'Long'][nodeReach]=route[1]
      tripMatrix[,'Lat'][nodeReach]=route[2]
      #Add coordinate to the end point of arrows
      route1=as.vector(st_coordinates(filter(storeDf,Store==used[[1]][j])$geometry))
      tripMatrix[,'LongEnd'][nodeReach]=route1[1]
      tripMatrix[,'LatEnd'][nodeReach]=route1[2]
      route=route1
      nodeReach=nodeReach+1
    }
    
  }
  #change tripMatrix to a dataframe
  tripMatrix=as.data.frame(tripMatrix)
  #Return the map
  map=ggplot(akl_shape)+
    geom_sf(data=akl_shape,fill='grey')+
    geom_sf(data=storeDf,aes(color=Type))+
    scale_color_brewer(palette="Dark2")+
    geom_segment(data=tripMatrix,aes(x=Long,y=Lat,xend=LongEnd,yend=LatEnd),
                 arrow=arrow(length=unit(0.2,'cm')),alpha=0.3)+
    labs(title=paste0(name, 'Routes'))
  return(map)
}
regionClassifier=function(routeFilename,storeDf) {
  #This function classify the route into region for regional plot
  #Input:   routeFilename: String
  #         the LP output file name that we will use
  #         storeDf: dataframe
  #         The data frame for supermarket location either on weekday or Saturday
  #Output:  usedRoute: dataframe
  #         The route and their respective region
  
  #Read the route file
  usedRoute=readLines(routeFilename)
  usedRoute=as.data.frame(usedRoute)
  colnames(usedRoute)='Route'
  usedRoute$Region='Unknown'
  for(i in 1:nrow(usedRoute)) {
    #split the string for the route
    route=str_split(usedRoute[i,1],', ')
    usedRoute[i,2]=filter(storeDf,Store==route[[1]][1])$Region
  }
  return(usedRoute)
}
regionalRoute=function (regional_raster,regional_trips,regional_sat_trips,region_stores) {
  #This function plot regional routes for trips to Woolworth stores
  #Input:   regional_raster: rasterStack or rasterBrick object
  #         The route map raster used for the region
  #         regional_trips: dataframe
  #         The dataframe for the trips within the regions during weekdays
  #         regional_sat_trips: dataframe
  #         The dataframe for the trips within the regions on Saturday
  #         region_stores: dataframe
  #         The dataframe for the store in the region and the Distribution Center
  #Output:  region_map: tmap object
  #         The plot of regional map for weekdays is on the left and for Saturday is on the right

  #Filter the store used on Saturday and the Distribution Centre
  Sat_stores=filter(region_stores,Type%in%c('Countdown','Distribution Centre'))
  distro=filter(region_stores,Type=='Distribution Centre')
  #Plot the base for the regional routes(raster and store location) for each category
  base=tm_shape(regional_raster)+
    tm_rgb()+tm_shape(region_stores)+
    tm_dots(size=0.3,col='Type',palette='Dark2')+
    tm_layout(legend.outside = TRUE)
  base_sat=tm_shape(regional_raster)+
    tm_rgb()+tm_shape(Sat_stores)+
    tm_dots(size=0.3,col='Type',palette='Dark2')+
    tm_layout(legend.outside=TRUE)
  #Get the route to each store in each route of the region, including the route back
  for(i in 1:nrow(regional_trips)) {
    #Split the route into set of Strings
    route=str_split(regional_trips[i,1],', ')
    #Draw the route for each individual trip
    for (j in 1:length(route[[1]])) {
      if(j==1) {
        pointFrom=distro
        pointTo=filter(region_stores,Store==route[[1]][j])
      } else if(j==length(route[[1]])) {
        pointFrom=filter(region_stores,Store==route[[1]][j-1])
        pointTo=distro
      } else {
        pointFrom=filter(region_stores,Store==route[[1]][j-1])
        pointTo=filter(region_stores,Store==route[[1]][j])
      }
      trip=osrmRoute(pointFrom,pointTo)
      #After using osrmRoute, we will have a set of point, so I will connect them together as a linestring and plot them
      trip=st_as_sf(trip,coords=c('lon','lat'),crs=4326)
      triplines=trip%>%summarise(do_union=F)%>%st_cast('LINESTRING')
      base=base+tm_shape(triplines)+tm_lines(col='blue')
    }
  }
  for(i in 1:nrow(regional_sat_trips)) {
    #Split the route into set of Strings
    route=str_split(regional_sat_trips[i,1],', ')
    #Draw the route for each individual trip
    for (j in 1:length(route[[1]])) {
      if(j==1) {
        pointFrom=distro
        pointTo=filter(region_stores,Store==route[[1]][j])
      } else if(j==length(route[[1]])) {
        pointFrom=filter(region_stores,Store==route[[1]][j-1])
        pointTo=distro
      } else {
        pointFrom=filter(region_stores,Store==route[[1]][j-1])
        pointTo=filter(region_stores,Store==route[[1]][j])
      }
      #After using osrmRoute, we will have a set of point, so I will connect them together as a linestring and plot them
      trip_sat=osrmRoute(pointFrom,pointTo)
      trip_sat=st_as_sf(trip_sat,coords=c('lon','lat'),crs=4326)
      triplines_sat=trip_sat%>%summarise(do_union=F)%>%st_cast('LINESTRING')
      base_sat=base_sat+tm_shape(triplines_sat)+tm_lines(col='blue')
    }
  }
  #Plot the 2 maps together
  region_map=tmap_arrange(base,base_sat,ncol = 2)
  return (region_map)
}