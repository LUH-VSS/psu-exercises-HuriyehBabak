#include <stdio.h>
#include <time.h>

extern int l0_main();

static struct timespec ts0;
static void timestamp_reset(void) { // resets time
    clock_gettime(CLOCK_REALTIME, &ts0);
}

static double timestamp(void) { // returns miliseconds since the last reset
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (ts.tv_sec - ts0.tv_sec)*1000. + (ts.tv_nsec - ts0.tv_nsec) / 1000000.;
}


int main(void) {
    /* We use inline assembler here, as L0 does not obey any callee saved registers */
    int ret;
    timestamp_reset();
    asm volatile(
        "push %%ebp;"
        "call l0_main;" /// <-- Here is the acutal call
        "pop %%ebp;"
        : "=a"(ret) : : "ebx", "ecx", "edx", "edi", "esi");
    double runtime = timestamp();
    printf("L0 Return: %d\n", ret);
    printf("L0 Runtime: %.4fms\n", runtime);
    return 0;
}
