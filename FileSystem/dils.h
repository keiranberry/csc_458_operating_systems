#ifndef DILS_H
#define DILS_H

#include <driver.h>
#include <sfs_superblock.h>
#include <sfs_inode.h>
#include <sfs_dir.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
//function to print usage statement and exit
void printUsageAndExit();

//function to get block from file
void getFileBlock(sfs_inode_t* n, uint32_t blknum, char *data);

//function to list root directory
void listRootDirectory(const sfs_superblock* super);


#endif