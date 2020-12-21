from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy

# Input from command line
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="Input image path")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="Choose preprocessing type from blur, linear, adaptive, cubic, bilateral & thresh")
args = vars(ap.parse_args())

print(args)

# Load the example image and convert it to grayscale
input_image = cv2.imread("test1.jpg")
gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

# Preprocessing image according to type
if args["preprocess"] == "thresh":
    gray_image = cv2.threshold(gray_image, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

elif args["preprocess"] == "adaptive":
    gray_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

if args["preprocess"] == "linear":
    gray_image = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

elif args["preprocess"] == "cubic":
    gray = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# If image is blurred
if args["preprocess"] == "blur":
    gray_image = cv2.medianBlur(gray_image, 3)

elif args["preprocess"] == "bilateral":
    gray_image = cv2.bilateralFilter(gray_image, 9, 75, 75)

# Save processed grayscale image for temporary purpose
filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray_image)

# Load the image, apply OCR, and then delete temp file
text = pytesseract.image_to_string(Image.open(filename), lang = 'eng')
os.remove(filename)

# print(text)

# Write extracted text to output file
text_output = open('output.txt', 'w', encoding='utf-8')
text_output.write(text)
text_output.close()

file = open('output.txt', 'r', encoding='utf-8')
text = file.read()

# ftfy: fixes text for you (mostly fixes unicode that's broken)
text = ftfy.fix_text(text)
text = ftfy.fix_encoding(text)
# print(text)


# Extracting information from text
name = None
fname = None
dob = None
pan = None
nameline = []
dobline = []
panline = []
text0 = []
text1 = []
text2 = []

# Searching for PAN
lines = text.split('\n')
for lin in lines:
    s = lin.strip()
    s = lin.replace('\n','')
    s = s.rstrip()
    s = s.lstrip()
    text1.append(s)

text1 = list(filter(None, text1))

# Regex to remove unnecessary words

lineno = 0  # to start from the first line of the text file.

for wordline in text1:
    xx = wordline.split('\n')
    if ([w for w in xx if re.search('(INCOMETAXDEPARWENT @|mcommx|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$', w)]):
        text1 = list(text1)
        lineno = text1.index(wordline)
        break

text0 = text1[lineno+1:]
print(text0) 

def findword(textlist, wordstring):
    lineno = -1
    for wordline in textlist:
        xx = wordline.split( )
        if ([w for w in xx if re.search(wordstring, w)]):
            lineno = textlist.index(wordline)
            textlist = textlist[lineno+1:]
            return textlist
    return textlist

try:

    # name
    name = text0[0]
    name = name.rstrip()
    name = name.lstrip()
    name = name.replace("8", "B")
    name = name.replace("0", "D")
    name = name.replace("6", "G")
    name = name.replace("1", "I")
    name = re.sub('[^a-zA-Z] +', ' ', name)

    # father's name
    fname = text0[1]
    fname = fname.rstrip()
    fname = fname.lstrip()
    fname = fname.replace("8", "S")
    fname = fname.replace("0", "O")
    fname = fname.replace("6", "G")
    fname = fname.replace("1", "I")
    fname = fname.replace("\"", "A")
    fname = re.sub('[^a-zA-Z] +', ' ', fname)

    # dob
    dob = text0[2]
    dob = dob.rstrip()
    dob = dob.lstrip()
    dob = dob.replace('l', '/')
    dob = dob.replace('L', '/')
    dob = dob.replace('I', '/')
    dob = dob.replace('i', '/')
    dob = dob.replace('|', '/')
    dob = dob.replace('\"', '/1')
    dob = dob.replace(" ", "")

    # pan number
    text0 = findword(text1, '(Pormanam|Number|umber|Account|ccount|count|Permanent|ermanent|manent|wumm)$')
    panline = text0[0]
    pan = panline.rstrip()
    pan = pan.lstrip()
    pan = pan.replace(" ", "")
    pan = pan.replace("\"", "")
    pan = pan.replace(";", "")
    pan = pan.replace("%", "L")

except:
    pass

# storing information in tuple
data = {}
data['Name'] = name
data['Father Name'] = fname
data['Date of Birth'] = dob
data['PAN'] = pan

# print(data)

print("|-------------------------------|")
print('|', '\t', data['Name'])
print("|-------------------------------|")
print('|', '\t', data['Father Name'])
print("|-------------------------------|")
print('|', '\t', data['Date of Birth'])
print("|-------------------------------|")
print('|', '\t', data['PAN'])
print("|-------------------------------|")