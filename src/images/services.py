from PIL import Image

def optimize_image(path, quality=93):
    """
        Optimize an image with the provided 'quality'.
        path (str): File path of the image to optimize.
        quality (int, optional): Desired quality of the image.
        The function saves the optimized image back at the original path.
    """
    with Image.open(path) as image:
        if image.mode != 'RGB':
            rgb_image = image.convert('RGB')
        else:
            rgb_image = image
        rgb_image.save(path, 
                   'JPEG',
                   optimize=True,
                   quality=quality)


def resize_image(path, width, height):
    """
        Resize an image to specified 'width' and 'height'.
        path (str): File path of the image to resize.
        width, height (int): Desired dimensions of the image.
        The function saves the resized image back at the original path.
    """
    with Image.open(path) as image:
        resized_image = image.resize((width, height))
        resized_image.save(path)