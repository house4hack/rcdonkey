
#include <Servo.h> 
#define THROTTLE 7
#define TURN 8
#define MODE 9

#define THROTTLE_SERVO 3
#define TURN_SERVO 5
#define MODE_SERVO 6

#define THROTTLE_BUT 14
#define TURN_BUT 15

#define THROTTLE_LED 16
#define TURN_LED 17

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



Servo myservo_throttle, myservo_turn, myservo_mode; 
char throttle_passthru = 1;
char turn_passthru = 1;


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
  
  pinMode(THROTTLE_BUT, INPUT);
  digitalWrite(THROTTLE_BUT, HIGH);
  pinMode(TURN_BUT, INPUT);
  digitalWrite(TURN_BUT, HIGH);  
  
  pinMode(THROTTLE_LED, OUTPUT);
  pinMode(TURN_LED, OUTPUT);
  

  myservo_throttle.attach(THROTTLE_SERVO);
  myservo_turn.attach(TURN_SERVO);
  myservo_mode.attach(MODE_SERVO);
  
  Serial.setTimeout(1000);
  Serial.begin(115200);
}
 
 
void display(){
  digitalWrite(THROTTLE_LED,throttle_passthru); 
  digitalWrite(TURN_LED,turn_passthru);  
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
void loop() {
  
 
  readFromPWM();
  readSerialData();

  myservo_throttle.writeMicroseconds(pwm_value_throttle);
  myservo_turn.writeMicroseconds(pwm_value_turn); 
  myservo_mode.writeMicroseconds(pwm_value_mode);  

  
  Serial.print(pwm_value_throttle);
  Serial.print(",");
  Serial.print(pwm_value_turn);
  Serial.print(",");
  Serial.println(pwm_value_mode); 
 
  if(!digitalRead(TURN_BUT)){
     turn_passthru = !turn_passthru;
     display();
     delay(500);
  }

  if(!digitalRead(THROTTLE_BUT)){
     throttle_passthru = !throttle_passthru;
     display();
     delay(500);
  } 
  display(); 
  
}

