int main() {
    int i;
    int sum;

    i = 0;
    while (i < 3) {
        debug(i);
        i = i + 1;
    }

    sum = 0;
    for (int j = 0; j < 4; j = j + 1) {
        sum = sum + j;
    }
    debug(sum);

    int k;
    k = 0;
    do {
        debug(k);
        k = k + 1;
    } while (k < 2);

    return 0;
}
