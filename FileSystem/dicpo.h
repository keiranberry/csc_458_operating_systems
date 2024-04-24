#ifndef DICPO_H
#define DICPO_H

#define BLOCK_SIZE 128
#define NUM_BLOCKS 128

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

//function to write file to working directory
void writeFileFromDisk(const sfs_superblock* super, char* fileName);

//function to get block from file
void getFileBlock(sfs_inode_t* n, uint32_t blknum, char *data);

#endif