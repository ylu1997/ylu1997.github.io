import numpy as np
import ctypes

bitarray_dll = ctypes.CDLL("./cDll/BitArray/BitArrayDll.dll")

toStr_func = bitarray_dll.toStr
toStr_func.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int32, ctypes.c_int32]
toStr_func.restype = None

setItem_func = bitarray_dll.setBitItem
setItem_func.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32, ctypes.c_bool]
setItem_func.restype = None

setItemSlice_func = bitarray_dll.setBitItemSlice
setItemSlice_func.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32,
                              ctypes.c_int32, ctypes.c_int32]
setItemSlice_func.restype = None

getItem_func = bitarray_dll.getBitItem
getItem_func.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32]
getItem_func.restype = None

getItemSlice_func = bitarray_dll.getBitItemSlice
getItemSlice_func.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32,
                              ctypes.c_int32, ctypes.c_int32]
getItemSlice_func.restype = None

isZero_func = bitarray_dll.is_zero
isZero_func.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32]
isZero_func.restype = ctypes.c_bool

shiftLarray = bitarray_dll.shiftLarray
shiftLarray.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_int, ctypes.c_int32]
shiftLarray.restype = None

shiftHarray = bitarray_dll.shiftHarray
shiftHarray.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32,
                        ctypes.c_int32, ctypes.c_int32]
shiftHarray.restype = None

bitOr = bitarray_dll.bitOr
bitOr.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                  ctypes.c_int32]
bitOr.restype = None

bitEq = bitarray_dll.bitEq
bitEq.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32]
bitEq.restype = ctypes.c_bool

clone_func = bitarray_dll.clone
clone_func.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.c_int32]
clone_func.restype = None

bitAnd = bitarray_dll.bitAnd
bitAnd.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                   ctypes.c_int32]
bitAnd.restype = None


class BitArray:
    def __init__(self, bit_length):
        self.base_type = np.uint32
        self.bit_length = bit_length
        self.arr_length = (self.bit_length + 31) // 32
        self.arr = np.zeros([self.arr_length], self.base_type)

    def __and__(self, other):
        if isinstance(other, BitArray):
            if self.arr_length == other.arr_length and self.bit_length == other.bit_length:
                ans = BitArray(self.bit_length)
                bitAnd(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                       other.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                       ans.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                       self.arr_length)
                return ans
            else:
                raise ValueError("Input array must be in same size.")
        else:
            raise ValueError("Input type must be BitArray.")

    def __or__(self, other):
        if isinstance(other, BitArray):
            if self.arr_length == other.arr_length and self.bit_length == other.bit_length:
                ans = BitArray(self.bit_length)
                bitOr(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                      other.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                      ans.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                      self.arr_length)
                return ans
            else:
                raise ValueError("Input array must be in same size.")
        else:
            raise ValueError("Input type must be BitArray.")

    def clone(self):
        ans = BitArray(self.bit_length)
        clone_func(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                   ans.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                   self.arr_length)
        return ans

    def __setitem__(self, key, value):
        val = value == True
        if isinstance(key, slice):
            start = key.start
            stop = key.stop
            step = key.step
            start = 0 if (start is None or start < 0) else start
            stop = self.bit_length if (stop is None or stop > self.bit_length) else stop
            step = 1 if step is None else step
            setItemSlice_func(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)), val, start, stop, step)
        else:
            if isinstance(key, int):
                if key < 0 or key >= self.bit_length:
                    raise KeyError("Key value is out of range. It should be in [0, %d]" % (self.bit_length - 1))
                setItem_func(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)), key, val)
            else:
                raise KeyError("Key must be Slice or Int!")

    def __eq__(self, other):
        if isinstance(other, BitArray):
            if self.arr_length == other.arr_length and self.bit_length == other.bit_length:
                return bitEq(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                             other.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                             self.arr_length)
        return False

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start
            stop = item.stop
            step = item.step
            start = 0 if (start is None or start < 0) else start
            stop = self.bit_length if (stop is None or stop > self.bit_length) else stop
            step = 1 if step is None else step
            n = (stop - start + step - 1) // step
            ans = BitArray(n)
            getItemSlice_func(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                              ans.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                              start, stop, step)
            return ans
        else:
            if isinstance(item, int):
                if item < 0 or item >= self.bit_length:
                    raise KeyError("Key value is out of range. It should be in [0, %d]" % (self.bit_length - 1))
                ans = BitArray(1)
                getItem_func(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                             ans.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                             self.arr_length)
                return ans
            else:
                raise KeyError("Key must be Slice or Int!")

    def is_zero(self):
        ans = isZero_func(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)), self.arr_length)
        return ans

    def __lshift__(self, other):
        if not isinstance(other, int):
            raise ValueError('Input value must be Int.')
        ans = BitArray(self.bit_length)
        shiftLarray(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                    ans.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                    self.arr_length, other)
        return ans

    def __rshift__(self, other):
        if not isinstance(other, int):
            raise ValueError('Input value must be Int.')
        ans = BitArray(self.bit_length)
        shiftHarray(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                    ans.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                    self.arr_length, other, self.bit_length)
        return ans

    def __str__(self):
        s = (ctypes.c_ubyte * self.bit_length)()
        toStr_func(self.arr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                   s,
                   self.arr_length,
                   self.bit_length)
        s = ''.join(chr(byte) for byte in s)
        return s


if __name__ == '__main__':
    a = BitArray(10)
    a[2:10:2] = True
    b = BitArray(10)
    b[5:20] = True
    print(a)
    print(b)
    print(a & b)
    print(a | b)
    print('a: ',a)
    print(a>>3)
    print((a>>3)<<4)
    print(a==b)
    print(a.is_zero())
    print(BitArray(2).is_zero())
    c = a.clone()
    c = c>>2
    print(a[:10:2])
    pass
