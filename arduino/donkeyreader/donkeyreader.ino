
#include <Servo.h> 
#define THROTTLE 7
#define TURN 8
#define MODE 9

#define THROTTLE_SERVO 3
#define TURN_SERVO 5
#define MODE_SERVO 6

#define DRIVE_BUT 14
#define RECORD_BUT 15

#define DRIVE_LED 16
#define RECORD_LED 17

#define DEFAULT_ANGLE 1500
#define DEFAULT_THROTTLE 1500
#define DEFAULT_MODE 1000


#define CONTROL_SIZE 4
struct controlItem {
    int angle;              // 2
    int throttle;           // 2
};

union inputFromPC {
   controlItem controlData;
   byte pcLine[CONTROL_SIZE];
};

inputFromPC inputData;
byte pcData[CONTROL_SIZE];

#define EMPTY_DATA 1
#define MARKER1_DATA 2
#define MARKER2_DATA 3
#define RECV_DATA 4
#define NEW_DATA 5

char receiveState = EMPTY_DATA;
byte startMarker1 = 'A';
byte startMarker2 = 'A';
char recvIndex = 0;


#define RECORD_ON 1
#define RECORD_OFF 0
#define DRIVE_MANUAL 0
#define DRIVE_ANGLE 1
#define DRIVE_AUTO 2

int record_mode= RECORD_OFF;
int drive_mode= DRIVE_MANUAL;
long last_blink=0;
char blink_on=0;

char throttle_passthru=true, turn_passthru=true;

Servo myservo_throttle, myservo_turn, myservo_mode; 


#include <RunningMedian.h>

RunningMedian throttle_samples = RunningMedian(3);
RunningMedian turn_samples = RunningMedian(3);
 


int pwm_value_throttle=DEFAULT_THROTTLE, pwm_value_turn=DEFAULT_ANGLE, pwm_value_mode=DEFAULT_MODE;
void setup() {
  // put your setup code here, to run once:
  pinMode(THROTTLE, INPUT);
  pinMode(TURN, INPUT);
  pinMode(MODE, INPUT); 
 
  pinMode(THROTTLE_SERVO, OUTPUT);
  pinMode(TURN_SERVO, OUTPUT);
  pinMode(MODE_SERVO, OUTPUT);
  
  pinMode(RECORD_BUT, INPUT);
  digitalWrite(RECORD_BUT, HIGH);
  pinMode(DRIVE_BUT, INPUT);
  digitalWrite(DRIVE_BUT, HIGH);  
  
  pinMode(RECORD_LED, OUTPUT);
  pinMode(DRIVE_LED, OUTPUT);
  

  myservo_throttle.attach(THROTTLE_SERVO);
  myservo_turn.attach(TURN_SERVO);
  myservo_mode.attach(MODE_SERVO);
  
  Serial.setTimeout(1000);
  Serial.begin(115200);
}
 
 
void display(){
  if(record_mode==RECORD_OFF){
    digitalWrite(RECORD_LED, LOW);
  } else if( record_mode == RECORD_ON){
    digitalWrite(RECORD_LED, HIGH);
  }
  
  if(drive_mode==DRIVE_MANUAL){
    digitalWrite(DRIVE_LED,LOW);
  } else if (drive_mode==DRIVE_ANGLE){
    digitalWrite(DRIVE_LED, HIGH); 
  } else if (drive_mode==DRIVE_AUTO){
    if(millis() - last_blink>100){
      blink_on = !blink_on;
      last_blink = millis();
    }
    digitalWrite(DRIVE_LED, blink_on);
  
  }
}




void readSerialData() {   
    byte rb;
   
    if(receiveState == NEW_DATA){
       return; 
    }
    
    if(receiveState == EMPTY_DATA){
       recvIndex = 0;
       if(Serial.available()){
          rb = Serial.read();
          if(rb == startMarker1){
             receiveState == MARKER1_DATA; 
          }
       } 
    }

    if(receiveState == MARKER1_DATA){
       if(Serial.available()){
          rb = Serial.read();
          if(rb == startMarker2){
             receiveState == RECV_DATA;
 
          } else {
             receiveState = EMPTY_DATA; 
          }
       } 
    }

    if(receiveState == RECV_DATA){
       while(Serial.available()){
          rb = Serial.read();
          inputData.pcLine[recvIndex] = rb;
          recvIndex++;
          if(recvIndex == CONTROL_SIZE){
             processSerialData();
             receiveState = EMPTY_DATA;  
          }
       } 
    }
    
}


void processSerialData() {
  if(receiveState == NEW_DATA){
     for (byte n = 0; n < CONTROL_SIZE; n++) {
       inputData.pcLine[n] = pcData[n];
     }

     pwm_value_throttle = inputData.controlData.throttle;
     pwm_value_turn     = inputData.controlData.angle;
     receiveState = EMPTY_DATA;
  }   
} 
 
void readFromPWM(){
   if(throttle_passthru){
    pwm_value_throttle = pulseIn(THROTTLE, HIGH);
    if(pwm_value_throttle < 500){
       pwm_value_throttle = DEFAULT_THROTTLE;
    }
    throttle_samples.add(pwm_value_throttle);
    pwm_value_throttle = throttle_samples.getMedian();   
  } 

  if(turn_passthru){  
    pwm_value_turn = pulseIn(TURN, HIGH);
    if(pwm_value_turn < 500){
       pwm_value_turn = DEFAULT_ANGLE;
    }

    turn_samples.add(pwm_value_turn);  
    pwm_value_turn = turn_samples.getMedian();
     
  } 
  pwm_value_mode = pulseIn(MODE, HIGH);
} 

void readButtons(){
  if(!digitalRead(DRIVE_BUT)){
     if(drive_mode == DRIVE_MANUAL){
       drive_mode = DRIVE_ANGLE;
       turn_passthru = false;
       throttle_passthru = true;
     } else if (drive_mode == DRIVE_ANGLE) {
       drive_mode = DRIVE_AUTO;
       turn_passthru = false;
       throttle_passthru = false;

     } else if (drive_mode = DRIVE_AUTO){
       drive_mode = DRIVE_MANUAL;
       turn_passthru = true;
       throttle_passthru = true;
     } else {
       drive_mode = DRIVE_MANUAL;
       turn_passthru = true;
       throttle_passthru = true;
     }
     display();
     delay(500);
  }

  if(!digitalRead(RECORD_BUT)){
     if(record_mode == RECORD_OFF){
        record_mode = RECORD_ON; 
     } else if(record_mode== RECORD_ON){
        record_mode = RECORD_OFF;
     } else {
        record_mode= RECORD_OFF;
     }
     display();
     delay(500);
  } 
  
}


void loop() {
  
 
  readFromPWM();
  readSerialData();
  readButtons();

  myservo_throttle.writeMicroseconds(pwm_value_throttle);
  myservo_turn.writeMicroseconds(pwm_value_turn); 
  myservo_mode.writeMicroseconds(pwm_value_mode);  

  
  Serial.print(pwm_value_throttle);
  Serial.print(",");
  Serial.print(pwm_value_turn);
  Serial.print(",");
  Serial.print(drive_mode);
  Serial.print(",");
  Serial.println(record_mode);
  
 
  display(); 
  
}

