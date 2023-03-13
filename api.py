from flask import Flask, request
import cv2
import pandas as pd
import numpy as np
from rembg import remove
from PIL import Image
import sys
import base64
import socket
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

app = Flask(__name__)

socket.setdefaulttimeout(300)


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

    arch_height = process_side_profile()
    toe_width = process_top_profile()
    arch_pred = predict_arch(arch_height)
    toe_pred = predict_toe(toe_width)

    print(arch_pred)
    print(toe_pred)
    return {
        "arch_height" : arch_height,
        "toe_width" : toe_width,
        "arch_type" : arch_pred, 
        "toe_type" : toe_pred
    }

def predict_toe(toe_width):
    data = pd.read_csv(r"C:\Users\Sathvik\Desktop\Project\ML Model\CSV Toe Width.csv", header=None)
    data = pd.DataFrame(data)
    x = np.array(data.iloc[:, 0])
    y = np.array(data.iloc[:, 1])
    knn = KNeighborsClassifier(n_neighbors=10)
    x = x.reshape(-1, 1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
    knn.fit(x_train, y_train)
    res = knn.predict([[toe_width]])[0]
    if res==0:
        return 'Normal Toe Box'
    else:
        return 'Wide Toe Box'

def predict_arch(arch_height):
    if arch_height == -1:
        return 'Please recapture image'
    data = pd.read_csv(r"C:\Users\Sathvik\Desktop\Project\ML Model\CSV Arch Height.csv", header=None)
    data = pd.DataFrame(data)
    x = np.array(data.iloc[:, 0])
    y = np.array(data.iloc[:, 1])
    knn = KNeighborsClassifier(n_neighbors=10)
    x = x.reshape(-1, 1)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
    knn.fit(x_train, y_train)
    res = knn.predict([[arch_height]])[0]
    if res==0:
        return 'Flat Arch'
    elif res==1:
        return 'Normal Arch'
    else:
        return 'High Arch'


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
        arr = thresh[i]
        l, r = 0, len(arr)-1
        if(len(set(arr))==1): continue
        while(arr[l]==0 and l<r): 
            l+=1
        while(arr[r]==0 and l<r): 
            r-=1
        lf = l
        while(arr[l] == 255 and l<r): 
            l+=1
        if(l>=r):
            if(flag==0):
                flag = 1
                continue
            elif(flag==1): 
                continue
            else: break
        rf = r
        while(arr[r]==255 and l<r): r-=1
        if len(set(arr[l:r+1]))>1:
                continue
        if ((rf-lf+1)>=len(arr)*0.8):
            minI = i
            min = rf-lf+1
        if(flag==1): flag+=1
        x = r-l+1
        if(x<((len(arr)/100)*0.5)): continue
        if(x<min): 
            min = x
            minI = i

    if(min == sys.maxsize):
        return -1
    for j in range(minI+1, len(thresh)):
        arr = thresh[j]
        if(len(set(arr))==2):
            maxI = j

    arch_h = (maxI-minI)/len(thresh[0])
    return arch_h


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

    max = dimensionUtil(thresh)
    totalW = len(thresh[0])
    toeWidth = max/totalW
    return toeWidth


def dimensionUtil(contours):
  cmax=0
  for x in contours:
        if(len(set(x))==1): continue
        l, r =0, len(x)-1
        while(x[l]==0): l+=1
        while(x[r]==0): r-=1
        if(l>r): continue
        y = r-l+1
        if(cmax<y): cmax= y
  return cmax


if __name__ == "__main__":
    app.run(host='0.0.0.0')
