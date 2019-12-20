#include <SPI.h> // SPI-Bibiothek hinzufügen

#include <MFRC522.h> // RFID-Bibiothek hinzufügen

#define SS_PIN 10 // SDA an Pin 10 

#define RST_PIN 9 // RST an Pin 9 

#include <SoftwareSerial.h>

SoftwareSerial hc_05(7, 8); // Bluetooth modul an Pins 7 und 8

MFRC522 mfrc522(SS_PIN, RST_PIN); // RFID-Empfänger benennen
MFRC522::MIFARE_Key key; // create a MIFARE_Key struct named 'key', which will hold the card information


//int period = 100; //Verzoegerung zwischen Bluetooth-Signalen

unsigned long time_now = 0;

void setup() // Beginn des Setups:
{

  Serial.begin(9600); // Serielle Verbindung starten (Monitor)

  SPI.begin(); // SPI-Verbindung aufbauen

  mfrc522.PCD_Init(); // Initialisierung des RFID-Empfängers

  hc_05.begin(9600);
}

int blocknr=1;  //nr of block on card we are trying to interact with
byte blockcontent[16] = {"d2____________"};//an array with 16 bytes to be written into one of the 64 card blocks is defined

byte readbackblock[18]; // Buffer fuer auslesen von NFC tags

void loop() // Hier beginnt der Loop-Teil
{
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;


  if ( ! mfrc522.PICC_IsNewCardPresent()) // Wenn keine Karte in Reichweite ist...
    return; // ...springt das Programm zurück vor die if-Schleife, womit sich die Abfrage wiederholt.



  if ( ! mfrc522.PICC_ReadCardSerial()) {// Wenn kein RFID-Sender ausgewählt wurde
    return; // ...springt das Programm zurück vor die if-Schleife, womit sich die Abfrage wiederholt.
  }
  Serial.println("card detected.");

//  Serial.println("write block 1");
//  writeBlock(blocknr, blockcontent);

  Serial.println("read block: ");
  readBlock(1, readbackblock); //ersten record der rfid karte einlesen

  String note = "";
  for (int j = 0 ; j < 2 ; j++) //print the block contents
  {
    note = note + (char)readbackblock[j];
  }
  Serial.print("note: ");
  Serial.print(note);

  String noteStubMessage = note + "0000";
  
//  //mfrc522.PICC_DumpToSerial(&(mfrc522.uid));

  hc_05.print(noteStubMessage);

  Serial.println(""); // Mit dieser Zeile wird auf dem Serial Monitor nur ein Zeilenumbruch gemacht.

  mfrc522.PCD_StopCrypto1(); //RFID tag fuer neue kommunikation resetten
}


int readBlock(int blockNumber, byte arrayAddress[]) 
{
  int largestModulo4Number=blockNumber/4*4;
  int trailerBlock=largestModulo4Number+3;//determine trailer block for the sector

  /*****************************************authentication of the desired block for access***********************************************************/
  byte status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_B, trailerBlock, &key, &(mfrc522.uid));
  //byte PCD_Authenticate(byte command, byte blockAddr, MIFARE_Key *key, Uid *uid);
  //this method is used to authenticate a certain block for writing or reading
  //command: See enumerations above -> PICC_CMD_MF_AUTH_KEY_A  = 0x60 (=1100000),    // this command performs authentication with Key A
  //blockAddr is the number of the block from 0 to 15.
  //MIFARE_Key *key is a pointer to the MIFARE_Key struct defined above, this struct needs to be defined for each block. New cards have all A/B= FF FF FF FF FF FF
  //Uid *uid is a pointer to the UID struct that contains the user ID of the card.
  if (status != MFRC522::STATUS_OK) {
         Serial.print("PCD_Authenticate() failed (read): ");
         return 3;//return "3" as error message
  }
  //it appears the authentication needs to be made before every block read/write within a specific sector.
  //If a different sector is being authenticated access to the previous one is lost.


  /*****************************************reading a block***********************************************************/
        
  byte buffersize = 18;//we need to define a variable with the read buffer size, since the MIFARE_Read method below needs a pointer to the variable that contains the size... 
  status = mfrc522.MIFARE_Read(blockNumber, arrayAddress, &buffersize);//&buffersize is a pointer to the buffersize variable; MIFARE_Read requires a pointer instead of just a number
  if (status != MFRC522::STATUS_OK) {
          Serial.print("MIFARE_read() failed: ");
          return 4;//return "4" as error message
  }
  Serial.println("block was read");
  return 0;
}

       
int writeBlock(int blockNumber, byte arrayAddress[]) 
{
  //this makes sure that we only write into data blocks. Every 4th block is a trailer block for the access/security info.
  int largestModulo4Number=blockNumber/4*4;
  int trailerBlock=largestModulo4Number+3;//determine trailer block for the sector
  if (blockNumber > 2 && (blockNumber+1)%4 == 0){Serial.print(blockNumber);Serial.println(" is a trailer block:");return 2;}//block number is a trailer block (modulo 4); quit and send error code 2
  Serial.print(blockNumber);
  Serial.println(" is a data block:");
  
  /*****************************************authentication of the desired block for access***********************************************************/
  byte status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_B, trailerBlock, &key, &(mfrc522.uid));
  //byte PCD_Authenticate(byte command, byte blockAddr, MIFARE_Key *key, Uid *uid);
  //this method is used to authenticate a certain block for writing or reading
  //command: See enumerations above -> PICC_CMD_MF_AUTH_KEY_A  = 0x60 (=1100000),    // this command performs authentication with Key A
  //blockAddr is the number of the block from 0 to 15.
  //MIFARE_Key *key is a pointer to the MIFARE_Key struct defined above, this struct needs to be defined for each block. New cards have all A/B= FF FF FF FF FF FF
  //Uid *uid is a pointer to the UID struct that contains the user ID of the card.
  if (status != MFRC522::STATUS_OK) {
         Serial.print("PCD_Authenticate() failed: ");
         return 3;//return "3" as error message
  }
  //it appears the authentication needs to be made before every block read/write within a specific sector.
  //If a different sector is being authenticated access to the previous one is lost.


  /*****************************************writing the block***********************************************************/
        
  status = mfrc522.MIFARE_Write(blockNumber, arrayAddress, 16);//valueBlockA is the block number, MIFARE_Write(block number (0-15), byte array containing 16 values, number of bytes in block (=16))
  //status = mfrc522.MIFARE_Write(9, value1Block, 16);
  if (status != MFRC522::STATUS_OK) {
           Serial.print("MIFARE_Write() failed: ");
           return 4;//return "4" as error message
  }
  Serial.println("block was written");
  return 0;
}
