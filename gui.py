from Tkinter import *
import numpy as np
import cv2
import hashlib
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ctypes
import tkFont

from fp_functions import hash_file
from fp_functions import gen_RSA_keys
from fp_functions import sign_hash
from fp_functions import read_bits
from fp_functions import apply_watermark
from fp_functions import read_watermark
from fp_functions import watermark_dir


class GraphicalInterface(Frame):
	"""The graphical interface class"""
	
	def __init__(self,master):
		"""Initialize the frame"""
		self.frame = Frame.__init__(self,master)
		self.grid()
		
		#path variables
		self.filename = ""
		self.dir= ""
		self.privateKey= ""		
		self.publicKey= ""
		self.originalFile = ""
		self.watermarkedFile = ""
		
		self.create_widgets()
		
	def create_widgets(self):
		self.fav = StringVar()
		customFont = tkFont.Font(family= "Helvetica", size = 13, weight = "bold")
		headerFont = tkFont.Font(family = "Helvetica", size = 10, weight = "bold", slant = "italic")
		
		"""WATERMARKING FRAME"""
		WatermarkFrameOuter = LabelFrame (self.frame, text = "  WATERMARK IMAGES  ", 
		bd=3, relief = GROOVE, font = customFont)		
		WatermarkFrame = Frame (WatermarkFrameOuter)
		Label(WatermarkFrame, 
		text = "Select processing type",
		font = headerFont).grid(row = 0, column = 0, sticky = W)
		self.fav = StringVar()
		
		#single file radiobutton choice
		Radiobutton(WatermarkFrame, 
		text = "Single image", 
		variable = self.fav, 
		value = 1, 
		indicatoron=0,
		command = self.single_processing).grid(row = 1, column = 0, sticky = W)

		#multiple files radiobutton choice
		Radiobutton(WatermarkFrame, 
		text = "Multiple images", 
		variable = self.fav, 
		value= 2, 
		indicatoron=0, 
		command = self.batch_processing).grid(row = 2, column = 0, sticky = W)

		WatermarkFrame.grid(row = 0, column = 0, rowspan = 3, columnspan = 2, 
		padx=10, pady= 10, sticky = W+E+N+S)
		
		#Watermark button
		Button(WatermarkFrameOuter, 
		text = "WATERMARK", 
		command = self.watermark,
		bd = 4, 
		justify = CENTER, 
		relief = RIDGE).grid(row = 4, column = 2, padx = 10, pady = 10, sticky = W )
		
		WatermarkFrameOuter.grid(row = 0, column = 0, rowspan = 3, columnspan = 2, 
		padx=5, pady=10, sticky = W+E+N+S)
		
		"""VERIFICATION FRAME"""
		self.fav2 = StringVar()
		VerifyFrameOuter = LabelFrame (self.frame, text = "  VERIFY WATERMARKS  ", 
		bd = 3, relief = GROOVE, font = customFont)
		
		VerifyFrameLeft = Frame(VerifyFrameOuter)
		
		Label(VerifyFrameLeft, 
		text = "Select Images ",
		font = headerFont).grid(row = 0, column = 0, sticky = W)
		Label(VerifyFrameLeft, 
		text = "Select Watermarked image : ").grid(row = 1, column = 0, sticky = W)
		Button(VerifyFrameLeft, 
		text = " Browse ",
		command = self.browse_watermarkedImage).grid(row = 1, column = 1, sticky = W)
		
		Label(VerifyFrameLeft, 
		text = "Select Original image : ").grid(row = 2, column = 0, sticky = W)
		Button(VerifyFrameLeft, 
		text = " Browse ", 
		command = self.browse_originalFile).grid(row = 2, column = 1, sticky = W)
		
		VerifyFrameLeft.grid(row = 0, column = 0,  rowspan = 3, columnspan = 2, 
		padx= 10, pady = 10, sticky = W+E+N+S)
		
		VerifyFrameRight = Frame(VerifyFrameOuter)
		
		Label(VerifyFrameRight, 
		text = "Generate Signature", 
		font = headerFont).grid(row = 0, column = 0, sticky = W)
		
		Label(VerifyFrameRight, 
		text = "Select the private key : ").grid(row = 1, column = 0, sticky = W)
		#Browse private key file button
		Button(VerifyFrameRight, 
		text = " Browse ", 
		command = self.browse_privateKey).grid(row = 1, column = 1, sticky = W )
		
		Label(VerifyFrameRight, 
		text = "Select the public key : ").grid(row = 2, column = 0, sticky = W)
		#Browse public key file button
		Button(VerifyFrameRight, 
		text = " Browse ", 
		command = self.browse_publicKey).grid(row = 2, column = 1, sticky = W )
		
		VerifyFrameRight.grid(row = 0, column = 2, rowspan = 3, columnspan = 2, 
		padx= 10, pady = 10, sticky = W+E+N+S)

		#Verify button
		Button(VerifyFrameOuter, 
		text = "VERIFY WATERMARK", 
		command = self.verify_watermark,
		bd = 4, 
		justify = CENTER, 
		relief = RIDGE).grid(row = 5, column = 3, padx = 10, pady = 10, sticky = W )
		
		VerifyFrameOuter.grid(row = 0, column = 2, rowspan = 3, columnspan = 4, 
		padx=5, pady= 10, sticky = W+E+N+S)
		
	def single_processing(self):
		from tkFileDialog import askopenfilename
		Tk().withdraw()
		self.filename = askopenfilename()
	
	def batch_processing(self):
		from tkFileDialog import askdirectory
		Tk().withdraw()
		self.dir = askdirectory()
		
	def browse_privateKey(self):
		from tkFileDialog import askopenfilename
		Tk().withdraw()
		self.privateKey = askopenfilename()
		
	def browse_publicKey(self):
		from tkFileDialog import askopenfilename
		Tk().withdraw()
		self.publicKey = askopenfilename()	

	def browse_originalFile(self):
		from tkFileDialog import askopenfilename
		Tk().withdraw()
		self.originalFile = askopenfilename()	
		
	def browse_watermarkedImage(self):
		from tkFileDialog import askopenfilename
		Tk().withdraw()
		self.watermarkedFile = askopenfilename()
		
	def watermark(self):

		if self.fav.get() == "1":
			"""Single image watermarking-----"""
			image = cv2.imread(self.filename)
			imageHash = hash_file(self.filename)
			key = gen_RSA_keys(1024)

			signature = sign_hash(key, imageHash)
			watermarkedImage = apply_watermark(signature, image)
			cv2.imwrite("WatermarkedImage.png", watermarkedImage)
			
			#to show confirmation popup - Style 0 is for OK popup
			ctypes.windll.user32.MessageBoxA( 0, "Image watermarked successfully!!", "Watermarking completed",0)
			
		elif self.fav.get() == "2":
			"""Multiple image watermarking - Samuel's code here"""
			key = gen_RSA_keys(1024)
			print self.dir
			watermark_dir(key, self.dir+"/")
			#TODO: Verify that watermarking is done
			#If done , uncomment below lines
			ctypes.windll.user32.MessageBoxA( 0, "Image watermarked successfully!!", "Watermarking completed",0)
			
		else:
			ctypes.windll.user32.MessageBoxA( 0, "Please select processing type option above", "Warning",0)
		
	def verify_watermark(self):
		if self.watermarkedFile == "":
			#checking if signature file has been selected 
			ctypes.windll.user32.MessageBoxA( 0, "Please select watermarked file for verification", "Warning",0)	
			
		elif self.privateKey == "":
			#checking if privateKey file has been selected 
			ctypes.windll.user32.MessageBoxA( 0, "Please select the file containing the private key for verification", "Warning",0)
			
		elif self.publicKey == "":
			#checking if privateKey file has been selected 
			ctypes.windll.user32.MessageBoxA( 0, "Please select the file containing the public key for verification", "Warning",0)

		elif self.originalFile == "":
			#checking if original file has been selected 
			ctypes.windll.user32.MessageBoxA( 0, "Please select the original image for verification", "Warning",0)
		
		else:
			"""TO-DO: Verify image - Samuel """
			verify_watermark(self.watermarkedFile, self.originalFile, self.privateKey, self.publicKey)			
			#to show confirmation popup - Style 0 is for OK popup
			ctypes.windll.user32.MessageBoxA( 0, "Watermarked is verified!!", "Verification completed",0)
		

root = Tk()
root.title("Watermarking")
root.geometry("735x210")
app = GraphicalInterface(root)
root.mainloop()

