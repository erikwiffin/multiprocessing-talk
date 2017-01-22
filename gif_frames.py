from PIL import Image, ImageChops, GifImagePlugin


def is_partial_frame(img):
    if not img.tile:
        return False

    return img.tile[0][1][2:] != img.size


def read_frames(orig):
    ''' Generator that yields each frame in an animated GIF.
    '''
    # Get some defaults out of the first frame
    palette = orig.getpalette()
    prev_frame = orig.convert('RGBA')

    while True:
        # Each frame may not store it's own palette, but we can just use the
        # one from the first frame.
        if not orig.getpalette():
            orig.putpalette(palette)

        # Create a new image the same size as the current frame
        current_frame = Image.new('RGBA', orig.size)

        # To save space, GIF frames only contain changes.
        # Paste the previous frame into our current image so we can apply the
        # changes on top of that.
        if is_partial_frame(orig):
            current_frame.paste(prev_frame)

        # Paste the current frame into our image
        current_frame.paste(orig, (0, 0), orig.convert('RGBA'))

        yield current_frame

        # We're moving on to the next frame now.
        prev_frame = current_frame

        # Pillow doesn't extract a frame count, so we seek one frame at a time
        # until we get an End Of File error.
        try:
            orig.seek(orig.tell() + 1)
        except EOFError:
            break


def int_to_bin(i):
    i1 = i % 256
    i2 = int(i / 256)

    return bytes('{:c}{:c}'.format(i1, i2), 'latin-1')


def header_block():
    pieces = [
        b'GIF',  # signature
        b'89a',  # version
    ]

    return b''.join(pieces)


def logical_screen_descriptor(img, packed_bit):
    img_x, img_y = img.size

    pieces = [
        int_to_bin(img_x),  # canvas width
        int_to_bin(img_y),  # canvas height
        # Just use the packed_bit from the original image
        packed_bit,
        b'\x00',  # background color index
        b'\x00',  # pixel aspect ratio
    ]

    return b''.join(pieces)


def application_ext(loops=0):
    pieces = [
        b'\x21',  # extension introducer
        b'\xff',  # extension label
        b'\x0b',  # block size
        b'NETSCAPE',  # application identifier
        b'2.0',  # application authentication code
        b'\x03',  # block size
        b'\x01',  # ???
        int_to_bin(loops),  # number of repeats
        b'\x00',  # block terminator
    ]

    return b''.join(pieces)


def write_frames(handle, frames):
    prev_frame = None

    for img in frames:
        if not prev_frame:
            # We need to write some special headers in the first frame
            header, used_palette_colors = GifImagePlugin.getheader(img)
            del used_palette_colors

            handle.write(header_block())
            handle.write(logical_screen_descriptor(img, header[1]))
            handle.write(header[3])
            handle.write(application_ext())

            for block in GifImagePlugin.getdata(img):
                handle.write(block)
        else:
            delta = ImageChops.subtract_modulo(img, prev_frame)
            bbox = delta.getbbox()

            if bbox:
                data = GifImagePlugin.getdata(img.crop(bbox), offset=bbox[:2])
                for s in data:
                    handle.write(s)

        prev_frame = img.copy()

    handle.write(b'\x3b')  # trailer block
