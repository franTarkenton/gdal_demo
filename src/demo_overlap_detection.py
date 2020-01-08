"""Simple example of using GDAL to identify overlaps"""

import osgeo.ogr as ogr


def getFGDBDataset(dataset_path):
    """Gets the path to an ESRI file geodatabase and returns a ogr dataset
    object

    :return: an ogr dataset object that wraps the provided path to a file
    geodatabase folder
    :rtype: ogr.dataset
    """
    # proprietary esri driver, requires extra steps to install / make avail
    driver = ogr.GetDriverByName("FileGDB")
    # opensource driver
    driver = ogr.GetDriverByName("OpenFileGDB")
    ds = driver.Open(dataset_path, 0)
    # print(f'ds: {ds}')
    return ds


def getFeatures(dataset):
    """
    :param dataset: a ogr dataset object
    :return: list feature names
    """
    featsClassList = []
    for featsClass_idx in range(ds.GetLayerCount()):
        featsClass = ds.GetLayerByIndex(featsClass_idx)
        featsClassList.append(featsClass.GetName())

    featsClassList.sort()
    return featsClassList


def count_features(feature_class):
    """Demo's how to iterate through every feature in a feature_class, in this
    example counts the features

    :param feature_class: input ogr feature class
    :type feature_class: ogr.feature_class
    :return: a count of how many features exist in the feature_class
    :rtype: int
    """
    # shows how to iterate over... you can also get the count
    # using GetFeatureCount method.
    cnt = 0
    # for feat in feature_class:
    #     cnt += 1
    # return cnt

    # pip bindings work around
    feat = feature_class.GetNextFeature()
    while feat is not None:
        cnt += 1
        feat = feature_class.GetNextFeature()


def getAttributes(feature_class):
    """Prints the names of all the attributes associated with the feature_class

    :param feature_class: input feature class
    :type feature_class: ogr.feature_class
    """
    layerDefinition = feature_class.GetLayerDefn()

    for i in range(layerDefinition.GetFieldCount()):
        print(layerDefinition.GetFieldDefn(i).GetName())


def getOverlaps(feature_class, start_num=1, overlaps=[]):
    """Iterates over every feature in the feature_class and checks to see if
    it overlaps with other features in the same dataset.

    :return: a list of feature objects that overlap other features in the same
             dataset
    :rtype: list
    """
    # need to compare each feature with every other feature to identify
    # overlaps.
    total_features = feature_class.GetFeatureCount()
    print(f"completed: {start_num} of {total_features}")
    start_feature = feature_class.GetFeature(start_num)
    start_feat_geom = start_feature.GetGeometryRef()
    start_num += 1
    for counter in range(start_num, total_features + 1):
        is_overlapping_feature = feature_class.GetFeature(counter)
        is_over_feat_geom = is_overlapping_feature.GetGeometryRef()
        result_geom = start_feat_geom.Intersection(is_over_feat_geom)

        if result_geom.GetGeometryCount():
            overlaps.append([start_num, counter])
    if start_num >= total_features:
        return overlaps
    else:
        overlaps = getOverlaps(feature_class, start_num, overlaps)
        return overlaps


def getOverlaps2(feature_class, start_num=1, overlaps=[], boundingBoxes={}):
    """Using bb to test for overlap first."""

    total_features = feature_class.GetFeatureCount()
    print(f"completed: {start_num} of {total_features}, overlaps: {len(overlaps)}")
    start_feature = feature_class.GetFeature(start_num)
    start_feat_geom = start_feature.GetGeometryRef()
    boundingBoxes[str(start_num)] = bb_to_geometry(start_feat_geom.GetEnvelope())
    current_feature_bb = boundingBoxes[str(start_num)]
    start_num += 1
    for counter in range(start_num, total_features + 1):
        is_overlapping_feature = feature_class.GetFeature(counter)

        is_over_feat_geom = is_overlapping_feature.GetGeometryRef()
        if counter not in boundingBoxes:
            boundingBoxes[counter] = bb_to_geometry(is_over_feat_geom.GetEnvelope())

        if current_feature_bb.Intersection(boundingBoxes[counter]):
            # now do actual intersect
            result_geom = start_feat_geom.Intersection(is_over_feat_geom)
            if not result_geom.IsEmpty():
                # print(f'overlap detected: {result_geom.GetGeometryCount()}')
                overlaps.append([start_num, counter])
    if start_num >= total_features:
        # if start_num >= 10:
        print(f"overlaps: {overlaps}")
        return overlaps
    else:
        overlaps = getOverlaps2(
            feature_class, start_num, overlaps=overlaps, boundingBoxes=boundingBoxes
        )
        return overlaps


def bb_to_geometry(bb):
    """
    Getting the bounding box tuple and converting to a geometry so can be
    compared with other geometries
    """
    (minX, maxX, minY, maxY) = bb
    # print(minX, maxX, minY, maxY)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(minX, minY)
    ring.AddPoint(maxX, minY)
    ring.AddPoint(maxX, maxY)
    ring.AddPoint(minX, maxY)
    ring.AddPoint(minX, minY)
    polygon_env = ogr.Geometry(ogr.wkbPolygon)
    polygon_env.AddGeometry(ring)
    return polygon_env


if __name__ == "__main__":
    dataSetPath = r"/mnt/c/Kevin/proj/gdal/data/BCTS_OPERATING_AREAS_SP.gdb"
    ds = getFGDBDataset(dataSetPath)
    feature_list = getFeatures(ds)

    print(f"feature classes in the dataset: {feature_list}")
    featureClassName = r"WHSE_FOREST_TENURE_BCTS_OPERATING_AREAS_SP"

    featsClass = ds.GetLayerByName(featureClassName)

    feature_cnt = count_features(featsClass)
    print(f"features in feature class: {feature_cnt}")

    getAttributes(featsClass)
    # overlaps = getOverlaps(featsClass)
    ov = getOverlaps2(featsClass)
    print(f"overlaps: {ov}")

