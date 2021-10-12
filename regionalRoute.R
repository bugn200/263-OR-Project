regionalRoute=function (regional_raster,regional_trips,regional_sat_trips,region_stores) {
  #This function plot regional routes for trips to Woolworth stores
  Sat_stores=filter(region_stores,Type%in%c('Countdown','Distribution Centre'))
  distro=filter(region_stores,Type=='Distribution Centre')
  #Plot the base for the regional routes(raster and store location)
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
    route=str_split(regional_trips[i,1],',')
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
      trip=st_as_sf(trip,coords=c('lon','lat'),crs=4326)
      triplines=trip%>%summarise(do_union=F)%>%st_cast('LINESTRING')
      base=base+tm_shape(triplines)+tm_lines(col='blue')
    }
  }
  for(i in 1:nrow(regional_sat_trips)) {
    #Split the route into set of Strings
    route=str_split(regional_sat_trips[i,1],',')
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
      trip_sat=osrmRoute(pointFrom,pointTo)
      trip_sat=st_as_sf(trip_sat,coords=c('lon','lat'),crs=4326)
      triplines_sat=trip_sat%>%summarise(do_union=F)%>%st_cast('LINESTRING')
      base_sat=base_sat+tm_shape(triplines_sat)+tm_lines(col='blue')
    }
  }
  region_map=tmap_arrange(base,base_sat,ncol = 2)
  return (region_map)
}