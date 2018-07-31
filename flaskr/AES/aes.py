"""
Author: Chris Dare
Version: 1.0
"""

from __future__ import print_function
import numpy as np


########################################################
#                  SUBSTITUTION BOXES                  #
########################################################

# Precomputed substitution layer
_SBox = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

# precomputed inverse substitution layer
_InvSBox = [
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
]


########################################################
#              GALOIS FIELD COMPUTATION                #
########################################################

def xtime(x):
    """ The equivalent of multiplying an element in the galois field
        GF(2^8) by x """
    return (x << 1) ^ (((x >> 7) & 0x01) * 0x1b)


def gmult(x, y):
    """ Uses function composition to represent each digit of a polynomaial
        in GF(2^8). Notice that function composition effectively gives us
        at least 4 bits of accurate data here"""
    
    # multiply each bit of y against x represented
    # as polynomial
    result = (y & 0x01) * x
    result ^= (y>>1 & 1) * xtime(x)
    result ^= (y>>2 & 1) * xtime(xtime(x))
    result ^= (y>>3 & 1) * xtime(xtime(xtime(x)))
    result ^= (y>>4 & 1) * xtime(xtime(xtime(xtime(x))))
    return result & 0xff   # return only the first byte of the calculation


########################################################
#                     EXCEPTIONS                       #
########################################################

class AESError(Exception):
    """ Custom exception for this module """
    pass

########################################################
#                      CLASSES                         #
########################################################


class AESEncryptor:
    """ Class which applies AES block cipher to short strings
        (specifically 16 characters or less). Does not handle
        breaking of strings into chunks, the user must handle
        that his or herself.
        
        The default key is the 256 test vector used in the FIPS
        documentation. Therefore, AES-256 is selected by default
        as well. The user has the option to enable verbose mode
        so that the state is printed before and after decryption
        """
    def __init__(self, klen="256", key=[0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f], verbose=False):
        """ Constructor for AESEncryptor. Sets the default parameters
            for AES-256, but handles cases where other versions are
            selected for key length.
            
            The key schedule is part of instantiation, so that Round
            Keys are availible right off the bat
            """
        # Set options for version of AES key length (
        # i.e. number of rounds, words in key )
        if klen == "128":
            self.__Nr = 10
            self.__Nk = 4
        elif klen == "192":
            self.__Nr = 12
            self.__Nk = 6
        else:
            # Default is AES-256
            self.__Nr = 14
            self.__Nk = 8

        # TEST DATA PROVIDED FROM FIPS DOCUMENTATION
        self._Key = key
        self._state=[[0x00, 0x11, 0x22, 0x33], [0x44, 0x55, 0x66, 0x77], [0x88, 0x99, 0xaa, 0xbb], [0xcc, 0xdd, 0xee, 0xff]]
        self._RoundKey = [0 for i in range(16 * (self.__Nr + 1) )]
        # create round keys upon instantiation
        self._KeySchedule()
        # by default, verbose is off
        self.verbose = verbose


    def encrypt(self, my_str):
        """ One of the two primary methods for AESEncryptor.
            Provided a string of length 16 or less, this method
            encrypts the data and returns the resulting string.
            """
        
        # convert string to instance data in the form
        # of a byte matrix
        self._convertStringToState(my_str)
        # potentially print state
        if self.verbose:
            print("Plaintext:")
            self._printState()
        # encrypt state
        self._AESCipher()
        # potentially print state
        if self.verbose:
            print("Ciphertext:")
            self._printState()
        # retrieve all encrypted data from the
        # state
        return self._convertStateToString()
    
    def decrypt(self, my_str):
        """ The second of our two primary methods for AESEncryptor.
            Provided a string of length 16 or less, this method converts
            encrypted data back into unencrypted data.
            """
        # convert string to instance data in the form
        # of a byte matrix
        self._convertStringToState(my_str)
        # potentially print state
        if self.verbose:
            print("Ciphertext:")
            self._printState()
        # decrypt state
        self._AESInvCipher()
        # potentially print state
        if self.verbose:
            print("Plaintext:")
            self._printState()
        # retrieve all encrypted data from the
        # state
        return self._convertStateToString()


    ########################################################
    #                    KEY SCHEDULE                      #
    ########################################################

    def _RotWord(self, word):
        """ Inline function which takes a word (4 bytes) and performs a cyclical
        right shift"""
        return [word[(i + 1) % 4] for i in range(4)]
    
    def _SubWord(self, word):
        """ Takes each individual byte from a word and sends it through the
        substitution layer"""
        return [_SBox[word[i]] for i in range(4)] #SBox is provided in next section
    
    def _KeySchedule(self):
        """ Rijndael key schedule for generating all round keys
        based off the original key"""
     
        # Since round constants are only used for the key schedule, we
        # keep them local to the method
        Rcon = [0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a]
     
        # The first round key is the key itself
        for i in range(4 * self.__Nk):
            self._RoundKey[i] = self._Key[i]
     
        for i in range(self.__Nk, 4 * (self.__Nr + 1)):
            tempWord = [self._RoundKey[4 * (i - 1) + j] for j in range(4)]

            # since the state is 4x the size of a RoundKey, we only apply our
            # subroutines on necessary rounds
            if (i % self.__Nk == 0) :
               tempWord = self._RotWord(tempWord)
            if (i % 4 == 0):
               tempWord = self._SubWord(tempWord)
            if (i % self.__Nk == 0):
               tempWord[0] ^= Rcon[i // self.__Nk]
     
            # set current round key
            for j in range(4):
                self._RoundKey[4*i + j] = self._RoundKey[4*(i - self.__Nk) + j] ^ tempWord[j]



    ########################################################
    #                      ENCRYPTION                      #
    ########################################################

    def _SubBytes(self):
        """ Force all data in the state matrix through the substitution layer """
        self._state = [[_SBox[self._state[row][col]] for col in range(4)] for row in range(4)]


    def _ShiftRows(self):
        """ Perform a cyclic shift on each row dependent on the depth of the row"""
        for i in range(1, 4):
            self._state[0][i], self._state[1][i], self._state[2][i], self._state[3][i] = \
            self._state[i][i], self._state[(i + 1) % 4][i], self._state[(i + 2) % 4][i], self._state[i - 1][i]


    def _MixColumns(self):
        """ Affine transform in the Rijndael field on the state """
        for col in range(4):
            # temporary variables
            a = self._state[col][0]
            b = self._state[col][1]
            c = self._state[col][2]
            d = self._state[col][3]
     
            self._state[col][0] = gmult(a, 2) ^ gmult(b, 3) ^ c ^ d
            self._state[col][1] = a ^ gmult(b, 2) ^ gmult(c, 3) ^ d
            self._state[col][2] = a ^ b ^ gmult(c, 2) ^ gmult(d, 3)
            self._state[col][3] = gmult(a, 3) ^ b ^ c ^ gmult(d, 2)
     
    def _AddRoundKey(self, round):
        """Adds the round key generated for that specific round to the state"""
        self._state = [[self._state[row][col] ^ self._RoundKey[16 * round + 4 * row + col] for col in range(4)] for row in range(4)]

    def _AESCipher(self):
        """ The complete AES forward encryption performed through byte-array calculations """
        
        # key-whitening
        self._AddRoundKey(0)
        
        for round in range(1, self.__Nr):
            self._SubBytes()
            self._ShiftRows()
            self._MixColumns()
            self._AddRoundKey(round)
        
        # final round
        self._SubBytes()
        self._ShiftRows()
        self._AddRoundKey(self.__Nr)


    ########################################################
    #                     DECRYPTION                       #
    ########################################################

    def _InvSubBytes(self):
        """ Force all data in the state matrix through the inverse substitution layer """
        self._state = [[_InvSBox[self._state[row][col]] for col in range(4)] for row in range(4)]

    def _InvShiftRows(self):
        """ Perform the reverse cyclic shift on each row dependent on the depth of the row"""
        for i in range(1, 4):
            self._state[0][i], self._state[1][i], self._state[2][i], self._state[3][i] = \
            self._state[(4-i)%4][i], self._state[(5- i) % 4][i], self._state[(6-i) % 4][i], self._state[(7-i)%4][i]

    def _InvMixColumns(self):
        """ Inverse affine transform in the Rijndael field on the state """
        for col in range(4):
            # temporary variables
            a = self._state[col][0]
            b = self._state[col][1]
            c = self._state[col][2]
            d = self._state[col][3]
            
            self._state[col][0] = gmult(a, 0x0e) ^ gmult(b, 0x0b) ^ gmult(c, 0x0d) ^ gmult(d, 0x09)
            self._state[col][1] = gmult(a, 0x09) ^ gmult(b, 0x0e) ^ gmult(c, 0x0b) ^ gmult(d, 0x0d)
            self._state[col][2] = gmult(a, 0x0d) ^ gmult(b, 0x09) ^ gmult(c, 0x0e) ^ gmult(d, 0x0b)
            self._state[col][3] = gmult(a, 0x0b) ^ gmult(b, 0x0d) ^ gmult(c, 0x09) ^ gmult(d, 0x0e)

    def _AESInvCipher(self):
        """ The complete AES decryption performed through byte-array calculations """

        # final round
        self._AddRoundKey(self.__Nr)
        self._InvShiftRows()
        self._InvSubBytes()

        for round in range(self.__Nr - 1, 0, -1):
            self._AddRoundKey(round)
            self._InvMixColumns()
            self._InvShiftRows()
            self._InvSubBytes()


        # Reverse Key-whitening
        self._AddRoundKey(0)


    ########################################################
    #                   DATA-FORMATTING                    #
    ########################################################

    def _printState(self):
        """ Prints the state in the same manner specified on
            the AES FIPS documentation. Data is treated in a
            column-row format instead of row-column for
            visualization purposes """

        for row in range(4):
            for col in range(4):
                print(format(self._state[col][row], '02x'), end=' ')
            print()


    def _convertStringToArray(self, my_str):
        """ Helper method which takes a string of length
            16 or less and converts it to an array of
            bytes """
        
        ########################
        #   NEEDS IMPROVEMENT  #
        ########################
        #
        # Instead of breaking up data into separate
        # blocks, I simply require all data fit into one
        if len(my_str) > 16:
            raise AESError("Cannot encrypt block larger than 16 bytes")
        
        my_bytes = [ord(elem) for elem in my_str]
        to_ret = [0x00] * 16

        for i in range(len(my_bytes)):
            to_ret[i] = my_bytes[i]
        return to_ret


    def _convertArrayToString(self, my_arr):
        """ Takes an array of hex data and converts
            each byte back into a string """

        # Additional padding will affect == operation
        my_arr = np.trim_zeros(my_arr)
        return "".join(map(chr, my_arr))

    def _convertArrayToState(self, array):
        """ Takes a byte array and converts it into our
            4x4 matrix of bytes """
        for col in range(4):
            for row in range(4):
                self._state[row][col] = array[4 * row + col]

    def _convertStateToArray(self):
        """" converts our 4x4 matrix of bytes back into
            a linear vector of bytes """
        my_arr = [0x00] * 16

        for col in range(4):
            for row in range(4):
                my_arr[4 * row + col] = self._state[row][col]

        return my_arr

    def _convertStringToState(self, my_str):
        """ Helper method which applies our two smaller methods
            convertStringToArray and convertArrayToState """
        my_arr = self._convertStringToArray(my_str)
        self._convertArrayToState(my_arr)

    def _convertStateToString(self):
        """ Helper method which applies our two smaller methods
            convertStateToArray and convertArrayToString """
        my_arr = self._convertStateToArray()
        return self._convertArrayToString(my_arr)


########################################################
#                      TESTING                         #
########################################################

# Testing purposes only
if __name__ == "__main__":

    justEncrypted = False
    AES = AESEncryptor(verbose = True)
    plaintext = None
    ciphertext = None
    
    while True:
        
        option = None
        if justEncrypted:
            option = raw_input("Decrypt [D], Encrypt another [E], or Quit [Q]: ")
        else:
            option = raw_input("Encrypt [E] or Quit [Q]: ")

        if option == "E" or option == "e":
            justEncrypted = True
            # input plaintext from user
            plaintext = raw_input("Enter plaintext: ")
            ciphertext = AES.encrypt(plaintext)
            print (ciphertext)
        elif (option == "D" or option == "d") and justEncrypted:
            justEncrypted = False
            print(AES.decrypt(ciphertext))
        elif option == "Q" or option == "q":
            print("Exiting...")
            break
        else:
            continue

