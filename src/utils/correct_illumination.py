import cv2
import numpy as np

def correct_illumination(frame, enable_denoise=True, clahe_clip=2.0, clahe_tile_size=8):
    """
    Corectează iluminarea imaginii pentru detecție AI robustă în condiții variabile de lumină.
    Aplicații: YOLO, analiză vizuală, supraveghere inteligentă.
    Include: CLAHE, gamma adaptiv, normalizare tonuri, denoising inteligent.

    :param frame: imaginea de intrare (BGR)
    :param enable_denoise: aplică denoising doar în condiții critice
    :param clahe_clip: valoare pentru limitarea contrastului în CLAHE
    :param clahe_tile_size: dimensiunea pătrată a fiecărui tile (X și Y egale)
    :return: imaginea preprocesată
    """
    # Validare sigură pentru tile size
    if not isinstance(clahe_tile_size, int) or clahe_tile_size < 1:
        clahe_tile_size = 8

    # Conversie în LAB pentru analiză precisă a luminozității
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Analiză luminozitate și contrast
    l_mean, l_std = np.mean(l), np.std(l)

    # CLAHE - corecție locală a contrastului
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(clahe_tile_size, clahe_tile_size))
    l_clahe = clahe.apply(l)

    # Îmbinare cu componentele originale de culoare
    lab_clahe = cv2.merge((l_clahe, a, b))
    frame_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

    # Gamma adaptiv - optimizare pentru interval larg de iluminare
    gamma = np.interp(l_mean, [30, 80, 180, 240], [2.2, 1.6, 1.0, 0.8])
    inv_gamma = 1.0 / gamma
    gamma_table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(256)]).astype("uint8")
    frame_gamma = cv2.LUT(frame_clahe, gamma_table)

    # Normalizare tonuri - opțională pentru stabilizare culoare
    frame_norm = cv2.normalize(frame_gamma, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    # Reducere zgomot (aplicată doar în condiții de lumină critică)
    if enable_denoise and (l_mean < 50 or l_mean > 200 or l_std < 10):
        frame_norm = cv2.fastNlMeansDenoisingColored(frame_norm, None, 10, 10, 7, 21)

    return frame_norm
