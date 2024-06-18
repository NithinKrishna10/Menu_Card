import qrcode
from io import BytesIO


def generate_qr_code(url):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"{url}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer,"PNG")
    buffer.seek(0)
    img.save("filename.png")    
    return "filename.png"
   
generate_qr_code("ht")