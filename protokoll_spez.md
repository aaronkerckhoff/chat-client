# Das Chat Client Protokoll
## Head (Ersten 32 bit)
**Bit 0-7**: Magic number (69) 0b0100_0101
    Genutzt zur identifizierung des Protokolls
**Bit 8-15**: Standart Protokoll Version. Momentan 0
**Bit 16-31**: Client-speziefische Version. Default-Protokoll hat hier Nullen

## Body (Für Default-Protokoll)
Der Body ist vom Ende des Heads bis zum Ende des Pakets. Er ist in einem utf-8-encodierten String, der selbst im JSON Format ist.

Wir benutzen verschiedene Level von Abstraktionen von den JSON Objekten.



- Level 0:
    - from_buf: *Bool* - Ob eine Nachricht von einem Buffer-Server gerelayed wurde.
    - type: BROADCAST/DIRECTED - Identifizierer des Nächsten Levels des Protokolls.
        - *Directed Pakete* sind Pakete die für einen speziefischen Empfänger gedacht sind.
        - *Broadcast Pakete* sind Pakete die für jede einzelnde Person im Netzwerk gedacht sind
    - (bei Directed nachrichten) receiver: *Public Key* - Der Public key des gedachten Empfängers
    - inner: *Json Objekt* - das innere Paket für MEHR ABSTRAKTION JAAAAA

- Level 1 (BROADCAST, im inner Objekt)
    - type: EXISTS/WANTS/WANTSNAME - Die Art der Broadcast Nachricht
        - Exists - Ein client broadcasted seinen public key und display name zu dem Gesamten Netzwerk:
            - public_key: *Public Key* - Der public key der Person
            - display_name: *String* - Der bevorzuge Name der Person (Jeder kann jeden Namen haben, bei Kollision public key überprüfen)
            - sig: *Signature* - Signiert den *display_name*
        - Wants - Ein client will, dass ein Broadcast server die letzten *Directed* Nachrichten an einen bestimmten public key relayed.
            - public_key: *Public Key* - Der public key dessen Nachrichten relayed werden soll
            - *todo* Queue leeren mit cryptographischen signaturen das eine Nachricht bekommen und verarbeitet wurde.
        - Wantsname - Ein client sucht nach einem nutzer mit bestimmten Namen und will broadcast messages von dem buffer server gerelayed bekommen
            - name: *String* - die namen query

- Level 1 (DIRECTED, im inner Objekt)
    - type: HEAL/MESSAGE - Die art der Directed Nachricht
        - Heal - Heilungsprozess
            - new_key: *Public Key* - The new key used for the healing process
            - sig: *Signature* - Signature, signed with the public key of the other partie
            - sender: *Public Key* - The global public key of the sender
        - Message - Sends a message, encrypted with the current rolling key
            - data: *Encrypted JSON*
            - hash: *Hash* - ein hash der entschlüsselten nachricht, um zu überprüfen, ob der schlüssel valid ist.
            - sender: *Public Key* - The global public key of the sender



### Typen
Verschieden Typen die in der JSON Datei verwendet werden
- *Public Key* - Ein Elliptic Curve 256 Public key, der als Base64 encodierter String encodiert wird.
- *Signature* - Eine digitale Unterschrift
- *Encrypted JSON* - Ein JSON objekt, dass Verschlüsselt wurde und also Base64 String encodiert wird.
- *Hash* - Ein base64 encoded sha256 hash