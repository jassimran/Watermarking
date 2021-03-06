'''
CS 6475
Final Project
Samuel Woo
Jassimran Kaur
'''

import numpy as np
import cv2
import hashlib
import os
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random


def hash_file(FILE_NAME):
    '''
    Description:  This function will hash a file and return the hash object.
    The hash algorithm can be modified by changing the hashlib algorithm.

    References:
    https://docs.python.org/2/library/hashlib.html
    http://www.pythoncentral.io/hashing-files-with-python/

    input args:
    FILE_NAME is the path and name of the file to be hashed in string format.

    output:
    hasher is the HASH object created by the hashlib function
    '''
    blockSize = 2 ** 16
    fileHash = hashlib.sha256()
    with open(FILE_NAME, 'rb') as afile:
        buf = afile.read(blockSize)
        while len(buf) > 0:
            fileHash.update(buf)
            buf = afile.read(blockSize)
    return fileHash



def gen_RSA_keys(mod_size):
    '''
    Description:  This function will generate a public-private key pair using RSA.
    The key object contains the public exponent, modulus, and private exponent.

    References:
    https://www.dlitz.net/software/pycrypto/doc/
    http://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/

    input args:
    mod_size is an integer which specifies the size of the modulus.  The values
    should be 1024, 2048, or 4096.

    output:
    key is an instance of RSAobj from pycrypto library
    '''
    random_generator = Random.new().read
    key = RSA.generate(mod_size, random_generator)
    return key


def sign_hash(rsaKey, fileHash):
    '''
    Description:  This function will sign a hash and return the signature

    References:  
    https://www.dlitz.net/software/pycrypto/doc/
    http://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/

    input args:
    rsaKey is the RSA key object generated by gen_RSA_keys
    fileHash is the hash object generated by hash_file

    output:
    signature is the signed hash object.  The data type is a tuple with one element
    which is the signature number in 'long' format.  The length of the long integer
    will be a number between 0 and the size of the modulus.  Most likely the size of
    the signature will be approximately the size of the modulus (e.g. 1024-bit 
    modulus will result in an appoximately 1024-bit signature).
    '''
    signature = rsaKey.sign(fileHash.digest(), '')
    return signature


def read_bits(signature, shift):
    '''
    Description:  This function will read the bits in a signature one a time.

    References:
    http://docs.scipy.org/doc/numpy/reference/generated/numpy.right_shift.html
    http://docs.scipy.org/doc/numpy/reference/generated/numpy.binary_repr.html

    input args:
    signature is the RSA signature generated by sign_hash function
    shift is an integer argument that specifies how many bits to shift the signature
    by.

    output:
    A tuple with two elements.  Element 0 is an integer which will be a 0 or 1 
    corresponding to the shift size.  Element 1, sigLength, is the length of the 
    signature in bits.
    '''
    #Do a binary right shift of the signature by the shift parameter
    sig = np.right_shift(signature[0], shift)
    #Get the binary string representation of the shifted signature
    bitStr = np.binary_repr(sig)
    sigLength = len(bitStr)
    #Get the last number in bit string converted to an int and return
    return int(bitStr[-1]), sigLength


def apply_watermark(signature, image):
    '''
    Description:  This function applies the signature as a watermark to the image
    by changing the least signficant bit in each pixel to that of the digital
    signature.

    input args:
    signature: the RSA signature generated by the sign_hash function
    image: the image to be watermarked

    output:
    image is returned as the watermarked version
    '''
    shift = 0
    # Nested for loop to iterate through each pixel from top left to right and
    # moving back to the left on the next row after all columns.
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            for k in range(0, 3):
                # Convert pixel value to binary string
                binStr = bin(image[i, j, k])
                # Remove least signficant bit from the string
                binStr = binStr[0:-1]
                # Append signature bit to binStr (i.e. watermark value)
                binStr = binStr + str(read_bits(signature, shift)[0])
                # Change pixel to watermarked value
                image[i, j, k] = int(binStr, 2)
                shift += 1
                if shift == read_bits(signature, 0)[1]:
                    return image

def read_watermark(image, sigLength):
    '''
    Description:  This function will read the watermark from the image.

    input args:
    image is the watermarked image from which to extract the signature
    sigLength is the length of the watermark in bits

    output:
    sigTuple is the watermark in a tuple format so we can easily verify that the 
    signature is authentic.
    '''
    counter = 0
    signature = ''
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            for k in range(0, 3):
                binStr = bin(image[i, j, k])
                signature = binStr[-1] + signature
                counter += 1
                if counter == sigLength:
                    sigInteger = int(signature, 2)
                    # Assign sigInteger to a tuple with only one element
                    sigTuple = (sigInteger,)
                    return sigTuple

def watermark_dir(key, IMAGE_PATH):
    '''
    Description:  This function will watermark an entire directory of images.

    input args:
    key is the key created by the key gen_RSA_keys function
    IMAGE_PATH is the full path of the folder containing the images

    output:
    One output image will be create for each image in the directory.  All of
    the output images will be prefixed with 'wm_' to indicate that they are
    watermarked.
    '''
    # Initialize tuple of valid file extensions
    validExt = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')
    # Create list of images
    imageList = os.listdir(IMAGE_PATH)
    # Iterate through every image in path
    for imageFile in imageList:
        # Split the name from the extension
        imageName, imageExt = os.path.splitext(imageFile)
        if imageExt.lower() in validExt:
            fullPath = IMAGE_PATH + imageFile
            image = cv2.imread(fullPath)
            imageHash = hash_file(fullPath)
            signature = sign_hash(key, imageHash)
            watermarkedImage = apply_watermark(signature, image)
            cv2.imwrite(IMAGE_PATH + 'wm_' + imageName + '.png', watermarkedImage)



'''
Need function read a private and public RSA key and load as a pycrypto key object
in memory.

Rewrite hash function to handle larger files.
'''

def import_key(KEY_PATH):
    '''
    Description:  This function reads an RSA key file in PKCS#1 or PKCS#8 in 
    binary or PEM encoding.  It can also read OpenSSH text keys.

    References:
    https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA-module.html#importKey
    https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA._RSAobj-class.html
    http://joelvroom.blogspot.com/2013/07/encryption-in-python-pycrypto.html
    http://pumka.net/2009/12/19/reading-writing-and-converting-rsa-keys-in-pem-der-publickeyblob-and-privatekeyblob-formats/

    input args:
    KEY_PATH is the full path to the key file

    output:
    RSAObject is a pycrypto RSAobj which includes the following fields: modulus
    and size, public exponent, private exponent, the two generating primes, and
    the CRT coefficient (1/p) mod q.
    '''
    keyFile = open(KEY_PATH, 'rb')
    keyString = keyFile.read()
    keyFile.close()
    RSAObject = RSA.importKey(keyString)
    return RSAObject




















