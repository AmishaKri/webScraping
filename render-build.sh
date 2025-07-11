#!/usr/bin/env bash
# Install Google Chrome for Selenium
wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update
apt-get install -y /tmp/chrome.deb 