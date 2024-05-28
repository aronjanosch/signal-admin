import qrcode

def generate_qr_code(data):
    """
    Generates a QR code image based on the provided data.

    Args:
        data (str): The data to be encoded in the QR code.

    Raises:
        Exception: If there is an error generating the QR code.

    Returns:
        None
    """
    try:
        # Generate the QR code image
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qr_code.png")
        print("QR code generated and saved as 'qr_code.png'")
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")