#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include <iostream> 
#include <time.h>
#include <stdlib.h>
#include <math.h> 
#include <random>
#include <chrono> 

template<typename T>
void fillArrayWithRandomData(T* arr, int arrayLength, const T* charTable, int charTableLength) {
    auto seed = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    std::mt19937 gen(seed);
    std::uniform_int_distribution<int> dist(0, charTableLength - 1);

    for (int i = 0; i < arrayLength; ++i) {
        int randomIndex = dist(gen);
        arr[i] = charTable[randomIndex];
    }
}

void showCharArray(char* arr, int len) {
    for (int i = 0; i < len; i++) {
        printf("%c", arr[i]);
    }
    printf("\n");
}

template<typename T>
class cuArray {
private:

    __host__ __device__ int __getOffset(int* ptr, int r, int n) {
        return n + r;
    }

    template<typename ...Args>
    __host__ __device__
        int __getOffset(int* ptr, int r, int n, Args ... args) {
        return this->__getOffset(ptr + 1, (r + n) * (*(ptr + 1)), args...);
    }

protected:
    T* h_arr = nullptr;           // Host array pointer
    T* d_arr = nullptr;           // Device array pointer

    int arrSize = 1;              // Size of the array
    int shapeSize = 0;            // Number of dimensions of the array
    int* h_shape = nullptr;       // Host shape array pointer
    int* d_shape = nullptr;       // Device shape array pointer

    // L1, L2, ... 
    // c1, c2, ...
    template<typename ...Args>
    int h_getOffsetIndex(Args ... args) {
        return this->__getOffset(this->h_shape, 0, args...);
    }

    template<typename ...Args>
    __device__
        int d_getOffsetIndex(Args ... args) {
        return this->__getOffset(this->d_shape, 0, args...);
    }

    template<typename ...Args>
    T h_getItem(Args... args) {
        return this->h_getItemOffset(this->h_getOffsetIndex(args...));

    }

    template<typename ...Args>
    void h_setItem(T item, Args... args) {
        this->h_setItemOffset(this->h_getOffsetIndex(args...), item);
    }

    template<typename ...Args>
    __device__
        T d_getItem(Args... args) {
        return this->d_getItemOffset(this->d_getOffsetIndex(args...));
    }

    template<typename ...Args>
    __device__
        void d_setItem(T item, Args... args) { 
        this->d_setItemOffset(this->d_getOffsetIndex(args...), item);
    }

    // Initialize the shape of the array
    virtual void initShape(int* shape, int size) {
        this->shapeSize = size;   // Set the number of dimensions
        this->h_shape = new int[size];  // Allocate memory for the shape array
        for (int i = 0; i < size; i++) {
            this->h_shape[i] = shape[i];  // Copy the shape data
        }
        this->calculateArrSize(); // Calculate the total size of the array
        
        this->allocateDeviceShapeArray();
        this->copyShapeToDevice();
    }


    // Calculate the total size of the array
    void calculateArrSize() {
        for (int i = 0; i < this->shapeSize; i++) {
            this->arrSize *= this->h_shape[i];  // Multiply the dimensions to get the total number of elements
        }
    }

public:


    // cuArray constructor: does not modify external data
    cuArray() {};

    // Free allocated memory
    virtual void freeData() {
        if (this->d_arr != nullptr) {
            cudaFree(this->d_arr);  // Free device array memory
            this->d_arr = nullptr;
        }
        if (this->d_shape != nullptr) {
            cudaFree(this->d_shape);  // Free device shape array memory
            this->d_shape = nullptr;
        }
        if (this->h_shape != nullptr) {
            delete[] this->h_shape;  // Free host shape array memory
            this->h_shape = nullptr;
        }
    }

    // Set the host data
    virtual void setData(T* data) {
        this->h_arr = data;  // Assign the provided data pointer to the host array pointer
    }

    // Get the item at a given offset (host side)
    T h_getItemOffset(int offset) {
        return this->h_arr[offset];
    }

    // Get the item at a given offset (device side)
    __device__ T d_getItemOffset(int offset) {
        return this->d_arr[offset];
    }

    // Set the item at a given offset (host side)
    void h_setItemOffset(int offset, T item) {
        this->h_arr[offset] = item;
    }

    // Set the item at a given offset (device side)
    __device__ void d_setItemOffset(int offset, T item) { 
        this->d_arr[offset] = item;
    }

    // Display the array contents (host side)
    virtual void showArray() {
        if (this->h_arr == nullptr) {
            std::cout << "Array is empty" << std::endl;
            return;
        }

        std::cout << "Array data:" << std::endl;
        for (int i = 0; i < this->arrSize; ++i) {
            std::cout << this->h_arr[i] << " ";
        }
        std::cout << std::endl;
    }

    // Display the array shape (host side)
    void showShape() {
        std::cout << "The size of array: " << (this->arrSize * sizeof(T)) << " byte(s)" << std::endl;
        std::cout << "Shape: [";
        for (int i = 0; i < this->shapeSize; i++) {
            std::cout << this->h_shape[i] << ",";
        }
        std::cout << "]" << std::endl;
    }

    // Allocate memory for the device array
    void allocateDeviceArray() {
        if (this->d_arr == nullptr) {
            cudaMalloc((void**)&this->d_arr, sizeof(T) * this->arrSize);
        }
    }

    // Copy data to the device array
    void copyDataToDevice() {
        cudaMemcpy(this->d_arr, this->h_arr, sizeof(T) * this->arrSize, cudaMemcpyHostToDevice);
    }

    // Allocate memory for the device shape array
    void allocateDeviceShapeArray() {
        if (this->d_shape == nullptr) {
            cudaMalloc((void**)&this->d_shape, sizeof(int) * this->shapeSize);
        }
    } 

    // Copy shape data to the device array
    void copyShapeToDevice() {
        cudaMemcpy(this->d_shape, this->h_shape, sizeof(int) * this->shapeSize, cudaMemcpyHostToDevice);
    }


    // Transfer data from host to device
    virtual void toDevice() {
        this->allocateDeviceArray();
        if(this->h_arr != nullptr)
        {
            this->copyDataToDevice();
        }
    }

    // Transfer data from device to host
    virtual void toHost() {
        cudaMemcpy(this->h_arr, this->d_arr, sizeof(T) * this->arrSize, cudaMemcpyDeviceToHost); // Copy data to the host array
    }

    void toHost(T* h_ptr) {
        cudaMemcpy(h_ptr, this->d_arr, sizeof(T) * this->arrSize, cudaMemcpyDeviceToHost); // Copy data to the host array
    }
};


class SeqPair : public cuArray<char> {
public:
    SeqPair(int batchnum, int seqlen) {
        int shape[3] = { batchnum, 2, seqlen };
        this->initShape(shape, 3);
    }

    char h_getItem(int batchId, int seqId, int charId) {
        return cuArray<char>::h_getItem(batchId, seqId, charId);
    }

    void h_setItem(int batchId, int seqId, int charId, char item) {
        cuArray<char>::h_setItem(item, batchId, seqId, charId);
    }

    __device__ char d_getItem(int batchId, int seqId, int charId) {
        return cuArray<char>::d_getItem(batchId, seqId, charId);
        
    }

    __device__ void d_setItem(int batchId, int seqId, int charId, char item) {
        cuArray<char>::d_setItem(item, batchId, seqId, charId);
    }

};

class DpMatrix : public cuArray<int> {
public:
    DpMatrix(int batchNum, int rowNum, int colNum) {
        int shape[3] = { batchNum, rowNum, colNum };
        this->initShape(shape, 3);

    }

    int h_getItem(int batchId, int rowId, int colId) {
        return cuArray<int>::h_getItem(batchId, rowId, colId);
    }

    void h_setItem(int batchId, int rowId, int colId, int item) {
        cuArray<int>::h_setItem(item, batchId, rowId, colId);
    }

    __device__ int d_getItem(int batchId, int rowId, int colId) {
        
        return cuArray<int>::d_getItem(batchId, rowId, colId);
    }

    __device__ void d_setItem(int batchId, int rowId, int colId, int item) {
        cuArray<int>::d_setItem(item, batchId, rowId, colId);
    }
     

    __device__ void debug() {
        printf("debug\n");
        //cuArray<int>::d_getOffsetIndex(0, 1, 2);
        printf("xx%d\n", this->d_getOffsetIndex(0,1,3));
    }
};

class cuResult : public cuArray<int> {
public:
    cuResult(int batchNum) {
        int shape[2] = { batchNum,  };
        this->initShape(shape, 1);
    }

    int h_getItem(int batchId) {
        return cuArray<int>::h_getItem(batchId );
    }

    void h_setItem(int batchId, int item) {
        cuArray<int>::h_setItem(item, batchId );
    }

    __device__ int d_getItem(int batchId) {
        return cuArray<int>::d_getItem(batchId);
    }

    __device__ void d_setItem(int batchId, int item) {
        cuArray<int>::d_setItem(item, batchId);
    }
     
};

__global__ void levenshtein(SeqPair sp, DpMatrix dpmat, cuResult res, int len) {
    int t_id = threadIdx.x + blockDim.x * blockIdx.x;
    int m;
 
    for (int i = 0; i < len + 1; i++) {
        dpmat.d_setItem(t_id, i, 0, i);
    }
    for (int i = 0; i < len + 1; i++) {
        dpmat.d_setItem(t_id, 0, i, i);
    }

    for (int i = 1; i < len + 1; i++) {
        for (int j = 1; j < len + 1; j++) {
           if (sp.d_getItem(t_id, 0, i - 1) == sp.d_getItem(t_id, 1, j - 1)) {
                dpmat.d_setItem(t_id, i, j, dpmat.d_getItem(t_id, i - 1, j - 1));
            }
            else {
                m = min(dpmat.d_getItem(t_id, i, j - 1), min(dpmat.d_getItem(t_id, i - 1, j), dpmat.d_getItem(t_id, i - 1, j - 1))) + 1;
                dpmat.d_setItem(t_id, i, j, m);
            }
        }
    }
    res.d_setItem(t_id, dpmat.d_getItem(t_id, len, len));
}

int levenshteinDistance(const char* s1, const char* s2, int len) {
    int** dp = (int**)malloc((len + 1) * sizeof(int*));
    int cost;
    for (int i = 0; i <= len; i++) {
        dp[i] = (int*)malloc((len + 1) * sizeof(int));
    }

    for (int i = 0; i <= len; i++) {
        dp[i][0] = i;
        dp[0][i] = i;
    }

    for (int i = 1; i <= len; i++) {
        for (int j = 1; j <= len; j++) { 
            if (s1[i - 1] == s2[j - 1]) {
                cost = 0;
            }
            else {
                cost = 1;
            }
            dp[i][j] = min(dp[i - 1][j] + 1,  
                min(dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost)); // 替换
        }
    }

    int result = dp[len][len];

    for (int i = 0; i <= len; i++) {
        free(dp[i]);
    }
    free(dp);

    return result;
}
int main() {
    int b_num = 1024 * 4;
    int seq_len = 32;
    int blockNum = 128;
    int N = 2 * b_num * seq_len;
    char* strs = new char[N];
    char table[4] = { 'A','G','C','T' };
    fillArrayWithRandomData(strs, N, table, 4);
    SeqPair sp = SeqPair(b_num, seq_len);
    DpMatrix dpmat = DpMatrix(b_num, seq_len + 1, seq_len + 1);
    cuResult res = cuResult(b_num);
    int* ans = new int[b_num];
    ans[0] = 2;
    sp.setData(strs);
    std::cout << "block num: " << blockNum << " block size: " << b_num / blockNum << std::endl;
    clock_t start = clock();
    sp.toDevice();
    dpmat.toDevice();
    res.toDevice();
    levenshtein << <blockNum, b_num / blockNum >> > (sp, dpmat, res, seq_len);
    res.toHost(ans);
    clock_t end = clock();
    std::cout <<"gpu: " << end - start << std::endl;
    int a;
    start = clock();
    for (int i = 0; i < b_num; i++) {
        a = levenshteinDistance(strs + 2 * i * seq_len, strs + 2 * i * seq_len + seq_len, seq_len);
        //std::cout << ans[i]<<" "<< a <<" "<<(a == ans[i]) << std::endl;
        if (a != ans[i]) {
            std::cout << "error" << std::endl;
        }
    }
    end = clock();
    std::cout<<"cpu: " << end - start << std::endl;
    delete[] ans;
    delete[] strs;
    sp.freeData();
    res.freeData();
    dpmat.freeData();
    return 0;
}
