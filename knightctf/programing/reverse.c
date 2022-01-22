#include <stdio.h>
#include <string.h>

int main() {
	char flag[25] = "CFb5cp0rm1gK{1r4nT_m4}6";
	int length = strlen(flag);

	// puts(flag);
	// printf("\n\n");
	// for (int i=0; i < length; i++) {
	// 	for (int j=i; j < length - 1; j++) {
	// 		char x = flag[j];
	// 		flag[j] = flag[j+1];
	// 		flag[j+1] = x;
	// 	}
	// }

	// puts(flag);
	// printf("\n\n");


	for (int i=length-1; i>0; i--){
		for (int j=length-1; j>=i; j--){
			char x = flag[j];
			flag[j] = flag[j-1];
			flag[j-1] = x;
		}

	}
	puts(flag);

	return 0;
}

// flag: KCTF{b451c_pr06r4mm1ng}


// Slove by test output
/*
Write step loop --> reverse it back step by step --> convert it to C code
i j
4 4
3 4 3
2 4 3 2
1 4 3 2 1
/*