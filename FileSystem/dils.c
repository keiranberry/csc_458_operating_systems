#include <dils.h>

int main(int argc, char** argv)
{
    char raw_superblock[BLOCK_SIZE]; // declare a buffer that is the same size as a filesystem block
    sfs_superblock *super = (sfs_superblock *)raw_superblock; // Create a pointer to the buffer
    char* diskImageName;
    int shortListing = 0;
    int longListing = 0;

    if(argc == 2){ //if the only argument is the disk image then do short listing
        diskImageName = argv[1];
        shortListing = 1;
    }
    else if(argc == 3){ //otherwise make sure the argument is -l
        if(strcmp(argv[2], "-l") == 0){
            diskImageName = argv[1];
            longListing = 1;
        }
        else{
            printUsageAndExit();
        }
    }   //if usage is wrong, print the usage and leave
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
        //if its not short listing or long listing, something is wrong
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

    //allocate currData and fileData for reading in
    char* currData = (char*)malloc(BLOCK_SIZE); //size of one block
    char* fileData = (char*)malloc(numBlocks * BLOCK_SIZE); //size of all the blocks we need
    int currSize = 0;

    for(int i = 0; i < numBlocks; i++){
        getFileBlock(rootDirNode, i, currData); //get the block and put it in currData
        memcpy(fileData + currSize, currData, BLOCK_SIZE); //put currData in fileData
        currSize += BLOCK_SIZE; //increment currSize
    }

    int amountDirEntries = rootDirNode->size / sizeof(sfs_dirent);
    sfs_dirent* entries = (sfs_dirent*)fileData;

    for(int i = 0; i < amountDirEntries; i++){
        printf("%s\n", entries->name); //print name
        entries++;
    }

    free(currData); //free memory
    free(fileData);
}

void longListRootDirectory(const sfs_superblock* super) {
    char buff[BLOCK_SIZE];

    sfs_inode_t* rootDirNode = (sfs_inode_t*)buff;
    driver_read(rootDirNode, super->inodes);        //root is at inode[0]
    int numBlocks = rootDirNode->size / BLOCK_SIZE; //get number of blocks
    if(rootDirNode->size % BLOCK_SIZE != 0){
        numBlocks++;                                //if its not a full block, top it off
    }

    //currdata is one block, fileData is all of them
    char* currData = (char*)malloc(sizeof(char) * BLOCK_SIZE);
    char* fileData = (char*)malloc(sizeof(char) * (numBlocks * BLOCK_SIZE));
    int currSize = 0;

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

    for(int i = 0; i < amountDirEntries; i++){
        currNode = entries->inode;
        temp = currNode/2;
        driver_read(inode, super->inodes + temp);
        if(currNode % 2 != 0){
            inode++;
        }
        
        char type;
        switch (inode->type) {
            case FT_NORMAL: type = '-'; break;
            case FT_DIR: type = 'd'; break;
            case FT_CHAR_SPEC: type = 'c'; break;
            case FT_BLOCK_SPEC: type = 'b'; break;
            case FT_PIPE: type = 'p'; break;
            case FT_SOCKET: type = 's'; break;
            case FT_SYMLINK: type = 'l'; break;
            default: type = '?'; break; // unknown type
        }

        // print permissions with masks
        char permissions[10];
        permissions[0] = (inode->perm & 0400) ? 'r' : '-';
        permissions[1] = (inode->perm & 0200) ? 'w' : '-';
        permissions[2] = (inode->perm & 0100) ? 'x' : '-';
        permissions[3] = (inode->perm & 0040) ? 'r' : '-';
        permissions[4] = (inode->perm & 0020) ? 'w' : '-';
        permissions[5] = (inode->perm & 0010) ? 'x' : '-';
        permissions[6] = (inode->perm & 0004) ? 'r' : '-';
        permissions[7] = (inode->perm & 0002) ? 'w' : '-';
        permissions[8] = (inode->perm & 0001) ? 'x' : '-';
        permissions[9] = '\0';

        // print everything up until time
        printf("%c%s %6d %6d %6u %6ld  ", type, permissions, inode->refcount, inode->owner, inode->group, inode->size);

        print_time(inode->atime);

        // File name
        printf("%s\n", entries->name);

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

void print_time(uint32_t timestamp) {
    struct tm *tm_info;
    time_t time_value = (time_t)timestamp;

    tm_info = gmtime(&time_value);

    // convert struct to time string
    char buffer[30];
    strftime(buffer, sizeof(buffer), "%a %b %d %H:%M:%S %Y", tm_info);

    printf("%s ", buffer);
}