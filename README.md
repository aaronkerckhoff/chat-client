# Chat-Client in python

## Features

The Chat-Client contains following features:

    - ✅End-To-End Encryption 🔒💬
    - ✅Beautiful, user-friendly GUI 🖥️
    - ✅Censoring of innapropriate messages 🚫
    - ✅Allow to block and unblock others ⛔




## Key Concepts

A Chat-Client using TCP to communicate through a server. The server can be found in [server.py](server.py).
When sending a message, a specific protocol is used to send:

                - Version identifier to check whether the right protocol is used
                - from_buf to check whether the message is from the buffer
                - type which can be BROADCAST for all or DIRECTED for a specific person
                - the receiver
                - the inner which is the message

This is just a general explanation. Take a look at [protokoll_spez.md](protokoll_spez.md), if interested in more specific information.
In [Source](/src) one can find the key scripts for different features. These consist of the cryptography to encode and decode messages, the gui,
extra functions for a more friendly usage and scripts to connect all of the aspects. One can also find a buffer script, which allows users to recall old
messages after reconnecting.

## Structure of Code

```
chat-client/
├── src/
│   ├── main.py
│   ├── gui/
|   |   ├── web_client/
|   |   |   └── client.py
│   │   ├── main_gui_start.py
│   │   ├── censor_bad_words.py
│   │   ├── client_socket.py
│   │   ├── client_state.py
│   │   ├── buffer.py
│   │   ├── crypto.py
│   │   ├── logger_utils.py
│   │   ├── packet_creator.py
│   │   ├── packet_parser.py
│   │   ├── public_key.py
│   │   ├── signature.py
|   |   └── blocking.py
│   └── 
├── tests/
│   └── test_crypto.py
├── README.md
├── protokoll_spez.md
├── .gitignore
├── environment.yml
├── requirements.txt
└── server.py
```



## Contributers

[Aaron](https://github.com/aaronkerckhoff) \
[Mathis](https://github.com/dickWittmann) \
[Richard](https://github.com/1TheCrazy) \
[Nina](https://github.com/nzi00) \
[Leah](https://github.com/Ekischleki) \
[Martin](https://github.com/Moxile)
