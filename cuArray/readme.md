# cuArray README

## Overview

`cuArray` is a templated C++ class designed to manage multi-dimensional arrays on both the host (CPU) and the device (GPU) using CUDA. It provides functionalities to initialize, manipulate, and transfer data between the host and device. This class is particularly useful for scientific computing and machine learning applications that require efficient handling of large data sets on GPUs.

You can find the code for the `cuArray` class in the [`kernel.cu`](kernel.cu) file located in this directory.

## Features

- **Multi-dimensional Array Handling:** Supports arrays of arbitrary dimensions.
- **Host and Device Data Management:** Manages separate arrays on the host and the device.
- **CUDA Integration:** Provides methods to allocate memory, transfer data, and perform operations on the GPU.
- **Flexible Indexing:** Supports flexible indexing for accessing and setting elements in multi-dimensional arrays.
- **Memory Management:** Ensures proper allocation and deallocation of memory on both host and device.

## Class Members

### Private Methods

- `__getOffset(int* ptr, int r, int n)`: Calculates the offset for accessing elements.
- `__getOffset(int* ptr, int r, int n, Args ... args)`: Recursive template method for calculating offset for multi-dimensional arrays.

### Protected Members

- `T* h_arr`: Pointer to the host array.
- `T* d_arr`: Pointer to the device array.
- `int arrSize`: Total size of the array.
- `int shapeSize`: Number of dimensions.
- `int* h_shape`: Pointer to the host shape array.
- `int* d_shape`: Pointer to the device shape array.

### Protected Methods

- `int h_getOffsetIndex(Args ... args)`: Computes the offset index for accessing elements on the host.
- `__device__ int d_getOffsetIndex(Args ... args)`: Computes the offset index for accessing elements on the device.
- `T h_getItem(Args... args)`: Gets an element from the host array using variable arguments for indexing.
- `void h_setItem(T item, Args... args)`: Sets an element in the host array using variable arguments for indexing.
- `__device__ T d_getItem(Args... args)`: Gets an element from the device array using variable arguments for indexing.
- `__device__ void d_setItem(T item, Args... args)`: Sets an element in the device array using variable arguments for indexing.
- `void initShape(int* shape, int size)`: Initializes the shape of the array.
- `void calculateArrSize()`: Calculates the total size of the array.

### Public Methods

- `cuArray()`: Constructor.
- `void freeData()`: Frees allocated memory on both host and device.
- `void setData(T* data)`: Sets the host data.
- `T h_getItemOffset(int offset)`: Gets an element from the host array at a specific offset.
- `__device__ T d_getItemOffset(int offset)`: Gets an element from the device array at a specific offset.
- `void h_setItemOffset(int offset, T item)`: Sets an element in the host array at a specific offset.
- `__device__ void d_setItemOffset(int offset, T item)`: Sets an element in the device array at a specific offset.
- `void showArray()`: Displays the contents of the host array.
- `void showShape()`: Displays the shape of the array.
- `void allocateDeviceArray()`: Allocates memory for the device array.
- `void copyDataToDevice()`: Copies data from the host array to the device array.
- `void allocateDeviceShapeArray()`: Allocates memory for the device shape array.
- `void copyShapeToDevice()`: Copies the shape array from the host to the device.
- `void toDevice()`: Transfers both data and shape from host to device.
- `void toHost()`: Transfers data from device to host.
- `void toHost(T* h_ptr)`: Transfers data from device to a provided host pointer.
