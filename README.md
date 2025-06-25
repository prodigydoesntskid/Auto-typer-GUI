# Prodigy's Suite - Advanced Automation & Utility Tool

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)

An all-in-one desktop application designed for power users, gamers, and Discord enthusiasts. Prodigy's Suite combines a powerful auto-typer, a sophisticated wordlist generator, Discord automation bots, and an integrated AI chat client into a single, sleek interface.

</div>

---

### Table of Contents

- [About The Project](#about-the-project)
- [Core Features](#core-features)
- [⚠️ Important Disclaimer](#️-important-disclaimer)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [How to Use](#how-to-use)
  - [Global Hotkeys](#global-hotkeys)
  - [Tab 1: Auto Typer](#tab-1-auto-typer)
  - [Tab 2: AR (Auto-Reply) Bot](#tab-2-ar-auto-reply-bot)
  - [Tab 3: GC (Group Chat) Changer](#tab-3-gc-group-chat-changer)
  - [Tab 4: WordList Generator](#tab-4-wordlist-generator)
  - [Tab 5: AI Chat (Gemini)](#tab-5-ai-chat-gemini)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## About The Project

Prodigy's Suite was built to consolidate multiple tools into one efficient and user-friendly application. Whether you need to automate typing for "chat packing," generate creative wordlists, automate Discord tasks, or consult with a powerful AI, this suite has you covered. The interface is built with `customtkinter` for a modern, responsive feel.

<p align="center">
  <i>(It's highly recommended to add a screenshot of the application here!)</i>
  <br>
  <img src="placeholder.png" alt="App Screenshot" width="600">
</p>

## Core Features

-   **🤖 Auto Typer**: Automatically types messages from a text file with adjustable WPM and delay.
-   **🛡️ Capture Protection**: Hides the application window from screenshots and screen recordings (Windows only).
-   **📝 WordList Generator**: Creates highly customized lists of "toxic" or "trolling" messages with options for typos, case, and structure.
-   **💬 AI Chat**: An integrated client for Google's Gemini AI, supporting both text and image-based prompts for advanced queries and content generation.
-   **👾 Discord AR Bot**: Automatically replies to a specific user on Discord.
-   **💥 Discord GC Changer**: Rapidly renames a Discord group chat, creating a "raid" effect.
-   **⌨️ Global Hotkeys**: Control the application's core functions without needing to have the window focused.
-   **💾 Persistent Settings**: All your configurations are saved automatically to `settings.json`.

## ⚠️ Important Disclaimer

This tool contains powerful automation features. Some of these features, particularly the **AR Bot** and **GC Changer**, may violate Discord's Terms of Service and can lead to account suspension or termination.

> [!WARNING]
> **Use at Your Own Risk!** The developer is not responsible for any bans or other disciplinary actions taken against your account. The **GC Changer** is especially high-risk and is almost guaranteed to be detected by Discord. Never use these features on an account you are not willing to lose. Be smart and responsible.

Never share your `settings.json` file, as it may contain sensitive information like your Discord token and AI API key.

## Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

You need to have Python installed on your system. The application also requires several Python libraries.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/prodigy-suite.git
    cd prodigy-suite
    ```

2.  **Install the required libraries:**
    The application requires `customtkinter`, `pyautogui`, `pynput`, and several libraries for the AI and Discord features. Install them all with pip:
    ```sh
    pip install customtkinter pyautogui pynput
    pip install discord.py
    pip install google-generativeai pillow
    ```

3.  **Run the application:**
    ```sh
    python a.py
    ```

## How to Use

### Global Hotkeys

-   **`F2`**: Start / Stop the Auto Typer macro.
-   **`F6`**: Un-hide (deiconify) the application window if it's minimized.
-   **`F8`**: Instantly save settings and close the application.

### Tab 1: Auto Typer

This is the core "chat packing" tool.

1.  **Create a Text File**: Create a `.txt` file. Write each message you want the typer to send. **Separate each message with a blank line (two newlines)**.
2.  **Load File**: Click `Load Text File (.txt)` and select your file.
3.  **Set Speed**: Adjust the `WPM` slider to control the typing speed.
4.  **Set Delay**: Adjust the `Delay Between Messages` slider to control the pause after each message is sent.
5.  **Hide from Capture (Windows Only)**: Check this box to make the application window appear black in screenshots and screen shares.
6.  **Activate**: Click on the chat box where you want to type, then press `F2` to start the macro. Press `F2` again to stop it.

### Tab 2: AR (Auto-Reply) Bot

Automatically replies to a specific user.

1.  **Discord Token**: Paste your Discord account token.
2.  **Target User ID**: Paste the User ID of the person you want to auto-reply to.
3.  **Reply Message**: Enter the message you want to send as a reply.
4.  **Start/Stop**: Click the button to start or stop the bot. The status label will indicate if it's running.

### Tab 3: GC (Group Chat) Changer

> [!CAUTION]
> **EXTREMELY HIGH BAN RISK.** This feature spams Discord's API and is easily detectable.

1.  **Discord Token**: Paste your Discord account token.
2.  **Group Chat ID**: Paste the ID of the group chat you want to rename.
3.  **Base Name**: Enter the base text for the name change (e.g., " raided"). The bot will append a counter (e.g., " raided 1", " raided 2").
4.  **Start/Stop**: Click the button to start or stop the spam.

### Tab 4: WordList Generator

Create custom wordlists for the Auto Typer.

1.  **Configure**: Set your desired options:
    -   `Target Name`: An optional name to include in the generated lines.
    -   `Number of Lines`: How many unique lines to generate.
    -   `Use Start/End Phrase`: Adds conversational bookends to the phrases.
    -   `Enable Typos`: Randomly introduces human-like typos.
    -   `Text Case`: Force uppercase, lowercase, or a random mix.
    -   `Prefix Symbol`: Add a symbol like `#` or `+` before each line.
2.  **Generate**: Click `Generate WordList`.
3.  **Save**: A file dialog will appear, allowing you to save the generated list as a `.txt` file, ready to be used by the Auto Typer.

### Tab 5: AI Chat (Gemini)

Leverage Google's Gemini AI for conversation, brainstorming, or content generation.

1.  **Get API Key**: You need a Google AI API key. You can get one for free from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Initialize**: Paste your API key into the entry field and click `Set Key & Init`. The status label will confirm a successful connection.
3.  **Chat**:
    -   Type your message in the text box at the bottom.
    -   Optionally, click `Attach Image` to include an image in your prompt.
    -   Press `Shift+Enter` or click `Send` to submit your prompt.
    -   The conversation will appear in the chat window.

## Configuration

Your settings for all tabs are automatically saved to `settings.json` when you close the application or press `F8`. This allows you to retain your tokens, IDs, and slider preferences between sessions.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
