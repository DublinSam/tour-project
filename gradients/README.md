###Gradient Estimation

The goal of this code is to produce an estimate of the gradient at any point in a 2014 Tour de France stage.  

* The initial approach (which appears in `approximate`) was to use the stage profile images released at the start of the race. This works reasonably well as a first approximation.
* The second approach (which appears in `accurate`) calculates gradients from a combination of route data collected from Strava (found [here](http://blog.strava.com/tour-de-france-2014/)) and evelation collected from (ride-with-gps)[http://ridewithgps.com/].  This produces a much more accurate estimate of the gradient at each point.
