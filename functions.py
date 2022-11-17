import cv2
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

### IMAGES
def display_image(img, window_name='default'):
    cv2.imshow(window_name, img)
    while True:
        k = cv2.waitKey(100)
        if k == 27:
            print('ESC')
            cv2.destroyAllWindows()
            break        
        if cv2.getWindowProperty(window_name,cv2.WND_PROP_VISIBLE) < 1:        
            break            
    cv2.destroyAllWindows()

def generate_masked_images(img, ann):
    mask = np.zeros(img.shape, dtype=np.uint8)
    roi_corners = coco_polyseg_formatted(ann)
    channel_count = img.shape[2]
    ignore_mask_color = (255,)*channel_count
    cv2.fillConvexPoly(mask, roi_corners, ignore_mask_color)

    inv_mask = np.ones(img.shape, dtype=np.uint8) * 255
    ignore_mask_color = 0
    cv2.fillConvexPoly(inv_mask, roi_corners, ignore_mask_color)

    return cv2.bitwise_and(img, mask), cv2.bitwise_and(img, inv_mask)

def remove_true_blacks(img):
    mask = img == 0
    img[mask] = 1

def inverse_blacks(img): # not used
    output = np.copy(img)
    for x, y, z in np.ndindex(img.shape):
        temp = img[x][y]
        if np.sum(temp) == 0:
            output[x][y] = np.array([255, 255, 255])
    return output

def shift_array(lst, displace=1, direction='right'):
    if direction == 'left':
        return np.append(lst[displace:], lst[:displace], axis=0)
    elif direction == 'right':
        return np.append(lst[-displace:], lst[:-displace], axis=0)
    else:
        raise ValueError('Inappropriate direction argument')

def apply_rolling_shutter(masked_img, ann, strategy='right', intensity=.6, cutoff=.6):
    if strategy not in ['left', 'right']:
        raise ValueError(f'Strategy {strategy} is invalid')
    masked_output = np.zeros_like(masked_img)
    xmin, ymin, width, height = get_ann_dims(ann)
    poly = Polygon(coco_to_shapely(ann))
    if strategy == 'right': 
        cutoff_xidx = int(((width - xmin) * cutoff) + xmin)
        for row in range(ymin, ymin + height + 1):
            for col in range(xmin, xmin + width + 1):
                if poly.contains(Point(row, col)):
                    if col < cutoff_xidx:
                        curr_intens = int(np.power(cutoff_xidx - col, intensity))
                        if col + curr_intens < masked_img.shape[1]:
                            masked_output[row, col + curr_intens] = masked_img[row, col]
                        else:
                            masked_output[row, col] = masked_img[row, col]
                    else:
                        masked_output[row, col] = masked_img[row, col]
    else:
        cutoff_xidx = int(((width - xmin) * (1 - cutoff)) + xmin)
        for row in range(ymin, ymin + height + 1):
            for col in range(xmin + height, xmin - 1, -1):
                if poly.contains(Point(row, col)):
                    if col > cutoff_xidx:
                        curr_intens = int(np.power(col - cutoff_xidx, intensity))
                        if col - curr_intens >= 0:
                            masked_output[row, col - curr_intens] = masked_img[row, col]
                        else:
                            masked_output[row, col] = masked_img[row, col]
                    else:
                        masked_output[row, col] = masked_img[row, col]
    return masked_output

def get_ann_dims(ann):
    return int(np.round(ann['bbox'][0])), int(np.round(ann['bbox'][1])), int(np.round(ann['bbox'][2])), int(np.round(ann['bbox'][3])) # xmin, ymin, width, height

def fill_inv_masked(inv_masked_img, ann, strategy='right'): # when strategy='right', pull from left; when strategy='left', pull from right
    output = np.copy(inv_masked_img)

    xmin, ymin, width, height = get_ann_dims(ann)
    id = ann['id']
    atLeft, atRight = False, False

    if strategy not in ['left', 'right']:
        raise ValueError(f'Strategy {strategy} is invalid')

    if xmin == 0: # at left side of image
        atLeft = True
    if xmin + width == inv_masked_img.shape[1]: # at right side of image
        atRight = True
    
    if atLeft:
        if atRight:
            raise ValueError(f'Image #{id} takes up entire image width, cannot fill')
        else:
            strategy='left'
    elif atRight:
        strategy='right'

    if strategy == 'right': # pull from left
        for row in np.arange(ymin, ymin + height):
            blacks = np.sort(np.array(list(set(np.where(output[row] == np.array([0, 0, 0]))[0]))))
            if(len(blacks) > 0):
                low = 2 * blacks[0] - 1 - blacks[-1]
                high = blacks[0]
                foo = np.flip(output[row][low:high], axis=0)
                if(low < 0):
                    foo = np.pad(np.flip(output[row][0:high], axis=0), ((0, -low), (0, 0)), mode='reflect')
                output[row][blacks[0]:blacks[-1] + 1] = foo
    else: # pull from right
        for row in np.arange(ymin, ymin + height):
            blacks = np.sort(np.array(list(set(np.where(output[row] == np.array([0, 0, 0]))[0]))))
            if(len(blacks) > 0):
                low = blacks[-1] + 1
                high = 2 * blacks[-1] + 2 - blacks[0] 
                foo = np.flip(output[row][low:high], axis=0)
                if(high > output.shape[1]):
                    foo = np.pad(np.flip(output[row][low:output.shape[1]], axis=0), ((0, high - output.shape[1]), (0, 0)), mode='reflect')
                output[row][blacks[0]:blacks[-1] + 1] = foo
    return output

def recombine_masked_imgs(masked_img, inv_masked_img):
    output = np.copy(inv_masked_img)
    mask = masked_img > 0
    output[mask] = masked_img[mask]
    return output
    


### COCO

def coco_polyseg_formatted(ann):
    arr = []
    temp = ann['segmentation'][0]
    for i in range(int(len(temp) / 2)):
        arr.append([temp[2 * i], temp[2 * i + 1]])
    return np.array(arr).astype(np.int32)

def coco_to_shapely(ann):
    arr = []
    temp = ann['segmentation'][0]
    for i in range(int(len(temp) / 2)):
        arr.append([temp[2 * i + 1], temp[2 * i]])
    return np.array(arr).astype(np.int32)

### OLD/DEPRECATED

""" def apply_rolling_shutter(masked_img, ann, interval=5, strategy='right'): # v1
    masked_output = np.copy(masked_img)

    ymin = int(np.round(ann['bbox'][1]))
    ymax = int(np.round(ann['bbox'][1] + ann['bbox'][3]))

    for row in np.arange(ymin, ymax):
        masked_output[row] = shift_array(masked_output[row], int(row / interval), direction=strategy)
    
    return masked_output """

""" def fill_inv_masked(inv_masked_img, ann):
    output = np.copy(inv_masked_img)

    ymin = int(np.round(ann['bbox'][1]))
    ymax = int(np.round(ann['bbox'][1] + ann['bbox'][3]))

    for row in np.arange(ymin, ymax):
        blacks = np.sort(np.array(list(set(np.where(output[row] == np.array([0, 0, 0]))[0]))))
        mdpt = blacks[int(len(blacks) / 2)]
        left_len = mdpt - blacks[0]
        right_len = blacks[-1] - mdpt
        left_arr = np.flip(output[row][blacks[0] - left_len:blacks[0]], axis=0)
        right_arr = np.flip(output[row][blacks[-1] + 1:blacks[-1] + right_len + 2], axis=0)
        output[row][blacks[0]:mdpt] = left_arr
        output[row][mdpt:blacks[-1] + 1] = right_arr 
        
        return output"""