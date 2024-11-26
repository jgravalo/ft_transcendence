#include<iostream>
#include<fcntl.h>
#include<unistd.h>
#include<sys/wait.h>

int main(int argc, char **argv, char **envp)
{
	if (argc != 2)
		return 1;
	char	s[3][4][100] = {{"git", "add", "."}, {"git", "commit", "-m", argv[1]}, {"git", "push"}};
	for (int i = 0; i < 3; i++)
	{
		pid_t pid = fork();
		if (pid == 0)
			execve(s[i][0], &s[i][0], envp);
		waitpid(pid, NULL, 0);
	}
	return 0;
}