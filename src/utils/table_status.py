from src.utils.detection_utils import calculate_iou
from src.utils.detection_utils import calculate_area

def check_table_status(table_box, detections, red_threshold=0.1, blue_threshold=0.1):
    red_objects = []
    blue_objects = []
    
    for det in detections:
        if det['class'] in range(39, 56):  # Red objects (bottle, wine glass, etc.)
            red_objects.append(det)
        elif det['class'] == 0:  # Persons
            blue_objects.append(det)

    table_area = calculate_area(table_box)
    red_count = 0
    blue_count = 0

    for red in red_objects:
        red_area = calculate_area(red['box'])
        red_iou = calculate_iou(table_box, red['box'])
        if red_iou >= red_threshold * (red_area / table_area):
            red_count += 1

    for blue in blue_objects:
        blue_area = calculate_area(blue['box'])
        blue_iou = calculate_iou(table_box, blue['box'])
        if blue_iou >= blue_threshold * (blue_area / table_area):
            blue_count += 1

    if red_count > 0 and blue_count == 0:
        return "need to clean"
    elif red_count == 0 and blue_count == 0:
        return "available"
    elif blue_count > 0 and red_count == 0:
        return "ready to order"
    elif blue_count > 0 and red_count > 0:
        return "eating"
    
    return "unknown"
