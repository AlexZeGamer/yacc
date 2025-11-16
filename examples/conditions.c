int main() {
    int score;
    int threshold;

    score = 7;
    threshold = 5;

    if (score > threshold) {
        debug(100);
    } else {
        debug(0);
    }

    if (score == 7) {
        debug(score);
    } else {
        debug(-1);
    }

    return 0;
}
