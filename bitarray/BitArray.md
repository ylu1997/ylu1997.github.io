# Introduction

A bit array is a data structure that encapsulates an array for bitwise operations on individual bits.
It provides a compact representation for manipulating sequences of bits efficiently. 
This documentation provides an overview of the bit array data structure implemented in C. 
The content of this document has been polished by GPT.

# Properties

- **base_type**: The data type used as the base structure for each element in the array.
    - `unsigned char`;
    - `unsigned int` ✔️.

- **baseSize**: The number of bits in each base type.
    - `unsigned char`: **baseSize** = 8;
    - `unsigned int`: **baseSize** = 32 (in 64-bit system) ✔️.

- **cell**: A unit for operations, consisting of a specific number of bits.
    - **cellNum**: The number of cells in the array.
    - **cellSize**: The number of bits in each cell.

- **bitLength**: The total number of bits in the array.
- **arrayLength**: The total number of elements in the array.

Relationships between properties:
\[ cellNum \times cellSize = bitLength \leq arrayLength \]
