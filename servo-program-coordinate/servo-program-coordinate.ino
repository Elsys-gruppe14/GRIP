/*

    DENNE KODEN ER IKKE FERDIG OG FUNGERER IKKE I SIN NÅVÆRENDE TILSTAND

*/




// PRE-PROCESSOR COMMANDS
//////////////////////////////////////////////////////////////////////

#include <Servo.h>
#include <EEPROM.h>

// Definerer IO-pinner på arduino
#define for_pin 10
#define hei_pin 9
#define start_pin 7
#define stop_pin 8
#define x_pin A1
// define y_pin A0
#define red_pin 6
#define green_pin 11
#define blue_pin 12

// Definerer konstanter som brukes i koden
#define STEP_TIME 10
#define HEIGHT_ANGLE 40
#define BLINK_DELAY 2000
#define BLINK_DUR 500


// VARIABLES
//////////////////////////////////////////////////////////////////////

Servo for_servo, hei_servo;
bool printing, print_start, print_stop;
uint16_t x_pos;
uint8_t for_angle;
uint32_t blink_time;
float arm_length;


// SETUP FUNCTION
//////////////////////////////////////////////////////////////////////

  void setup() {

    Serial.begin(9600);
    
    // Leser av verdier fra minnet
    printing = EEPROM.read(3);
    print_start = EEPROM.read(4);
    print_stop = EEPROM.read(5);

    // I tilfelle systemet blir skrudd av under en print
    // Setter servoene tilbake til vinkelen de sto i
    if (printing) {
      for_angle = EEPROM.read(0);
      for_servo.write(for_angle);
      hei_servo.write(HEIGHT_ANGLE);
    }
    else {
      for_servo.write(180);
      hei_servo.write(0);
    }
    
    for_servo.attach(for_pin);
    hei_servo.attach(hei_pin);

    pinMode(start_pin, INPUT_PULLUP);
    pinMode(stop_pin, INPUT_PULLUP);

}


// LOOP FUNCTION
//////////////////////////////////////////////////////////////////////

void loop() {

  delay(50);

  // Sjekker startknappen
  if (!digitalRead(start_pin)) {
    print_start = 1;
    EEPROM.write(4, print_start);
  }

  // Initialiserer, og setter status til "printing"
  if (print_start && !printing){
     initialize();
     printing = 1;
     EEPROM.write(3, printing);
     print_start = 0;
     EEPROM.write(4, print_start);
     blink_time = millis();
  }

  while(printing) {

    // Blinker LED-lyset mens printen pågår
    if (millis() - blink_time > BLINK_DELAY) {
      blink_time = millis();
      Serial.println("Printing...");
      while(millis() - blink_time < BLINK_DUR) {
        RGB_led(255,0,255);
      }
      blink_time = millis();
      RGB_led(255,255,255);
    }

    // Sjekker stoppknappen
    if (!digitalRead(stop_pin)) {
      print_stop = 1;
      EEPROM.write(5, print_stop);
    }

    // Resetter armen
    if (print_stop){
      reset();
      printing = 0;
      EEPROM.write(3, printing);
      print_stop = 0;
      EEPROM.write(5, print_stop);
    }
  }
  Serial.print(printing);
  Serial.print(print_start);
  Serial.print(print_stop);
  Serial.println();
  
}


// INITIALIZE FUNCTION
//////////////////////////////////////////////////////////////////////

void initialize() {

  Serial.println("Initializing");
  delay(1000);
  arm_length = 0;

  // Leser distansen fra PC/Rasperry Pi
  while(Serial.available() > 0 || arm_length == 0) {
    arm_length = Serial.parseFloat();
    Serial.println(arm_length);
  }
  
  // Regner ut servovinkel og beveger armen
  for_angle = 180 - int((45*(arm_length-43)/(4*PI)));
  Serial.println(for_angle);
  for (uint8_t angle = EEPROM.read(0); angle > for_angle; angle--) {
    hei_servo.write(angle);
    delay(10*STEP_TIME);
  }
  
  // Senker armen
  for (uint8_t angle = 0; angle < HEIGHT_ANGLE; angle++) {
    hei_servo.write(angle);
    delay(10*STEP_TIME);
  }
  EEPROM.write(0, for_angle);
}


// RESET FUNCTION
//////////////////////////////////////////////////////////////////////

void reset() {

  Serial.println("Resetting");

  // Setter servoene tilbake til startposisjon
  for (uint8_t angle = hei_servo.read(); angle > 0; angle--) {
    hei_servo.write(angle);
    delay(10*STEP_TIME);
  }
  
  for (uint8_t angle = for_servo.read(); angle < 180; angle++) {
    for_servo.write(angle);
    delay(STEP_TIME);
  }
  EEPROM.write(0, 180);
}


// RGB FUNCTION
//////////////////////////////////////////////////////////////////////

void RGB_led(uint8_t red, uint8_t green, uint8_t blue) {
  
  analogWrite(red_pin, red);
  analogWrite(green_pin, green);
  analogWrite(blue_pin, blue);
}
