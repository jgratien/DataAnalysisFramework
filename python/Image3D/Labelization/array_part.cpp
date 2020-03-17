#include "array_part.h"

#include <stdlib.h>
#include <iostream>
#include <stdio.h>
#include <string.h>

#define BSIZE(nx, ny, nz) ((nx)*(ny)*(nz)*sizeof(float))

partitions* array_split_band(float* img, int nx, int ny, int nz, int n_part ){

    float* img_idx = (float*)malloc(BSIZE(nx, ny, nz));
    for( int i =0; i<nx*ny*nz; i++ ){
        img_idx[i] = (float)i;
    }

    partitions* parts = (partitions*)malloc(sizeof(partitions));

    parts->n_parts = n_part;
    parts->parts = (partition*)malloc(parts->n_parts*sizeof(partition));

    int nz_p = nz / n_part + 1;

    partition* part_ptr = parts->parts;

    int size_p = nx*ny*nz_p;

    part_ptr->nx = nx;
    part_ptr->ny = ny;
    part_ptr->nz = nz_p;
    part_ptr->idx = 0;
    part_ptr->array = (float*)calloc(size_p, sizeof(float)*2);
    memcpy(part_ptr->array+nx*ny, img, BSIZE(nx, ny, nz_p-1));
    memcpy(part_ptr->array + size_p + nx*ny, img_idx, BSIZE(nx, ny, nz_p-1));

    part_ptr++;

    for( int i=1; i<n_part; i++){
        part_ptr->nx = nx;
        part_ptr->ny = ny;
        part_ptr->nz = nz_p;
        part_ptr->idx = i;
        part_ptr->array = (float*)calloc(size_p*2, sizeof(float));
        memcpy(part_ptr->array, img+ nx*ny*(i*(nz_p-1)-1), BSIZE(nx, ny, nz_p));
        memcpy(part_ptr->array + size_p, img_idx+nx*ny*(i*(nz_p-1)-1), BSIZE(nx, ny, nz_p));
        part_ptr++;
    }

    free(img_idx);

    return parts;

}

void display_partitions(partitions* parts){
    printf("nb partitions %d \n", parts->n_parts);
    for(int i =0; i<parts->n_parts; i++ ){
        partition* part = parts->parts + i;
        printf("part %d \n", part->idx);
        printf("nx, ny, nz : %d %d %d\n", part->nx, part->ny, part->nz);
        int idx = 0;
        for( int z=0; z<part->nz; z++){
            for( int y=0; y<part->ny; y++){
                for( int x=0; x<part->nx; x++){
                    printf("%3.1f (%d) ", part->array[idx], (int)part->array[idx+part->nx*part->ny*part->nz]);
                    idx++;
                }
                printf("\n");
            }
            printf("---\n");
        }
    }
}

void free_partitions(partitions* parts){
    for( int i=0; i<parts->n_parts; i++ ){
        partition* part = parts->parts + i;
        free(part->array);
    }
    free(parts);
}

