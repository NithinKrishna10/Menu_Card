import qrcode
from io import BytesIO
from PIL import Image
from ..external.s3_bucket import S3Utils

def generate_qr_code(url: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert the img to PIL Image
    img = img.convert("RGB")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    s3_object = S3Utils() 

    return s3_object.upload_image_to_s3(name="qr-code", file=buffer)
