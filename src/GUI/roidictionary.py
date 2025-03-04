import numpy as np
import json
from silx.gui.plot.items.roi import (
    PointROI, CrossROI, LineROI, HorizontalLineROI, VerticalLineROI,
    RectangleROI, CircleROI, EllipseROI, PolygonROI, HorizontalRangeROI
)

# Mapping ROI class names to classes.
_ROI_CLASS_MAP = {
    "PointROI": PointROI,
    "CrossROI": CrossROI,
    "LineROI": LineROI,
    "HorizontalLineROI": HorizontalLineROI,
    "VerticalLineROI": VerticalLineROI,
    "RectangleROI": RectangleROI,
    "CircleROI": CircleROI,
    "EllipseROI": EllipseROI,
    "PolygonROI": PolygonROI,
    "HorizontalRangeROI": HorizontalRangeROI,
}


def roi_to_dict(roi):
    """Convert a 2D ROI into a dictionary."""
    d = {
        "class": roi.__class__.__name__,
        "name": roi.getName() if hasattr(roi, "getName") else "",
    }
    # Use the type of ROI to decide what properties to save:
    if hasattr(roi, "__shape"):
        d["color"] = roi.__shape.getColor()
    if isinstance(roi, (PointROI, CrossROI)):
        d["position"] = list(roi.getPosition())
    elif isinstance(roi, LineROI):
        start, end = roi.getEndPoints()
        d["start"] = list(start)
        d["end"] = list(end)
    elif isinstance(roi, (HorizontalLineROI, VerticalLineROI)):
        d["position"] = roi.getPosition()
    elif isinstance(roi, RectangleROI):
        d["origin"] = list(roi.getOrigin())
        d["size"] = list(roi.getSize())
    elif isinstance(roi, CircleROI):
        d["center"] = list(roi.getCenter())
        d["radius"] = roi.getRadius()
    elif isinstance(roi, EllipseROI):
        d["center"] = list(roi.getCenter())
        d["major_radius"] = roi.getMajorRadius()
        d["minor_radius"] = roi.getMinorRadius()
        d["orientation"] = roi.getOrientation()
    elif isinstance(roi, PolygonROI):
        d["points"] = roi.getPoints().tolist()
    elif isinstance(roi, HorizontalRangeROI):
        d["range"] = list(roi.getRange())
    return d


def roi_from_dict(d, plot=None):
    """
    Create an ROI from its dictionary representation.
    
    :param d: Dictionary with ROI properties.
    :param plot: Optional parent plot (passed as parent for ROI creation).
    :return: An ROI instance.
    """
    cls_name = d.get("class")
    cls = _ROI_CLASS_MAP.get(cls_name)
    if cls is None:
        raise ValueError("Unknown ROI class: %s" % cls_name)
    roi = cls(parent=plot)
    # Restore common property if available.
    if "name" in d and hasattr(roi, "setName"):
        roi.setName(d["name"])
    # Set ROI-specific geometry.
    if "color" in d and hasattr(roi, "__shape"):
        roi.__shape.setColor(d["color"])
    if cls_name in ("PointROI", "CrossROI"):
        roi.setPosition(tuple(d["position"]))
    elif cls_name == "LineROI":
        start = np.array(d["start"])
        end = np.array(d["end"])
        roi.setEndPoints(start, end)
    elif cls_name in ("HorizontalLineROI", "VerticalLineROI"):
        roi.setPosition(d["position"])
    elif cls_name == "RectangleROI":
        origin = np.array(d["origin"])
        size = np.array(d["size"])
        roi.setGeometry(origin=origin, size=size)
    elif cls_name == "CircleROI":
        center = np.array(d["center"])
        roi.setGeometry(center=center, radius=d["radius"])
    elif cls_name == "EllipseROI":
        center = np.array(d["center"])
        roi.setGeometry(center=center,
                        radius=(d["major_radius"], d["minor_radius"]),
                        orientation=d["orientation"])
    elif cls_name == "PolygonROI":
        points = np.array(d["points"])
        roi.setPoints(points)
    elif cls_name == "HorizontalRangeROI":
        rng = d["range"]
        roi.setRange(rng[0], rng[1])
    return roi


# Example functions to save and load ROIs to/from a JSON file.

def save_rois_to_file(rois, filename):
    """
    Save a list of ROI objects to a file.
    
    :param rois: List of ROI objects.
    :param filename: Path to the output file.
    """
    rois_data = [roi_to_dict(roi) for roi in rois]
    with open(filename, "w") as f:
        json.dump({"rois": rois_data}, f, indent=4)


def load_rois_from_file(filename, plot=None):
    """
    Load ROIs from a file.
    
    :param filename: Path to the file.
    :param plot: Parent plot widget to pass to each ROI.
    :return: List of ROI objects.
    """
    with open(filename, "r") as f:
        data = json.load(f)
    rois_data = data.get("rois", [])
    rois = [roi_from_dict(d, plot=plot) for d in rois_data]
    return rois
