#include <TimerOne.h>

#define PHR A1
#define LED_RELAY 12

#define TEMP A0
#define HEATING_RELAY 10
#define COOLING_RELAY 11
#define MOTION_BUTTON 8

boolean autoLightMode, takeTemperature, secureMode, motionDetected,autoTemperature, measuringLight, measuringMotions;
int pauseCounter, seconds, motions, numberOfMotions, movementDetected, holdingTheButton, autoLightModeDuration, secureModeDuration, temperaturePause, illuminationPause, securityTimer;

void autoLight(float illumination){
  if(illumination<306){
      digitalWrite(LED_RELAY, HIGH);
    }
  else{
      digitalWrite(LED_RELAY, LOW);
    }
  }

void smartHome(){
  if(autoLightMode){
    autoLightModeDuration++;
    }

  if(measuringMotions){
    secureModeDuration;
  }
  
  if(measuringLight){
    float illumination = analogRead(A1);
    Serial.print("illu-");
    Serial.println(illumination);
    if(autoLightMode){
      autoLight(illumination);
    }
    measuringLight = false;
    }
  
  if(takeTemperature){
    float temperature = analogRead(A0);
    Serial.print("temp-");
    Serial.println(temperature);
    if(temperature>=59 && autoTemperature){
      digitalWrite(COOLING_RELAY, HIGH);
      digitalWrite(HEATING_RELAY, LOW);
      }
    if(temperature<=55 && autoTemperature){
      digitalWrite(HEATING_RELAY, HIGH);
      digitalWrite(COOLING_RELAY, LOW);
    }
      takeTemperature=false;
    }

  if(secureMode){
    secureModeDuration++;
    if(motionDetected){
      securityTimer++;
      if(securityTimer>=10){
        digitalWrite(LED_RELAY, LOW);
        numberOfMotions++;
        motionDetected = false;
        Serial.println("noti-move");
      }
    }
  }

     pauseCounter++;
     if(pauseCounter == 10){
      takeTemperature = true;
//     }
//     else if(pauseCounter == 22){
      Serial.print("dalm-");
      Serial.println(autoLightModeDuration);
//     }else if(pauseCounter == 35){
      Serial.print("dsec-");
      Serial.println(secureModeDuration);
//     }
//      else if(pauseCounter == 48){
      measuringLight = true;
//     }else if(pauseCounter == 60){
      pauseCounter = 0;
      Serial.print("movn-");
      Serial.println(numberOfMotions);
      }
      
}


void setup() {
 Serial.begin(9600);
 pinMode(12, OUTPUT);
 pinMode(11, OUTPUT);
 pinMode(10, OUTPUT);
 pinMode(8, INPUT);
 autoLightMode = false;
 secureMode = true;
 takeTemperature = false;
 measuringLight= false;
 measuringMotions = true;
 autoTemperature = true;
 illuminationPause = 0;
 temperaturePause = 0;
 pauseCounter = 0;
 seconds = 10;
 numberOfMotions = 0;
 autoLightModeDuration = 0;
 secureModeDuration = 0;
 Timer1.initialize(1000000);
 Timer1.attachInterrupt(smartHome);
}

void loop() {
    if(digitalRead(8)==1 && secureMode){
      motionDetected = true;
      securityTimer = 0;
      digitalWrite(LED_RELAY, HIGH);
    }
    if(Serial.available() > 0) {
    String msg = Serial.readString();
    if(msg=="light_on\n" || msg=="light_on") {
      Serial.println("LON");
      digitalWrite(LED_RELAY, HIGH);
      autoLightMode = false;
   } else if(msg=="light_off\n" || msg=="light_off") {
      Serial.println("LOFF");
      digitalWrite(LED_RELAY, LOW);
      autoLightMode = false;
    }else if(msg=="auto light mode\n" || msg=="auto light mode") {
      Serial.println("AUTOLIGHT");
      //autoLight();
      autoLightMode = true;
      secureMode=false;
    }
    else if(msg=="cooling_on\n" || msg=="cooling_on") {
      Serial.println("COOLING_IS_ON");
      digitalWrite(COOLING_RELAY, HIGH);
      autoTemperature = false;
   } else if(msg=="cooling_off\n" || msg=="cooling_off") {
      Serial.println("COOLING_IS_OFF");
      digitalWrite(COOLING_RELAY, LOW);
      autoTemperature = false;
    } else if(msg=="heating_on\n" || msg=="heating_on") {
      Serial.println("HEATING_IS_ON");
      digitalWrite(HEATING_RELAY, HIGH);
      autoTemperature = false;
   } else if(msg=="heating_off\n" || msg=="heating_off") {
      Serial.println("HEATING_IS_OFF");
      digitalWrite(HEATING_RELAY, LOW);
      autoTemperature = false;
    }else if(msg=="auto temperature mode\n" || msg=="auto temperature mode") {
      Serial.println("AUTOTEMPERATURE");
      autoTemperature = true;
    }
    else if(msg == "SECURE_MODE\n" || msg=="SECURE_MODE") {
      autoLightMode = false;
      secureMode = true;
      Serial.print("secureMode on");
    } else if(msg == "SECURE_MODE_OFF\n" || msg=="SECURE_MODE_OFF") {
      secureMode = false;
      Serial.print("secureMode off");}
    else{
          digitalWrite(LED_RELAY, LOW);
          }
      }
}
