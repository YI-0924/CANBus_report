#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

void* send_message(void* arg)
{
	while(1)
	{
		system("./cansend vcan0 000#0000000000000000");
	}
	return NULL;
}
int main()
{
	pthread_t threads[10000];
	for(int i=0;i<10000;i++)
	{
		pthread_create(&threads[i],NULL,send_message,NULL);
	}
	while(1)
	{
		sleep(1);
	}
	return 0;
}
