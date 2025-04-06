def filter_detections(detections, overlap_threshold=0.2):
    """
    Filtrează detectările pentru a elimina suprapunerile dintre obiectele detectate.

    Parametri:
    - detections: o listă de detectări, fiecare fiind un dicționar cu chei precum `class`, `box`, și `confidence`.
    - overlap_threshold: pragul de suprapunere (IOU) peste care două detectări sunt considerate redundant suprapuse.

    Returnează:
    - O listă de detectări filtrate.
    """
    filtered_detections = []  # Lista pentru detectările filtrate

    for i, det1 in enumerate(detections):
        keep = True  # Presupunem că detectarea curentă trebuie păstrată
        for j, det2 in enumerate(detections):
            # Verificăm doar detectările care sunt de aceeași clasă și nu sunt identice
            if i != j and det1['class'] == det2['class']:
                # Calculăm IOU între cele două box-uri
                iou = calculate_iou(det1['box'], det2['box'])
                # Dacă suprapunerea este prea mare și încrederea det1 este mai mică decât det2
                if iou > overlap_threshold:
                    if det1['confidence'] < det2['confidence']:
                        keep = False  # Marcam det1 pentru eliminare
                        break  # Ieșim din buclă pentru a verifica următoarea detectare
        if keep:
            filtered_detections.append(det1)  # Adăugăm detectarea la lista finală

    return filtered_detections  # Returnăm lista de detectări filtrate

def calculate_iou(box1, box2):
    """
    Calculează Intersect Over Union (IOU) între două box-uri.

    Parametri:
    - box1: coordonatele primului box (x1, y1, x2, y2).
    - box2: coordonatele celui de-al doilea box (x1, y1, x2, y2).

    Returnează:
    - Valoarea IOU (un număr între 0 și 1).
    """
    # Calculăm colțurile zonei de intersecție
    x1_inter = max(box1[0], box2[0])  # Stânga sus (max x1)
    y1_inter = max(box1[1], box2[1])  # Stânga sus (max y1)
    x2_inter = min(box1[2], box2[2])  # Dreapta jos (min x2)
    y2_inter = min(box1[3], box2[3])  # Dreapta jos (min y2)

    # Calculăm aria de intersecție
    inter_area = max(0, x2_inter - x1_inter) * max(0, y2_inter - y1_inter)

    # Calculăm ariile celor două box-uri
    box1_area = calculate_area(box1)
    box2_area = calculate_area(box2)

    # Calculăm aria de uniune
    union_area = box1_area + box2_area - inter_area

    # Calculăm IOU
    iou = inter_area / union_area if union_area > 0 else 0
    return iou

def calculate_area(box):
    """
    Calculează aria unui box.

    Parametri:
    - box: coordonatele box-ului (x1, y1, x2, y2).

    Returnează:
    - Aria box-ului.
    """
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)  # Lățime * Înălțime