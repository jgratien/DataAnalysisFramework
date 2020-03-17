#ifndef ARRAY_PART_H
#define ARRAY_PART_H

#include "dllexport.h"

extern "C" {

struct partition_t
{
    int idx;
    int nx;
    int ny;
    int nz;
    float* array;
};

typedef struct partition_t partition;

struct partitions_t {
    int n_parts;
    partition* parts;
};

typedef struct partitions_t partitions;

ARRAYPART_EXPORT partitions* array_split_band(float* img, int nx, int ny, int nz, int n_part );
ARRAYPART_EXPORT void display_partitions( partitions* parts );
ARRAYPART_EXPORT void free_partitions( partitions* parts );

}

#endif // ARRAY_PART_H
