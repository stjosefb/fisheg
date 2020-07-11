import base64
import json
import numpy as np

from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
from skimage import measure
from shapely.geometry import Polygon


# ## PUBLIC


def img_content_change_mask_color_solid(img_content_mask):
    img_mask = Image.open(BytesIO(img_content_mask)).convert('L')
    img_mask_invert = ImageOps.invert(img_mask)
    buffered = BytesIO()
    img_mask_invert.save(buffered, format="PNG")
    im_bytes = buffered.getvalue()

    return im_bytes


def img_base64_change_mask_color_transparent(img_base64):
    encoded_elmts_img_base64 = img_base64.split(',', 1)
    img_content = base64.decodebytes(encoded_elmts_img_base64[1].encode('ascii'))

    img_content_new = img_content_change_mask_color_transparent(img_content)

    img_base64_new = ("data:" +
                        "image/png" + ";" +
                        "base64," + base64.b64encode(img_content_new).decode('ascii'))

    return img_base64_new

    # im = Image.open(BytesIO(img_content))
    # im = im.convert('RGBA')
    #
    # data = np.array(im)  # "data" is a height x width x 4 numpy array
    # red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability
    #
    # # Replace white with red... (leaves alpha values alone...)
    # white_areas = (red > 0) & (blue > 0) & (green > 0)
    # black_areas = (red == 0) & (blue == 0) & (green == 0)
    # #data[..., :-1][black_areas.T] = (255, 255, 255)  # Transpose back needed
    # data[...][black_areas.T] = (255, 255, 255, 0)  # Transpose back needed
    # data[..., :-1][white_areas.T] = (128, 0, 0)  # Transpose back needed
    #
    # im_new = Image.fromarray(data)
    #
    #
    # buffered = BytesIO()
    # im_new.save(buffered, format="PNG")
    # im_new_bytes = buffered.getvalue()
    #
    # img_base64_new = ("data:" +
    #                     "image/png" + ";" +
    #                     "base64," + base64.b64encode(im_new_bytes).decode('ascii'))
    # #img_base64_new = '#'
    # return img_base64_new


def img_content_change_mask_color_transparent(img_content):
    im = Image.open(BytesIO(img_content))
    im = im.convert('RGBA')

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    white_areas = (red > 0) & (blue > 0) & (green > 0)
    black_areas = (red == 0) & (blue == 0) & (green == 0)
    #data[..., :-1][black_areas.T] = (255, 255, 255)  # Transpose back needed
    data[...][black_areas.T] = (255, 255, 255, 0)  # Transpose back needed
    data[..., :-1][white_areas.T] = (128, 0, 0)  # Transpose back needed

    im_new = Image.fromarray(data)

    buffered = BytesIO()
    im_new.save(buffered, format="PNG")
    im_new_bytes = buffered.getvalue()

    #img_base64_new = '#'
    return im_new_bytes


def img_content_change_mask_color_from_black(img_content):
    im = Image.open(BytesIO(img_content))
    im = im.convert('RGBA')

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    white_areas = (red > 0) & (blue > 0) & (green > 0)
    black_areas = (red == 0) & (blue == 0) & (green == 0)
    #data[..., :-1][black_areas.T] = (255, 255, 255)  # Transpose back needed
    #data[...][black_areas.T] = (128, 0, 0, 0)  # Transpose back needed
    data[..., :-1][black_areas.T] = (128, 0, 0)  # Transpose back needed
    #data[..., :-1][white_areas.T] = (128, 0, 0)  # Transpose back needed

    im_new = Image.fromarray(data)

    buffered = BytesIO()
    im_new.save(buffered, format="PNG")
    im_new_bytes = buffered.getvalue()

    #img_base64_new = '#'
    return im_new_bytes

def score_against_ref_by_img_content(image_info_file, base_annot_file, img_content):
    score_jaccard = 0
    score_dice = 0
    img_mask_1 = None

    # reference annotation
    annot_src = ''
    try:
        with open(base_annot_file) as f:
            annot_obj = json.load(f)
            annot_src = annot_obj[annot_obj['method']]
    except FileNotFoundError:
        pass

    if annot_src != '':
        with open(image_info_file) as f:
            image_info = json.load(f)
            img_file = image_info['image']

        #img_content = img_content_change_mask_color_from_black(img_content)
        if annot_obj['method'] == 'imagemask':
            encoded_elmts_img_reg = annot_src.split(',', 1)
            img_content_ref = base64.decodebytes(encoded_elmts_img_reg[1].encode('ascii'))
            score_jaccard, score_dice, img_mask_1, img_mask_2 = annot_img_content_mask_compare(img_content_ref, img_content, invert=True)
        else:  # method == 'default'
            score_jaccard, score_dice, img_mask_1, img_mask_2 = annot_polygon_compare_img_content_mask(img_file, annot_src, img_content)

    return score_jaccard, score_dice, img_mask_1, img_mask_2


def annot_polygon_compare(img_file, annot, annot_src):
    img = Image.open(img_file)
    mask1, _ = _get_mask_from_polygon_by_img(img, annot)
    mask2, _ = _get_mask_from_polygon_by_img(img, annot_src)
    score_jaccard, score_dice = _score_mask_similarity(mask1, mask2)
    return score_jaccard, score_dice


def annot_img_content_mask_compare(img_mask_file_1, img_mask_file_2, invert=False):
    img_mask_1 = Image.open(BytesIO(img_mask_file_1)).convert('L')
    img_mask_2 = Image.open(BytesIO(img_mask_file_2)).convert('L')
    mask1 = np.array(img_mask_1)
    mask1 = mask1.astype(int)
    mask1 = mask1.reshape(img_mask_1.width * img_mask_1.height)
    mask2 = np.array(img_mask_2)
    if invert:
        mask2 = np.invert(mask2)
    mask2 = mask2.astype(int)
    mask2 = mask2.reshape(img_mask_2.width * img_mask_2.height)
    score_jaccard, score_dice = _score_mask_similarity(mask1, mask2)

    buffered = BytesIO()
    img_mask_1.save(buffered, format="PNG")
    im_bytes = buffered.getvalue()

    img_mask_2_invert = ImageOps.invert(img_mask_2)
    buffered = BytesIO()
    img_mask_2_invert.save(buffered, format="PNG")
    im_bytes2 = buffered.getvalue()

    return score_jaccard, score_dice, im_bytes, im_bytes2


def annot_polygon_compare_img_content_mask(img_file, annot, img_mask_file, invert=True):
    img = Image.open(img_file)
    mask1, img_mask_1 = _get_mask_from_polygon_by_img(img, annot)
    img_mask = Image.open(BytesIO(img_mask_file)).convert('L')
    mask2 = np.array(img_mask)
    if invert:
        mask2 = np.invert(mask2)
    mask2 = mask2.astype(int)
    mask2 = mask2.reshape(img_mask.width * img_mask.height)
    score_jaccard, score_dice = _score_mask_similarity(mask1, mask2)

    buffered = BytesIO()
    #img_mask_1 = img_content_change_mask_color_from_black(img_mask_1)
    img_mask_1.save(buffered, format="PNG")
    im_bytes = buffered.getvalue()

    buffered = BytesIO()
    img_mask_file_2 = img_content_change_mask_color_from_black(img_mask_file)
    img_mask = Image.open(BytesIO(img_mask_file_2)).convert('RGBA')
    img_mask.save(buffered, format="PNG")
    im2_bytes = buffered.getvalue()

    return score_jaccard, score_dice, im_bytes, im2_bytes


def get_polygons_from_img_mask(image_file, type='name'):
    if type == 'name':
        pim = Image.open(image_file)
    else:  # type == 'content'
        pim = Image.open(BytesIO(image_file)).convert('1')

    mask = np.array(pim)

    segmentations = _get_polygons_from_mask(mask)
    #print(segmentations)
    #segmentations = [x for idx, x in enumerate(segmentations) if len(x) > 0 and idx == 0]
    segmentations = [x for idx, x in enumerate(segmentations) if len(x) > 0]

    if type == 'name':
        buffered = BytesIO()
        pim.save(buffered, format="PNG")
        im_bytes = buffered.getvalue()
        base64image = "data:image/png;base64," + base64.b64encode(im_bytes).decode('ascii')

        return segmentations, base64image
    else:
        return segmentations


# ## PRIVATE

def _get_polygons_from_mask(mask):
    contours = measure.find_contours(mask, 0.5, positive_orientation='low')

    segmentations = []
    polygons = []
    for contour in contours:
        # Flip from (row, col) representation to (x, y)
        # and subtract the padding pixel
        for i in range(len(contour)):
            row, col = contour[i]
            contour[i] = (col - 1, row - 1)

        # Make a polygon and simplify it
        poly = Polygon(contour)
        poly = poly.simplify(1.0, preserve_topology=False)
        polygons.append(poly)
        segmentation = np.array(poly.exterior.coords).ravel().tolist()
        segmentations.append(segmentation)

    return segmentations


# def get_mask_from_polygon_by_img_file(img, annot):
# def get_mask_from_polygon_by_img_content(img, annot):
def _get_mask_from_polygon_by_img(img, annot):
    size = img.size
    img_mask = Image.new('L', size, 'black')
    draw = ImageDraw.Draw(img_mask)
    for polygon in annot:
        draw.polygon(polygon, fill='white')

    mask2d = np.array(img_mask)
    mask = mask2d.reshape(img_mask.width * img_mask.height)

    return mask, img_mask


def _score_mask_similarity(mask1, mask2):
    mask_and = np.logical_and(mask1, mask2)
    #print(np.count_nonzero(mask_and))
    mask_or = np.logical_or(mask1, mask2)
    #print(np.count_nonzero(mask_or))
    n_intersect = np.count_nonzero(mask_and)
    n_union = np.count_nonzero(mask_or)
    jaccard = n_intersect / n_union
    #iou2 = np.count_nonzero(mask1) / n_union
    dice = (2 * n_intersect) / (np.count_nonzero(mask1) + np.count_nonzero(mask2))
    return jaccard, dice


# def compare_annot(img_file, annot, annot_src):
#     img = Image.open(img_file)
#     #print(img.size)
#     mask1, _ = lib_mask.get_mask_from_polygon_by_img(img, annot)
#     #print(mask1)
#     mask2, _ = lib_mask.get_mask_from_polygon_by_img(img, annot_src)
#     #score, _, score3 = iou_mask(mask1, mask2)
#     score_jaccard, score_dice = lib_mask.score_mask_similarity(mask1, mask2)
#     #score = 0.3
#     return score_jaccard, score_dice


# def compare_annot2(img_file, annot, img_mask_file):
#     img = Image.open(img_file)
#     #print(img.size)
#     mask1, img_mask_1 = lib_mask.get_mask_from_polygon_by_img(img, annot)
#     #print(mask1)
#     #mask2 = get_img_mask(img, annot_src)
#     #img2 = Image.open(img_mask_file)
#     #print(img_mask_file)
#     #img_mask = Image.open(img_mask_file).convert("RGBA")
#     img_mask = Image.open(BytesIO(img_mask_file)).convert('L')
#     #print(img_mask)
#     #img_mask = Image.open(BytesIO(img_mask_file)).convert("RGBA")
#     #img_mask = Image.open(img_mask_file)
#     mask2 = np.array(img_mask)
#     #print(np.count_nonzero(mask2 == True))
#     #print(np.count_nonzero(mask2 == False))
#     #print(mask1.size)
#     #print(mask2.size)
#     mask2 = np.invert(mask2)
#     #print(mask1.size)
#     #print(mask2.size)
#     mask2 = mask2.astype(int)
#     #print(np.count_nonzero(mask2))
#     #mask2 = mask2.ravel()
#     mask2 = mask2.reshape(img_mask.width * img_mask.height)
#     #print(mask1.size)
#     #print(mask2.size)
#     #print(mask1)
#     #print(mask2)
#     #print(np.count_nonzero(mask1))
#     #print(np.count_nonzero(mask2))
#     score, score2, score3 = lib_mask.score_mask_similarity(mask1, mask2)
#
#     #img_mask_1 = Image.fromarray(mask2d)
#     buffered = BytesIO()
#     img_mask_1.save(buffered, format="PNG")
#     im_bytes = buffered.getvalue()
#     #img_mask_file_1 = base64.b64encode(buffered.getvalue())
#
#     #score = 0.3
#     return score, im_bytes, score2, score3


# def get_img_mask(img, annot):
#     size = img.size
#     img2 = Image.new('L', size, 'black')
#     draw = ImageDraw.Draw(img2)
#     for polygon in annot:
#         draw.polygon(polygon, fill='white')
#
#     mask2d = np.array(img2)
#     mask = mask2d.reshape(img2.width * img2.height)
#
#     return mask, img2


# def iou_mask(mask1, mask2):
#     mask_and = np.logical_and(mask1, mask2)
#     #print(np.count_nonzero(mask_and))
#     mask_or = np.logical_or(mask1, mask2)
#     #print(np.count_nonzero(mask_or))
#     n_intersect = np.count_nonzero(mask_and)
#     n_union = np.count_nonzero(mask_or)
#     iou = n_intersect / n_union
#     iou2 = np.count_nonzero(mask1) / n_union
#     iou3 = (2 * n_intersect) / (np.count_nonzero(mask1) + np.count_nonzero(mask2))
#     return iou, iou2, iou3


# def get_segmentations_from_file(image_file, type='name'):
#     if type == 'name':
#         pim = Image.open(image_file)
#     else:  # type == 'content'
#         pim = Image.open(BytesIO(image_file)).convert('1')
#     #width, height = im.size
#     #print(width, height)
#
#     mask = np.array(pim)
#     #print(mask.shape)
#     #print(npim)
#
#     segmentations = lib_mask._get_polygons_from_mask(mask)
#     #print(segmentations)
#     segmentations = [x for idx,x in enumerate(segmentations) if len(x) > 0 and idx == 0]
#
#     if type == 'name':
#         buffered = BytesIO()
#         pim.save(buffered, format="PNG")
#         im_bytes = buffered.getvalue()
#         base64image = "data:image/png;base64," + base64.b64encode(im_bytes).decode('ascii')
#
#         return segmentations, base64image
#     else:
#         return segmentations
