import subprocess

COMMAND_TEMPLATES = {
    "nmap_quick": "nmap -T4 -F {target}",
    "nmap_full": "nmap -sV -sC -p- {target}",
    "ffuf": "ffuf -u https://{target}/FUZZ -w /usr/share/wordlists/dirb/common.txt",
    "sqlmap": "sqlmap -u https://{target} --batch --banner",
    "whois": "whois {target}",
    "dig": "dig any {target} +short",
    "curl_head": "curl -I https://{target}"
}

def launch_terminal(action_key: str, target: str):
    template = COMMAND_TEMPLATES.get(action_key, "{target}")
    full_cmd = template.format(target=target)

    cmd_str = f"echo 'SUGGESTED COMMAND:'; echo '{full_cmd}'; echo ''; exec bash"
    terminals = [
        ["konsole", "--noclose", "-e", "bash", "-c", cmd_str],
        ["alacritty", "-e", "bash", "-c", cmd_str],
        ["kitty", "bash", "-c", cmd_str],
        ["xfce4-terminal", "--hold", "-e", f"bash -c '{cmd_str}'"],
        ["xterm", "-hold", "-e", f"bash -c '{cmd_str}'"]
    ]

    for term in terminals:
        try:
            subprocess.Popen(term, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            ...
    return False