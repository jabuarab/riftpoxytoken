from PIL import Image, ImageDraw
import PIL.JpegImagePlugin  # Pillow 12+ lazy-loads plugins; PdfImagePlugin needs JPEG registered
import math


def create_printable_pdf(
    image_specs,
    output_path="output.pdf",
    page_size="A4",  # "A4" or "LETTER"
    dpi=300,
    margin_mm=10,
    gap_px=3,
    draw_cut_lines=True,
):
    # --- Page size in mm ---
    if page_size.upper() == "A4":
        page_w_mm, page_h_mm = 210, 297
    elif page_size.upper() == "LETTER":
        page_w_mm, page_h_mm = 216, 279
    else:
        raise ValueError("Unsupported page size")

    def mm_to_px(mm):
        return int(mm * dpi / 25.4)

    page_w = mm_to_px(page_w_mm)
    page_h = mm_to_px(page_h_mm)
    margin = mm_to_px(margin_mm)

    card_w = int(63 * dpi / 25.4)
    card_h = int(88 * dpi / 25.4)

    # --- Expand images ---
    expanded = []
    for path, count in image_specs:
        expanded.extend([path] * count)

    pages = []
    idx = 0

    while idx < len(expanded):
        page = Image.new("RGB", (page_w, page_h), "white")
        draw = ImageDraw.Draw(page)

        usable_w = page_w - 2 * margin
        usable_h = page_h - 2 * margin

        cols = max(1, (usable_w + gap_px) // (card_w + gap_px))
        rows = max(1, (usable_h + gap_px) // (card_h + gap_px))

        for r in range(rows):
            for c in range(cols):
                if idx >= len(expanded):
                    break

                path = expanded[idx]
                img = Image.open(path)

                if img.mode == "RGBA":
                    bg = Image.new("RGB", img.size, "white")
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                img = img.resize((card_w, card_h), Image.LANCZOS)

                x = margin + c * (card_w + gap_px)
                y = margin + r * (card_h + gap_px)

                page.paste(img, (x, y))

                idx += 1

        if draw_cut_lines:
            grid_w = cols * card_w + (cols - 1) * gap_px
            grid_h = rows * card_h + (rows - 1) * gap_px

            # Full-width horizontal lines at each row boundary
            for r in range(rows + 1):
                line_y = margin + r * (card_h + gap_px) - (gap_px // 2 if r > 0 else 0)
                draw.line([(0, line_y), (page_w, line_y)], fill="black", width=1)

            # Full-height vertical lines at each column boundary
            for c in range(cols + 1):
                line_x = margin + c * (card_w + gap_px) - (gap_px // 2 if c > 0 else 0)
                draw.line([(line_x, 0), (line_x, page_h)], fill="black", width=1)

        pages.append(page)

    # --- Save as PDF ---
    pages[0].save(output_path, save_all=True, append_images=pages[1:], resolution=dpi)

    print(f"Saved PDF: {output_path}")


images = [
    ("goldred.png", 9),
    ("goldblue.png", 9),
    ("casterR.png", 9),
    ("casterb.png", 9),
]

create_printable_pdf(
    images,
    output_path="cards3.pdf",
    page_size="A4",
    dpi=300,
    margin_mm=10,
    draw_cut_lines=True,
)
