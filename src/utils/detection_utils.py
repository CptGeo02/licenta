def filter_detections(detections, overlap_threshold=0.4):
    filtered_detections = []

    for i, det1 in enumerate(detections):
        keep = True
        for j, det2 in enumerate(detections):
            if i != j and det1['class'] == det2['class']:
                iou = calculate_iou(det1['box'], det2['box'])
                if iou > overlap_threshold:
                    if det1['confidence'] < det2['confidence']:
                        keep = False
                        break
        if keep:
            filtered_detections.append(det1)

    return filtered_detections

def calculate_iou(box1, box2):
    x1_inter = max(box1[0], box2[0])
    y1_inter = max(box1[1], box2[1])
    x2_inter = min(box1[2], box2[2])
    y2_inter = min(box1[3], box2[3])

    inter_area = max(0, x2_inter - x1_inter) * max(0, y2_inter - y1_inter)
    box1_area = calculate_area(box1)
    box2_area = calculate_area(box2)

    union_area = box1_area + box2_area - inter_area
    iou = inter_area / union_area if union_area > 0 else 0
    return iou

def calculate_area(box):
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)
