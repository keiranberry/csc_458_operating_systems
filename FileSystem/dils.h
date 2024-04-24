#ifndef DILS_H
#define DILS_H

#define BLOCK_SIZE 128
#define NUM_BLOCKS 128
#define NUM_DIRECT 5
#define NUM_INDIRECT 32
#define NUM_DINDIRECT 32 * 32       //1024
#define NUM_TINDIRECT 32 * 32 * 32  //32768

#include <driver.h>
#include <sfs_superblock.h>
#include <sfs_inode.h>
#include <sfs_dir.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
//function to print usage statement and exit
void printUsageAndExit();

//function to get block from file
void getFileBlock(sfs_inode_t* n, uint32_t blknum, char *data);

//function to list root directory
void listRootDirectory(const sfs_superblock* super);

//function to long list root directory
void longListRootDirectory(const sfs_superblock* super);

//function to print time
void print_time(uint32_t timestamp);

#endif