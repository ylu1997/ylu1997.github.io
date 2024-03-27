#include "pch.h"
#include "BitArray.h"


static int getIndex(int pos, int bitSize)
{
    return pos / bitSize;
}

static int getOffset(int pos, int bitSize)
{
    return pos % bitSize;
}

void getBitItem(unsigned int* arr, unsigned int* result, int bitIndex)
{
    const int index = getIndex(bitIndex, 32);
    const int offset = getOffset(bitIndex, 32);
    *result = (arr[index] >> offset) & 1u;
}

void getBitItemSlice(unsigned int* arr, unsigned int* result, int start, int end, int step)
{
    for (int i = 0;; i++) {
        if (start + step * i >= end) {
            break;
        }
        getBitItem(arr, result + i, start + step * i);
    }
}

void toStr(unsigned int* arr, unsigned char* str, int len, int bit_length)
{
    int index;
    int offset;
    unsigned int* item = new unsigned int[1];
    for (int i = 0; i < bit_length; i++) {
        index = getIndex(i, 32);
        offset = getOffset(i, 32);
        getBitItem(arr, item, i);
        if (item[0]) {
            str[i] = '1';
        }
        else {
            str[i] = '0';
        }
    }
    str[bit_length] = '\0';
}

void setBitItem(unsigned int* arr, int valIndex, bool val)
{
    const int index = getIndex(valIndex, 32);
    const int offset = getOffset(valIndex, 32);
    unsigned int v = 1u << offset;
    if (val) {
        arr[index] |= v;
    }
    else {
        arr[index] &= (~v);
    }
}

void setBitItemSlice(unsigned int* arr, bool val, int start, int end, int step)
{
    for (int i = 0;; i++) {
        if (start + step * i >= end) {
            break;
        }
        setBitItem(arr, start + step * i, val);
    }
}

bool is_zero(unsigned int* arr, int len)
{
    for (int i = 0; i < len; i++) {
        if (arr[i] != 0) {
            return false;
        }
    }
    return true;
}

void shiftLarray(unsigned int* arr, unsigned int* result, int len, int shiftAmount)
{
    // Calculate the number of integers to shift and the remaining shift amount
    const int index = getIndex(shiftAmount, 32);
    const int offset = getOffset(shiftAmount, 32);
    int n = len - index - 1;

    // Perform shifting
    if (offset != 0) {
        for (int i = 0; i < n; i++) {
            result[i] = (arr[index + i] >> offset);
            result[i] |= (arr[index + i + 1] << (sizeof(int) * 8 - offset));
        }
        result[n] = (arr[index + n] >> offset);
    }
    else {
        for (int i = 0; i < n; i++) {
            result[i] = arr[index + i];
        }
        result[n] = arr[index + n];
    }
}

void shiftHarray(unsigned int* arr, unsigned int* result, int len, int shiftAmount, int bitLength)
{
    const int index = getIndex(shiftAmount, 32);
    const int offset = getOffset(shiftAmount, 32);
    const int n = len - index - 1;
    const int bound_offset = (8 * sizeof(int) * len - bitLength);


    // Perform shifting
    if (offset != 0) {
        for (int i = 0; i < n; i++) {
            result[len - 1 - i] = (arr[len - 1 - (index + i)] << offset);
            result[len - 1 - i] |= (arr[len - 1 - (index + i + 1)] >> (sizeof(int) * 8 - offset));
        }
        result[len - 1 - n] = (arr[len - 1 - (index + n)] << offset);
    }
    else {
        for (int i = 0; i < n; i++) {
            result[len - 1 - i] = arr[len - 1 - (index + i)];
        }
        result[len - 1 - n] = arr[len - 1 - (index + n)];
    }

    // Handle boundary case
    if (bound_offset != 0) {
        result[len - 1] = (result[len - 1] << bound_offset) >> bound_offset;
    }
}

void bitOr(unsigned int* arr1, unsigned int* arr2, unsigned int* result, int len)
{
    for (int i = 0; i < len; i++) {
        result[i] = arr1[i] | arr2[i];
    }
}

bool bitEq(unsigned int* arr1, unsigned int* arr2, int len)
{
    for (int i = 0; i < len; i++)
    {
        if (arr1[i] != arr2[i]) {
            return false;
        }
    }
    return true;
}

void clone(unsigned int* arr, unsigned int* result, int len)
{
    for (int i = 0; i < len; i++) {
        result[i] = arr[i];
    }
}

void bitAnd(unsigned int* arr1, unsigned int* arr2, unsigned int* result, int len)
{
    for (int i = 0; i < len; i++) {
        result[i] = arr1[i] & arr2[i];
    }
}
