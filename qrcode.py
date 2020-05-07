# Standard python library imports
import argparse
import base64
import math
import random
import string
import time
from io import BytesIO

# Own code import
import badwords

# External library imports
import pymongo
import pyqrcode
from PIL import Image, ImageDraw, ImageFont

'''
	Generates a random string with a given length.
		Uses lowercase, uppercase, and digit characters
		For every position but the last position it also uses '-' and '_'
'''
def randomString(stringLength = 11):
	characters = string.ascii_letters + string.digits
	return ''.join([random.choice(characters + "_-") for i in range(stringLength - 1)] + [random.choice(characters)])

'''
	Generate a random string of given length that doesn't contain a badword.
'''
def generateCode(stringLength = 11, collection = None):
	while True:
		code = randomString(stringLength)

		if not badwords.check(code):
			if collection != None:
				if checkCodeAvailable(code, collection):
					return code
			else:
				return code

'''
	Round the corners of the given image with a given radius.
'''
def roundCorners(im, rad):
	# Ensure the image is the right format
	im = im.convert('RGBA')

	# Generate a circle image
	circle = Image.new('L', (rad * 2, rad * 2), 0)
	draw = ImageDraw.Draw(circle)
	draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)

	# Generate solid alpha of the input image size
	alpha = Image.new('L', im.size, 255)
	w, h = im.size

	# Past the 4 corners of the circle onto the alpha image
	alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
	alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
	alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
	alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))

	# Apply the alpha as a mask onto the input image and return
	im.putalpha(alpha)
	return im

'''
	Generate a QRCode pillow image with the given link.
'''
def generateQRCode(link, resizedWidth):
	# Generate the qrcode from the link using pyqrcode
	code = pyqrcode.create(link)

	# Calculate the optimal qr scale to generate at to ensure you are only ever downsizing
	scale = int(math.ceil(resizedWidth / code.get_png_size(quiet_zone=1)))

	# Get the qr code's png data
	pngData = code.png_as_base64_str(scale = scale, quiet_zone=1)

	# Convert the png to a pillow image and return
	codePILImg = Image.open(BytesIO(base64.b64decode(pngData)))
	return (codePILImg, scale)

'''
	Generates a full sticker with a given link and base image.
'''
def generateSticker(link, baseImg, font, stickerQRScale=0.55, QROffset = (0, 0.04), QRRounding=False, textOffset = (0, 0.02), textColor = (0,0,0,255)):
	
	# Generate the qr code for the sticker
	baseW, baseH = baseImg.size
	qrSize = int(stickerQRScale * min(baseW, baseH))
	QRCode, QRScale = generateQRCode(link, qrSize)

	# Add QRCode corner rounding
	if QRRounding:
		QRCode = roundCorners(QRCode, QRScale)

	# Resize the qr code to be put on the sicker
	QRCode = QRCode.resize((qrSize, qrSize))

	# Calculate the real offset
	QROffset = (int(QROffset[0] * baseW), int(QROffset[1] * baseH))

	# Center QRCode and add real offset
	QROffset = (QROffset[0] + int(baseW/2 - qrSize/2), QROffset[1] + int(baseH/2 - qrSize/2))

	# Form the QR paste box for pasting onto the baseImg
	QRPasteBox = (QROffset[0], QROffset[1], QROffset[0] + qrSize, QROffset[1] + qrSize)

	# Add the QR code to the baseImg
	baseImg.paste(QRCode, QRPasteBox, QRCode)

	# Draw the link centered under the QRCode with the textOffset applied
	textWidth = font.getsize(link)[0]
	ImageDraw.Draw(baseImg).text((QROffset[0] + int(qrSize/2) - int(textWidth/2) + int(baseW * textOffset[0]), QROffset[1] + qrSize + int(baseH * textOffset[1])), link, font = font, fill = textColor)

	return baseImg

def OpenStickerCollection(clientConnectionInfo, stickerDBName, stickerColName):
	mClient = pymongo.MongoClient(clientConnectionInfo)

	if not (stickerDBName in mClient.list_database_names()):
		return

	stickerDB = mClient[stickerDBName]

	if not (stickerColName in stickerDB.list_collection_names()):
		return

	return stickerDB[stickerColName]

def checkCodeAvailable(code, collection):
	codeConflict = collection.find_one({'code': code})

	return (codeConflict == None)


def storeCodeInDatabase(code, collection):
	if collection == None:
		return False

	# Check if code already exists
	codeConflict = collection.find_one({'code': code})

	if codeConflict != None:
		return False

	stickerInfo = {'code': code, 'book_id': 0}
	collection.insert_one(stickerInfo)
	return True

def getArguments():
	parser = argparse.ArgumentParser(description="Generate pngs for stickers with QR codes and links.")
	# Number of stickers to generate
	parser.add_argument("integers", metavar='N', type=int, help="How many stickers to generate.")
	# The base sticker image
	parser.add_argument('-s', '--stickerbase', nargs='?', default='StickerBases/bw/whitebase7.png', help='The file to use as the sticker base.')
	# The base sticker link
	parser.add_argument('-l', '--linkbase', nargs='?', default='sermire.com/', help='The start of the link to put the code onto.')
	# The length of a generated code
	parser.add_argument('-L', '--codelength', type=int, nargs='?', default=11, help='The length of the code to generate.')
	# The size of the link font
	parser.add_argument('-f', '--fontsize', type=int, nargs='?', default=50, help='The size of the font for the link.')
	# The font to use for the sticker link
	parser.add_argument('-F', '--font', nargs='?', default='Fonts/cour.ttf', help='The .ttf file to use as the link font.')
	# The path of the output
	parser.add_argument('-S', '--stickerdirectory', nargs='?', default='Stickers/', help='The directory to output the sticker pngs to.')
	# Whether to round the QR code corners or not
	parser.add_argument('-r', '--roundqr', type= bool, nargs='?', default=True, help='Whether to round the QR code\'s corners or not.')
	# The scale of the QR code on the sticker
	parser.add_argument('-q', '--qrscale', type=float, nargs='?', default=0.55, help='The scale of the QR code on the sticker.')
	# The QR code offset
	parser.add_argument('--qroffset', type=float, nargs='*', default=[0,0.04], help='The offset of the QR code on the horizontal and vertical axises.')
	# The link offset
	parser.add_argument('--textoffset', type=float, nargs='*', default=[0, 0.02], help='The offset of the link on the horizontal and vertical axises.')
	# The text color
	parser.add_argument('--textcolor', nargs='*', type=int, default=[0,0,0,255], help='The RGBA color of the link text.')

	# Whether to print the intermediate information
	parser.add_argument('-p', '--printinterinfo', type=bool, nargs='?', default=True, help='Whether to print the information for each sticker when generated.')

	args = parser.parse_args()

	if len(args.qroffset) < 2:
		print("Invalid qr offset, can't form sticker.")
		return None
	if len(args.textoffset) < 2:
		print("Invalid text offset, can't form sticker.")
		return None
	if len(args.textcolor) < 4:
		print("Invalid text color, can't form sticker.")
		return None

	return args

if __name__ == "__main__":

	args = getArguments()

	if args != None:
		# Sticker construction information
		N = args.integers
		baseImg = Image.open(args.stickerbase)
		baseLink = args.linkbase
		codeLength = args.codelength
		codeFontSize = args.fontsize
		codeFont = ImageFont.truetype(args.font, codeFontSize)
		stickerPath = args.stickerdirectory
		qrrounding = args.roundqr
		qrscale = args.qrscale
		qroffset = (args.qroffset[0], args.qroffset[1])
		textoffset = (args.textoffset[0], args.textoffset[1])
		textcolor = (args.textcolor[0], args.textcolor[1], args.textcolor[2], args.textcolor[3])

		# Console output information
		pi = args.printinterinfo

		# Connect to mongoDB collection for storing generating sticker codes
		collection = OpenStickerCollection("mongodb://localhost:27017", "Books", "Stickers")
		if collection == None:
			print("Could not open sticker collection")
		else:
			timeStart = time.perf_counter()
			i = 0
			realI = 0
			while (i < N) and (realI < 2*N):
				code = generateCode(codeLength)
				fullLink = baseLink + code

				temp = baseImg.copy()
				
				sticker = generateSticker(fullLink, temp, codeFont, stickerQRScale=qrscale, QROffset = qroffset, QRRounding=qrrounding, textOffset=textoffset, textColor = textcolor)

				if storeCodeInDatabase(code, collection):
					sticker.save(stickerPath + code + '.png')
					if pi:
						print("Generated sticker: ", fullLink, flush=True)
				else:
					if pi:
						print("Failed to generate sticker")
						i-=1

				i+=1
				realI+=1
			timeEnd = time.perf_counter()

			print("Generating stickers took: ", timeEnd - timeStart)
			print("\t", (timeEnd - timeStart)/i, "s per sticker", sep='')