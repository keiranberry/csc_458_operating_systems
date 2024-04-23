#include <dils.h>

#define BLOCK_SIZE 128
#define NUM_BLOCKS 128

int main(int argc, char** argv)
{
    char raw_superblock[BLOCK_SIZE]; // declare a buffer that is the same size as a filesystem block
    sfs_superblock *super = (sfs_superblock *)raw_superblock; // Create a pointer to the buffer
    char* diskImageName;
    int shortListing = 0;
    int longListing = 0;

    if(argc == 2){
        diskImageName = argv[1];
        shortListing = 1;
    }
    else if(argc == 3){
        if(strcmp(argv[2], "-l") == 0){
            diskImageName = argv[1];
            longListing = 1;
        }
        else{
            printUsageAndExit();
        }
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
    else if(shortListing){
        listRootDirectory(super);
    }
    else if(longListing){
        longListRootDirectory(super);
    }
    else{
        printf("An error occurred.");
    }

    // close the disk image
    driver_detach_disk_image();

    return 0;
}

void printUsageAndExit(){
    printf("Incorrect usage.\n  Usage: ./dils diskimagename\n  Usage: ./dils diskimagename -l\n");
    exit(1);
}

void listRootDirectory(const sfs_superblock* super) {
    char buff[BLOCK_SIZE];
    sfs_inode_t* rootDirNode = (sfs_inode_t*)buff;
    driver_read(rootDirNode, super->inodes);

    int numBlocks = rootDirNode->size / BLOCK_SIZE;
    if(rootDirNode->size %128 != 0){
        numBlocks++;
    }


    char* currData = (char*)malloc(BLOCK_SIZE);
    char* fileData = (char*)malloc(numBlocks * BLOCK_SIZE);
    int currSize = 0;

    int blockNum = rootDirNode->size / 128;
    if(rootDirNode->size % 128){
        blockNum++;
    }

    for(int i = 0; i < blockNum; i++){
        getFileBlock(rootDirNode, i, currData);
        memcpy(fileData + currSize, currData, BLOCK_SIZE);
        currSize += BLOCK_SIZE;
    }

    int amountDirEntries = rootDirNode->size / sizeof(sfs_dirent);
    sfs_dirent* entries = (sfs_dirent*)fileData;

    for(int i = 0; i < amountDirEntries; i++){
        printf("%s\n", entries->name);
        entries++;
    }

    free(currData);
    free(fileData);
}

void longListRootDirectory(const sfs_superblock* super) {
    char buff[BLOCK_SIZE];

    sfs_inode_t* rootDirNode = (sfs_inode_t*)buff;
    driver_read(rootDirNode, super->inodes);
    int numBlocks = rootDirNode->size / BLOCK_SIZE;
    if(rootDirNode->size % BLOCK_SIZE != 0){
        numBlocks++;
    }

    char* currData = (char*)malloc(sizeof(char) * BLOCK_SIZE);
    char* fileData = (char*)malloc(sizeof(char) * (numBlocks * BLOCK_SIZE));
    int currSize = 0;

    int blockNum = rootDirNode->size / 128;
    if(rootDirNode->size % 128){
        blockNum++;
    }

    for(int i = 0; i < blockNum; i++){
        getFileBlock(rootDirNode, i, currData);
        memcpy(fileData + currSize, currData, BLOCK_SIZE);
        currSize += BLOCK_SIZE;
    }

    int amountDirEntries = rootDirNode->size / sizeof(sfs_dirent);
    sfs_dirent* entries = (sfs_dirent*)fileData;
    uint32_t currNode = 0;
    int temp = 0;
    sfs_inode_t* inode = (sfs_inode_t*)malloc(sizeof(sfs_inode_t));

    printf("amountdirentries: %d\n", amountDirEntries);

    for(int i = 0; i < amountDirEntries; i++){
        printf("%d", i);
        currNode = entries->inode;
        temp = currNode/2;
        driver_read(inode, super->inodes + temp);
        if(currNode % 2 != 0){
            inode++;
        }
        printf("%s %ld %d\n", entries->name, inode->size, inode->owner);
        entries++;
    }
    free(currData);
    free(fileData);
}

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

//use something like asc_time() for the time (read the man pages)
//time should be day of week -> month -> day -> time (military time) -> year
//all of the time stamps should show up from dec 1969 around 1700
