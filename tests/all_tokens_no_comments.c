int arr[3] = {1, 2, 3};
int *ptr = &arr[0];

int add(int a, int b) { return a + b; }

void debug_send_recv_example() {
    int x = 10, y = 20, z = 0; 

    z = x + y - (x * y) / (x % y); 
    
    if ((x < y) && (y > 0) || !(z == 0)) { 
        debug(x); 
        send(x, y); 
    } else { 
        recv(z); 
    }

    int i = 0;
    do {
        i = i + 1;
        if (i == 2) { continue; }
        if (i >= 3) { break; }
    } while (i <= 3);
    
    for (int j = 0; j < 3; j = j + 1) {
        z = z + arr[j];
    }
    
    *ptr = *ptr + 1; 
}

int main(void) {
    int a = 1, b = 2;
    int c = add(a, b);

    if (a != b) { 
        c = c;
    }

    return 0; 
}
