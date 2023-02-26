from flask import Flask, request
import cv2
import numpy as np
from rembg import remove
from PIL import Image
import sys
import base64


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def image_query():
    input_query = request.get_json()
    b64side = input_query['Image1']
    b64side = bytes(b64side, 'utf-8')

    b64top = input_query['Image2']
    b64top = bytes(b64top, 'utf-8')

    with open("side_prof.png", "wb") as fh:
        fh.write(base64.decodebytes(b64side))

    with open("top_prof.png", "wb") as fh:
        fh.write(base64.decodebytes(b64top))
    print("Arch height = " + str(process_side_profile()) +
          "\nToe Width = " + str(process_top_profile()))
    return "Arch height = " + str(process_side_profile()) + "\nToe Width = " + str(process_top_profile())


def process_side_profile():
    input = Image.open('side_prof.png')
    output = remove(input)
    output.save('op.png')

    foot = cv2.imread("./op.png", 0)
    ret, thresh = cv2.threshold(foot, 10, 255, cv2.THRESH_BINARY)
    cont, heir = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hull = [cv2.convexHull(c) for c in cont]
    fin = cv2.drawContours(foot, hull, -1, (255, 255, 255))

    max = 0
    min = sys.maxsize
    maxI = 0
    minI = 0

    flag = 0
    for i in range(len(thresh)-1, -1, -1):
        # print(i)
        arr = thresh[i]
        l, r = 0, len(arr)-1
        if(len(set(arr)) == 1):
            continue
        while(arr[l] == 0 and l < r):
            l += 1
        while(arr[r] == 0 and l < r):
            r -= 1
        while(arr[l] == 255 and l < r):
            l += 1
        if(l >= r):
            if(flag == 0):
                flag = 1
                continue
            elif(flag == 1):
                continue
            else:
                break
        while(arr[r] == 255 and l < r):
            r -= 1
        if(flag == 1):
            flag += 1
        x = r-l+1
        if(x < min):
            min = x
            minI = i
    print(minI, min)

    for j in range(minI+1, len(thresh)):
        arr = thresh[j]
        l, r = 0, len(arr)-1
        while(arr[l] == 0 and l < r):
            l += 1
        while(arr[r] == 0 and r >= l):
            r -= 1
        if(max <= (r-l+1)):
            max = r-l+1
            maxI = j
    print(maxI, max)

    arch_h = (maxI-minI)/len(thresh)
    return (arch_h)


def process_top_profile():
    input = Image.open('top_prof.png')
    output = remove(input)
    output.save('op.png')

    foot = cv2.imread("./op.png", 0)
    ret, thresh = cv2.threshold(foot, 10, 255, cv2.THRESH_BINARY)
    cont, heir = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hull = [cv2.convexHull(c) for c in cont]
    fin = cv2.drawContours(foot, hull, -1, (255, 255, 255))

    contours = np.vstack(fin).squeeze()
    max = dimensionUtil(contours)
    totalW = contours.shape[1]
    toeWidth = max/totalW
    return toeWidth


def dimensionUtil(contours):
    cmax = 0
    for x in contours:
        count = 0
        for i in x:
            if i != 0:
                count += 1
            else:
                if count > cmax:
                    cmax = count
                count = 0
    return cmax


if __name__ == "__main__":
    app.run(host='0.0.0.0')
