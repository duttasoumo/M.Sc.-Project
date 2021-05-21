#include <dht.h>

dht DHT;

#define DHT11_PIN 8
#define LDR_PIN 5
#define MQ2_PIN 3
#define SM_PIN 4
void setup(){
  Serial.begin(9600);
}



void loop()
{
  DHT.read11(DHT11_PIN);
  Serial.print(DHT.temperature);
  Serial.print(",");
  Serial.print(DHT.humidity);
  Serial.print(",");
  Serial.print(100-analogRead(LDR_PIN)/10.24);
  Serial.print(",");
  Serial.print(analogRead(MQ2_PIN)/10.24);
  Serial.print(",");
  Serial.print(100-analogRead(SM_PIN)/10.24);
  Serial.println();
  delay(1000);

}
