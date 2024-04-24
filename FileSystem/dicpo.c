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
    driver_read(rootDirNode, super->inodes); // Read the root directory inode

    int numBlocks = rootDirNode->size / BLOCK_SIZE;
    if(rootDirNode->size % BLOCK_SIZE != 0){
        numBlocks++;
    }

    char* currData = (char*)malloc(BLOCK_SIZE); // Allocate buffer for reading block data
    char* fileData = (char*)malloc(numBlocks * BLOCK_SIZE); // Allocate buffer for file data
    int currSize = 0;

    // Read all blocks of the root directory into fileData
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

    // Find the inode corresponding to the file name
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

    // If file not found, exit
    if(currNode == 0) {
        printf("File %s not found in the disk image.\n", fileName);
        exit(1);
    }

    // Calculate number of blocks needed to store the file
    int numFileBlocks = inode->size / BLOCK_SIZE;
    if(inode->size % BLOCK_SIZE != 0){
        numFileBlocks++;
    }

    // Allocate buffer for file content
    char* fileContent = (char*)malloc(numFileBlocks * BLOCK_SIZE);

    // Read each block of the file into fileContent
    for(int i = 0; i < numFileBlocks; i++){
        getFileBlock(inode, i, currData);
        memcpy(fileContent + (i * BLOCK_SIZE), currData, BLOCK_SIZE);
    }

    // Write the file content to a new file in the working directory
    FILE *fp = fopen(fileName, "wb");
    if (fp == NULL) {
        printf("Error opening file for writing.\n");
        exit(1);
    }

    fwrite(fileContent, sizeof(char), inode->size, fp); // Write file content to the file
    fclose(fp);

    // Free allocated memory
    free(currData);
    free(fileData);
    free(fileContent);
}

// void copyToWorkingDirectory(const sfs_superblock* super, char* fileName){
//     char buff[BLOCK_SIZE];

//     sfs_inode_t* rootDirNode = (sfs_inode_t*)buff;
//     driver_read(rootDirNode, super->inodes);        //root is at inode[0]
//     int numBlocks = rootDirNode->size / BLOCK_SIZE; //get number of blocks
//     if(rootDirNode->size % BLOCK_SIZE != 0){
//         numBlocks++;                                //if its not a full block, top it off
//     }

//     //currdata is one block, fileData is all of them
//     char* currData = (char*)malloc(sizeof(char) * BLOCK_SIZE);
//     char* fileData = (char*)malloc(sizeof(char) * (numBlocks * BLOCK_SIZE));
//     int currSize = 0;

//     for(int i = 0; i < numBlocks; i++){
//         getFileBlock(rootDirNode, i, currData);
//         memcpy(fileData + currSize, currData, BLOCK_SIZE);
//         currSize += BLOCK_SIZE;
//     }

//     int amountDirEntries = rootDirNode->size / sizeof(sfs_dirent);
//     sfs_dirent* entries = (sfs_dirent*)fileData;
//     uint32_t currNode = 0;
//     int temp = 0;
//     sfs_inode_t* inode = (sfs_inode_t*)calloc(sizeof(sfs_inode_t), sizeof(sfs_inode_t));
//     int i;

//     for(i = 0; i < amountDirEntries; i++){
//         if(strcmp(entries->name, fileName) != 0){
//             entries++;
//             continue;
//         }
//         currNode = entries->inode;
//         temp = currNode/2;
//         driver_read(inode, super->inodes + temp);
//         if(currNode % 2 != 0){
//             inode++;
//         }

//         break;
//     }

//     if(i == amountDirEntries){
//         printf("The file %s could not be found in the disk image", fileName);
//         exit(1);
//     }
//     free(currData);
//     free(fileData);
// }

//if the block size doubles then we are using 64 instead of 32 for all of this 
void getFileBlock(sfs_inode_t* n, uint32_t blknum, char *data){
    uint32_t ptrs[32];
    uint32_t tmp;
    if(blknum < 5){
        driver_read(data, n->direct[blknum]);
    }
    else if(blknum < 37){
        driver_read(ptrs, n->indirect);
        driver_read(data, ptrs[blknum - 5]);
    }
    else if(blknum < 1061){ //5 + 32 + 1024
        driver_read(ptrs, n->dindirect);
        tmp = (blknum - 5 - 32) / 32;
        tmp = ptrs[tmp];
        driver_read(ptrs, ptrs[tmp]);
        tmp = (blknum - 5 - 32) % 32;
        driver_read(data, ptrs[tmp]);
    }
    else if (blknum < 33829){ //5 + 32 + 1024 + 32^3
        driver_read(ptrs, n->tindirect);
        tmp = (blknum - 5 - 32 - 1024) / (32 * 32);
        tmp = ptrs[tmp];
        driver_read(ptrs, tmp);
        tmp = (blknum - 5 - 32 - 1024) / 32 % 32;
        tmp = ptrs[tmp];
        driver_read(ptrs, tmp);
        tmp = (blknum - 5 - 32 - 1024) % 32;
        driver_read(data, ptrs[tmp]);
    }
}