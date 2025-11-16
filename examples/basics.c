int main() {
    int value;
    int delta;

    value = 1;
    delta = 2 * 3;
    value = value + delta;   // 1 + 6 = 7
    debug(value);

    value = value - 4;
    debug(value);

    return 0;
}
