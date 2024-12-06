#include<stdio.h>
#include<stdlib.h>
int main(){
    char command[100];
    int id;
	while(1){
        id = rand()&0x3FF;
        if(id == 580||id == 411||id == 392||id == 0x200)
            continue;
        snprintf(command, 49, "./cansend vcan0 %x#%x", id, rand()&0xFFFFFFFF);
	    system(command);
        usleep(20);
    }
    printf("done");
}