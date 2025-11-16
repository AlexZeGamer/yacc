int add(int a, int b) {
    return a + b;
}

int clamp_to_zero(int value) {
    if (value < 0) {
        return 0;
    }
    return value;
}

int main() {
    int total;
    int adjusted;

    total = add(2, 3);
    adjusted = clamp_to_zero(total - 10);

    debug(total);
    debug(adjusted);

    return total;
}
