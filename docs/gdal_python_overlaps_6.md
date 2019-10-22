# Detecting Overlaps

<IMG src="https://lh3.googleusercontent.com/jMzaCL8EgFOESQ0RiuB7w2GZl_8lxy5UjDba9uJuzP-nr2hL7DILFf8XwgkU3lupl0n5PF0v5AYjZ4wM-fmag1DZIIW0J2QuNmhj7p7kgf9eGyhjqUaI1V-4km14--NwT13M3IqZHWTFvCYOSI2eGsE6sA44-FA9_E8s4lhe9964f4WMSRsGRuwTZFyMwN9SjSRLV7n2R1O7BaPiJmD9uXi3zkC35LLqPb8sByyOUCTjs_ApyKB-1NFG34EBKrK08e08fXpDOnpDBHV2XuVcw-7UafL5tFiM4TcTqYBOv0-DJFWmkk1ySD57bnjnmZFAfpN0H5tzEF9GN_jQabvbqcVc3Dv1qU6iRemeZyuIklh-_hLJyP-ntmIapRkuwAqKSrDwiK2FiKxF0og5sqmQzgCab32qCoaVP3fOaE09N3YRGSULVGOEKY-M_v9cFNUyba2m1Hw9N7ProNdGqU3635lY-WduBoVezEL18WCzb17pTPpVwRhstT8rC05mxid45Nw4r_qET5PfsB005_dA0xw6aRXsqS4L3VRiwCroRsbStvQCleR4s2kLrLQIE_P7NHzv5hs8CroUtq_wP3BTWXetq2EeBjEdYa1_-AwGxg7nblTkKFy3eg2dbUmZ0VKMzXMjY9S-wAah57PyZYoLSEOmq5xALb5aZBENs1JUiLst7neLJwlT24c7HnmBXpKm34SPqsIfmn5Ns3jCbSjfF7g16ztRAERSwr-HSdYK4eUMpe5n=w1563-h879-no" width=450>


# Conceptual Model / Steps:

1. Define Driver
1. Define Datasource
1. Define Layer
1. Iterate over features in Layer
1. Get feature geometry
1. Assess for overlap each feature with every other feature

# Easy Stuff

* previous examples demo up to Step 4

[Ran out of time, lets look at the code](../demo_overlap_detection.py)


# Next Steps

* speed! Problem could easily be processed in parallel
  * [uvicorn](http://www.uvicorn.org/)
* look into using shapely or fiona
* bulk processing features instead of individually
* [rtree module](http://toblerity.org/rtree/)
* other?


Other useful links:
* [back to object hierarchy](gdal_python.md)
* [GDAL Api Docs](https://gdal.org/python/index.html)



[Conclusion / Summary](summary_7.md)

