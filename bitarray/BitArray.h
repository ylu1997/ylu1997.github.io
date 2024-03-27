#pragma once

#define DLL_BITARRAY extern "C" __declspec(dllimport)

static int getIndex(int pos, int bitSize);

static int getOffset(int pos, int bitSize);

DLL_BITARRAY void getBitItem(unsigned int* arr, unsigned int* result, int bitIndex);

DLL_BITARRAY void getBitItemSlice(unsigned int* arr, unsigned int* result, int start, int end, int step);

DLL_BITARRAY void toStr(unsigned int* arr, unsigned char* str, int len, int bit_length);

DLL_BITARRAY void setBitItem(unsigned int* arr, int valIndex, bool val);

DLL_BITARRAY void setBitItemSlice(unsigned int* arr, bool val, int start, int end, int step);

DLL_BITARRAY bool is_zero(unsigned int* arr, int len);

DLL_BITARRAY void shiftLarray(unsigned int* arr, unsigned int* result, int len, int shiftAmount);

DLL_BITARRAY void shiftHarray(unsigned int* arr, unsigned int* result, int len, int shiftAmount, int bitLength);

DLL_BITARRAY void bitOr(unsigned int* arr1, unsigned int* arr2, unsigned int* result, int len);

DLL_BITARRAY bool bitEq(unsigned int* arr1, unsigned int* arr2, int len);

DLL_BITARRAY void clone(unsigned int* arr, unsigned int* result, int len);

DLL_BITARRAY void bitAnd(unsigned int* arr1, unsigned int* arr2, unsigned int* result, int len);