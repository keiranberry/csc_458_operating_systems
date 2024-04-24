#include <dicpo.h>

int main(int argc, char** argv)
{
    char raw_superblock[BLOCK_SIZE]; // declare a buffer that is the same size as a filesystem block
    sfs_superblock *super = (sfs_superblock *)raw_superblock; // Create a pointer to the buffer
    char* diskImageName;
    char* fileToWrite;

    if(argc == 3){ //there is only one correct usage of this program
        diskImageName = argv[1];
        fileToWrite = argv[2];
    }
    else{
        printUsageAndExit();
    }
  
    // open the disk image and get it ready to read/write blocks
    driver_attach_disk_image(diskImageName, BLOCK_SIZE);

    int block_number = 0;
    int superblock_found = 0;

    while (block_number < NUM_BLOCKS) {
        // read block from the disk image
        driver_read(super, block_number);

        // check if it's the filesystem superblock
        if (super->fsmagic == VMLARIX_SFS_MAGIC &&
            !strcmp(super->fstypestr, VMLARIX_SFS_TYPESTR)) {
            superblock_found = 1;
            break; // exit the loop since superblock is found
        }

        block_number++;
    }

    if (!superblock_found) {
        printf("Superblock not found in the disk image.\n");
        driver_detach_disk_image();
        exit(1);
    }
    
    writeFileFromDisk(super, fileToWrite);

    // close the disk image
    driver_detach_disk_image();

    return 0;
}

void printUsageAndExit(){
    printf("Incorrect usage.\n  Usage: ./dils diskimagename\n  Usage: ./dils diskimagename -l\n");
    exit(1);
}

void writeFileFromDisk(const sfs_superblock* super, char* fileName) {
    char buff[BLOCK_SIZE];
    sfs_inode_t* rootDirNode = (sfs_inode_t*)buff;
    driver_read(rootDirNode, super->inodes); // root directory inode

    int numBlocks = rootDirNode->size / BLOCK_SIZE;
    if(rootDirNode->size % BLOCK_SIZE != 0){
        numBlocks++;
    }

    char* currData = (char*)malloc(BLOCK_SIZE); //buffer for current block of data
    char* fileData = (char*)malloc(numBlocks * BLOCK_SIZE); // buffer for file data
    int currSize = 0;

    // read in root directory
    for(int i = 0; i < numBlocks; i++){
        getFileBlock(rootDirNode, i, currData);
        memcpy(fileData + currSize, currData, BLOCK_SIZE);
        currSize += BLOCK_SIZE;
    }

    int amountDirEntries = rootDirNode->size / sizeof(sfs_dirent);
    sfs_dirent* entries = (sfs_dirent*)fileData;
    uint32_t currNode = 0;
    int temp = 0;
    sfs_inode_t* inode = (sfs_inode_t*)calloc(sizeof(sfs_inode_t), sizeof(sfs_inode_t));

    // find the inode for the file 
    for(int i = 0; i < amountDirEntries; i++){
        if(strcmp(entries->name, fileName) == 0){
            currNode = entries->inode;
            temp = currNode/2;
            driver_read(inode, super->inodes + temp);
            if(currNode % 2 != 0){
                inode++;
            }
            break;
        }
        entries++;
    }

    // if the file isn't found, it's an error
    if(currNode == 0) {
        printf("File %s not found in the disk image.\n", fileName);
        exit(1);
    }

    // calculate blocks needed
    int numFileBlocks = inode->size / BLOCK_SIZE;
    if(inode->size % BLOCK_SIZE != 0){
        numFileBlocks++;
    }

    char* fileContent = (char*)malloc(numFileBlocks * BLOCK_SIZE);

    // read each block into fileContent
    for(int i = 0; i < numFileBlocks; i++){
        getFileBlock(inode, i, currData);
        memcpy(fileContent + (i * BLOCK_SIZE), currData, BLOCK_SIZE);
    }

    FILE *fp = fopen(fileName, "wb");
    if (fp == NULL) {
        printf("Error opening file for writing.\n");
        exit(1);
    }

    fwrite(fileContent, sizeof(char), inode->size, fp); //write to the file
    fclose(fp);

    // free allocated memory
    free(currData);
    free(fileData);
    free(fileContent);
}

//if the block size doubles then we are using 64 instead of 32 for all of this 
void getFileBlock(sfs_inode_t* n, uint32_t blknum, char *data){
    uint32_t ptrs[NUM_INDIRECT];
    uint32_t tmp;
    if(blknum < NUM_DIRECT){
        driver_read(data, n->direct[blknum]);
    }
    else if(blknum < NUM_DIRECT + NUM_INDIRECT){
        driver_read(ptrs, n->indirect);
        driver_read(data, ptrs[blknum - NUM_DIRECT]);
    }
    else if(blknum < NUM_DIRECT + NUM_INDIRECT + NUM_DINDIRECT){ //5 + 32 + 1024
        driver_read(ptrs, n->dindirect);
        tmp = (blknum - NUM_DIRECT - NUM_INDIRECT) / NUM_INDIRECT;
        driver_read(ptrs, ptrs[tmp]);
        tmp = (blknum - NUM_DIRECT - NUM_INDIRECT) % NUM_INDIRECT;
        driver_read(data, ptrs[tmp]);
    }
    else if (blknum < NUM_DIRECT + NUM_INDIRECT + NUM_DINDIRECT + NUM_TINDIRECT){ //5 + 32 + 1024 + 32^3
        driver_read(ptrs, n->tindirect);
        tmp = (blknum - NUM_DIRECT - NUM_INDIRECT - NUM_DINDIRECT) / (NUM_INDIRECT * NUM_INDIRECT);
        tmp = ptrs[tmp];
        driver_read(ptrs, tmp);
        tmp = (blknum - NUM_DIRECT - NUM_INDIRECT - NUM_DINDIRECT) / NUM_INDIRECT % NUM_INDIRECT;
        tmp = ptrs[tmp];
        driver_read(ptrs, tmp);
        tmp = (blknum - NUM_DIRECT - NUM_INDIRECT - NUM_DINDIRECT) % NUM_INDIRECT;
        driver_read(data, ptrs[tmp]);
    }
}