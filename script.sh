#!/bin/bash

echo "JM3XMTDQGR5HCRBSPBGWMOCXONMWKOKUOVLGEQZQNZFGQQLDNZSWS5LIJFKVSVC2IJVQU===" > /root/definetly_not_the_flag.txt
chmod 700 /root/





username="adm_pseudoX"
password="S1TuL1tC4T3sUnNULL"


useradd -m -s /bin/bash "$username"
echo "$username:$password" | chpasswd

usermod -aG sudo "$username"


sudoers_file="/etc/sudoers.d/$username"
echo "$username ALL=(ALL) PASSWD: /usr/bin/vim" > "$sudoers_file"
chmod 440 "$sudoers_file"

echo "nice try, its not the flag" > /home/$username/walletpassword.txt

chmod o+r /etc/sudoers.d/$username

binaries_to_restrict=(
    "/usr/bin/curl"
    "/usr/bin/wget"
    "/usr/bin/git"
    "/usr/bin/python3"
    "/usr/bin/sqlite3"
    "/usr/bin/python3-venv"
    "/usr/bin/python3-pip"
    "/usr/sbin/openssh-server"
)

for binary in "${binaries_to_restrict[@]}"; do
    if [ -f "$binary" ]; then
        chmod o-x "$binary"
        echo "Permissions d'exécution retirées pour $binary"
    fi
done
