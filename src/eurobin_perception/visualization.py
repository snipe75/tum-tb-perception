#!/usr/bin/env python3

"""
Contains functions for visualizing detection model results e.g. images
annotated with detection bounding boxes, etc.
"""

import os
import yaml

import cv2
import numpy as np
import seaborn as sns             # Only used for its color maps
import matplotlib.pyplot as plt

CV2_BBOX_FONT = cv2.FONT_HERSHEY_PLAIN
CV2_BBOX_FONT_SCALE = 1.0

CV2_BBOX_FONT = cv2.FONT_HERSHEY_SIMPLEX
CV2_BBOX_FONT_SCALE = 0.5

def load_class_color_map(class_colors_config_file_path):
    """
    Loads and returns a mapping between class names and their color values
    from a YAML config file.
    The file is expected to contain a key for each class, whose value is a list
    of (R, G, B) values in the range [0., 255.].

    Parameters
    ----------
    class_colors_config_file_path: str
        Absolute path to config file

    Returns
    -------
    class_colors_dict: dict
        Map between class names and (R, G, B) color tuples (0-255)
    """
    with open(class_colors_config_file_path, 'r') as filehandle:
        class_colors_dict = yaml.safe_load(filehandle)
        
    return class_colors_dict
  
def get_class_color(class_colors_dict, class_str):
    """
    Returns a color value for a given class: a list of floats in
    (0., 255.) representing RGB values, from a given dict that maps
    class string to RGB arrays.
    
    If the given class string is not found in the dict, the function
    returns a random color value.

    Parameters
    ----------
    class_str: str
        String that identifies the desired class
    class_colors_dict: dict
        Map between class names and (R, G, B) color tuples (0-255)

    Returns
    -------
    class_color: list
        Floats representing RGB values.
    """
    try:
        return class_colors_dict[class_str]
    except KeyError:
        print('[WARN] Class string {} not found in color values dict.'.format(class_str))
        print('[WARN] Assigning a random color value.')
        
        return list(np.random.random(3) * 255.)
    
def annotate_image(image, bboxes, class_colors_dict):
    """
    Returns an annotated version of the input image, containing:
      - bounding boxes
      - text labels (slightly transparent to avoid occlusions)

    Parameters
    ----------
    image: numpy.ndarray
        BGR image array.
    bboxes: list
        Dicts containing info on each bbox (class, xmin, ymin, xmax, ymax, confidence)
    class_colors: dict
        Map between class names and (R, G, B) color tuples (0-255)

    Returns
    -------
    image_annotated: numpy.ndarray
        BGR image array, post-annotation.
    """
    
    image_annotated = np.copy(image)
    
    for bbox in bboxes:
        label = bbox['class']
        color = get_class_color(class_colors_dict, label)

        # Draw bbox rectangle:
        image_annotated = cv2.rectangle(image_annotated, 
                                        (bbox['xmin'], bbox['ymin']), 
                                        (bbox['xmax'], bbox['ymax']),
                                        color=color, thickness=2)

        # Construct label text:
        confidence = bbox['confidence']
        label_str = label
        if confidence is not None:
            label_str += ': {:.2f}%'.format(float(confidence))

        # Estimate area of label box:
        (w, h), _ = cv2.getTextSize(label_str, CV2_BBOX_FONT, 
                                    CV2_BBOX_FONT_SCALE, 1)
        
        # Draw faded label box and text:
        image_overlay = np.copy(image_annotated)
        image_overlay = cv2.rectangle(image_overlay, 
                                      (bbox['xmin'], bbox['ymin'] - int(h * 1.5)), 
                                      (bbox['xmin'] + w, bbox['ymin']), 
                                      color, -1)
        image_overlay = cv2.putText(image_overlay, label_str, 
                                    (bbox['xmin'], bbox['ymin'] - 5),
                                    CV2_BBOX_FONT, CV2_BBOX_FONT_SCALE, 
                                    (255, 255, 255), 1)
        alpha = 0.5
        cv2.addWeighted(image_overlay, alpha, image_annotated, 
                        1 - alpha, 0, image_annotated)
        
    return image_annotated

def view_image_cv(image, window_title=''):
    """
    Views the input image in an OpenCV window.
    The window can be closed by pressing any button.

    Parameters
    ----------
    image: numpy.ndarray
        BGR image array.
    window_title: str
        Text to title the window, if any.

    Returns
    -------
    None
    """
    cv2.imshow(window_title, image)
    cv2.waitKey(); cv2.destroyAllWindows()

# TODO: Implement function to view image using plt