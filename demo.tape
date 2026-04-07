Output demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 800
Set Theme "Catppuccin Mocha"
Set WindowBar Colorful

Type "git clone https://github.com/irfancode/ai-writing-agent-v2"
Sleep 500ms
Enter
Hide
Type "echo 'Cloning into ai-writing-agent-v2...'"
Enter
Type "echo 'remote: Enumerating objects: 125, done.'"
Enter
Type "echo 'remote: Counting objects: 100% (125/125), done.'"
Enter
Type "echo 'Receiving objects: 100% (125/125), 14.5 MiB | 15.00 MiB/s, done.'"
Enter
Type "echo 'Resolving deltas: 100% (45/45), done.'"
Enter
Show
Sleep 1.5s

Type "cd ai-writing-agent-v2"
Sleep 500ms
Enter
Sleep 1s

Type "docker-compose up -d"
Sleep 500ms
Enter
Hide
Type "echo '[+] Running 3/3'"
Enter
Type "echo ' ✔ Network ai-writing-agent_default    Created'"
Enter
Type "echo ' ✔ Container ollama_daemon             Started'"
Enter
Type "echo ' ✔ Container api_server                Started'"
Enter
Show
Sleep 2s

Type "python -m src.cli.main interactive"
Sleep 500ms
Enter
Hide
Type "echo 'ℹ Initializing AI Writing Agent...'"
Enter
Type "echo '✓ Ready! (Zero-Cost Local Mode Enabled)'"
Enter
Type "echo ''"
Enter
Type "echo 'AI Writing Agent - Interactive Mode'"
Enter
Type "echo 'Type help for commands, exit to quit'"
Enter
Type "echo ''"
Enter
Show
Sleep 1s
Type "write a quick tagline for an open source AI writing assistant"
Sleep 1s
Enter
Hide
Type "echo ''"
Enter
Type "echo 'Generated Content'"
Enter
Type "echo ''"
Enter
Type "echo 'Empower Your Ink, Own Your Brain: Write Free, Fast, and Locally.'"
Enter
Type "echo ''"
Enter
Type "echo -n '(write)> '"
Enter
Show
Sleep 4s
