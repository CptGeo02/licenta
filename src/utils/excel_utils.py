from src.libs import *

def apply_modern_design(ws):
    """Aplică un design modern și scalabil, cu alternanța culorilor pe coloane și un grid discret."""
    # Culori pentru coloane impare și pare
    odd_col_fill = PatternFill(start_color="A0C49D", end_color="A0C49D", fill_type="solid")  # Verde închis
    even_col_fill = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")  # Verde deschis
    header_fill = PatternFill(start_color="7CB342", end_color="7CB342", fill_type="solid")  # Verde header

    # Fonturi
    header_font = Font(bold=True, color="FFFFFF")  # Text alb pentru header
    cell_font = Font(color="000000")  # Text negru pentru celule

    # Border finuț pentru grid
    thin_border = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )

    # Stil header
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # Stil pentru celule
    for row in ws.iter_rows(min_row=2):  # Rândurile de date (începând cu al doilea)
        for cell in row:
            col_idx = cell.column  # Indexul coloanei
            if col_idx % 2 == 1:  # Coloană impară
                cell.fill = odd_col_fill
            else:  # Coloană pară
                cell.fill = even_col_fill
            cell.font = cell_font
            cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
            cell.border = thin_border

    # Ajustează dimensiunea coloanelor în funcție de lungimea textului/valorii
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter  # Obține litera coloanei
        for cell in col:
            try:
                if cell.value:  # Asigură-te că valoarea nu e None
                    max_length = max(max_length, len(str(cell.value)))
            except Exception as e:
                print(f"Error resizing cell: {e}")
        adjusted_width = max_length + 8  # Adaugă spațiu extra
        ws.column_dimensions[col_letter].width = adjusted_width

    # Ajustare automată a înălțimii rândurilor
    for row in ws.iter_rows():
        for cell in row:
            if cell.value:
                ws.row_dimensions[cell.row].height = 15 + (len(str(cell.value)) // 15)

    # Returnează worksheet-ul modificat pentru a putea fi utilizat în alte părți ale aplicației
    return ws