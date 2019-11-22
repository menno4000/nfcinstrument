#include <SPI.h> // SPI-Bibiothek hinzufügen

#include <MFRC522.h> // RFID-Bibiothek hinzufügen

#define SS_PIN 10 // SDA an Pin 10 (bei MEGA anders)

#define RST_PIN 9 // RST an Pin 9 (bei MEGA anders)

#include <SoftwareSerial.h>

SoftwareSerial hc_05(7, 8);

MFRC522 mfrc522(SS_PIN, RST_PIN); // RFID-Empfänger benennen



void setup() // Beginn des Setups:

{

Serial.begin(9600); // Serielle Verbindung starten (Monitor)

SPI.begin(); // SPI-Verbindung aufbauen

mfrc522.PCD_Init(); // Initialisierung des RFID-Empfängers

hc_05.begin(9600);

}



void loop() // Hier beginnt der Loop-Teil

{
  

  if ( ! mfrc522.PICC_IsNewCardPresent()) // Wenn keine Karte in Reichweite ist...
  
  {
  
  return; // ...springt das Programm zurück vor die if-Schleife, womit sich die Abfrage wiederholt.
  
  }
  
  
  
  if ( ! mfrc522.PICC_ReadCardSerial()) // Wenn kein RFID-Sender ausgewählt wurde
  
  {
  
  return; // ...springt das Programm zurück vor die if-Schleife, womit sich die Abfrage wiederholt.
  }
  
  
  
  Serial.print("Die ID des RFID-TAGS lautet:"); // "Die ID des RFID-TAGS lautet:" wird auf den Serial Monitor geschrieben.
  
  
  
  for (byte i = 0; i < mfrc522.uid.size; i++)
  
  {
  
  //Serial.print(mfrc522.uid.uidByte[i], HEX); // Dann wird die UID ausgelesen, die aus vier einzelnen Blöcken besteht und der Reihe nach an den Serial Monitor gesendet. Die Endung Hex bedeutet, dass die vier Blöcke der UID als HEX-Zahl (also auch mit Buchstaben) ausgegeben wird
  
  //Serial.print(" "); // Der Befehl „Serial.print(" ");“ sorgt dafür, dass zwischen den einzelnen ausgelesenen Blöcken ein Leerzeichen steht.
  
  byte buffer[18];
  MFRC522::StatusCode status;

  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  
  mfrc522.PICC_DumpDetailsToSerial(&(mfrc522.uid));

  Serial.println(); // Mit dieser Zeile wird auf dem Serial Monitor nur ein Zeilenumbruch gemacht.
  
  dump_byte_array(buffer, 18); Serial.println();
  }
  
  
    
}

/**
 * Helper routine to dump a byte array as hex values to Serial.
 */
void dump_byte_array(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);

        //hc_05.print("Message: lool");
        hc_05.print(buffer[i], HEX);
    }
}
