# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 14:34:01 2018

@author: Waseem
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 00:49:32 2018

@author: Waseem
"""

# import gmplot package 
import gmplot 

def gmap_plot(lat_list, long_list):
    
    latitude_list = [53.327376, 53.32739, 53.327405, 53.327419, 53.327434, 53.327448, 53.32746, 53.327474, 53.327488, 53.327494, 53.327507, 53.327521, 53.327534, 53.327541,53.327554, 53.327561, 53.327573] 
    longitude_list = [6.692222, 6.692293, 6.692365, 6.692436, 6.692507, 6.692578, 6.692632, 6.692704, 6.692775, 6.692806, 6.692877, 6.692949, 6.693021, 6.693057, 6.693129, 6.693171, 6.693243] 
  
    gmap1 = gmplot.GoogleMapPlotter(53.327376, 6.692222, 10) 
    gmap2 = gmplot.GoogleMapPlotter(53.327376, 6.692222, 10) 
  
    # scatter method of map object  
    # scatter points on the google map 
    gmap1.scatter(lat_list, long_list, '# FF0000', size = 40, marker=True) 
  
    # Plot method Draw a line in 
    # between given coordinates 
    gmap1.plot(lat_list, long_list,  
           'cornflowerblue', edge_width=2.5) 

    # heatmap plot heating Type 
    # points on the Google map 
    gmap2.heatmap(lat_list, long_list) 
  
    gmap1.draw("F:\\strukton_project\\figures\\track_groningen1.html") 
    gmap2.draw("F:\\strukton_project\\figures\\track_groningen2.html") 
    
if __name__ == '__main__':
    
    lats = [53.327376, 53.32739, 53.327405, 53.327419, 53.327434, 53.327448, 53.32746, 53.327474, 53.327488, 53.327494, 53.327507, 53.327521, 53.327534, 53.327541,53.327554, 53.327561, 53.327573] 
    longs = [6.692222, 6.692293, 6.692365, 6.692436, 6.692507, 6.692578, 6.692632, 6.692704, 6.692775, 6.692806, 6.692877, 6.692949, 6.693021, 6.693057, 6.693129, 6.693171, 6.693243] 
  
    gmap_plot(lats, longs)