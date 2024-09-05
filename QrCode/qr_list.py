import qrcode

images = []

for i in range(1, 1001):
    image = qrcode.make(f"https://t.me/yourbotuser?start={i}")

    image = image.convert('RGB')

    images.append(image)

images[0].save('QR_codes.pdf', save_all=True, append_images=images[1:])
