'''
Created on 10 Jun 2017

@author: rob
'''
import struct
import os

def save_image(filename, img_data, bpp, width, height):
    # output a bitmap file, because it's pretty simple
    #filename = "output%s.bmp"
    
    # allow an incrementing directory count filename
    # NOTES: race conditions exist for multiple instances, security implications? 
    if '%s' in filename:
        i = 0
        while os.path.exists(filename % i):
            i += 1
        filename = filename % i

    # now save the image as BMP
    with open(filename, 'wb') as f:
        f.write(b'BM')
        # BITMAPFILEHEADER
        img_size = 4 * width * height
        f.write(struct.pack( '<LLL', img_size + 14 + 40, 0, 14+40 ))
        # BITMAPINFOHEADER
        f.write(struct.pack('<LLLHHLLLLLL', 40, 
                            width, height,
                            1, # planes
                            32, # bits per pixel - avoid padding rows to 4 bytes
                            0, # compression 
                            0, #img_size, # image size, could be 0 for BI_RGB bitmapss
                            0, #2835, # x pixels per meter, =72DPI, could be zero
                            0, #2835, # y pixels per meter
                            0, # colours in colour table
                            0 # important colour count
                            ))
        
        if bpp != 24:
            # b,g,r,a
            # write bottom row to top
            for y in range(height-1, -1, -1):
                line = width * y
                for x in range(width):
                    data = img_data[x+line]
                    f.write(struct.pack('BBBB', data, data, data, 255))
        else:
            # b,g,r,a
            # write bottom row to top
            for y in range(height-1, -1, -1):
                line = width * 3 * y
                for x in range(width):
                    r = img_data[x * 3 + line]
                    g = img_data[x * 3 + line + 1]
                    b = img_data[x * 3 + line + 2]
                    f.write(struct.pack('BBBB', b, g, r, 255))
