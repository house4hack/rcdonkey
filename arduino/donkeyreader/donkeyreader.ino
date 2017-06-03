
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

//int incoming[2];


Servo myservo_throttle, myservo_turn, myservo_mode; 
char throttle_passthru = 1;
char turn_passthru = 1;

int incoming[2];

#include <RunningMedian.h>

RunningMedian throttle_samples = RunningMedian(3);
RunningMedian turn_samples = RunningMedian(3);
 


int pwm_value_throttle=1500, pwm_value_turn=1500, pwm_value_mode=1000;
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
  
  
  Serial.begin(115200);
}
 
 
void display(){
  digitalWrite(THROTTLE_LED,throttle_passthru); 
  digitalWrite(TURN_LED,turn_passthru);  
}

unsigned char waitForKey(int timeout){
  long start = millis();
  while(!Serial.available()){
     if(millis()-start>timeout){
       return(0);
     } 
  }
  unsigned char c= Serial.read();
  Serial.println(c,DEC);
  return(c);
}

void readFromSerial(){
    char found = 0;
    if(Serial.available()){
      char magic1= waitForKey(1000);
      if(magic1=='A'){
        char magic2 = waitForKey(1000);
        if(magic2=='A'){
           incoming[0] = waitForKey(1000);
           incoming[1] = waitForKey(1000);
           found = 1;         
        }
      }
    }
    if(found){  
      if(!throttle_passthru){ 
         pwm_value_throttle = ((float)incoming[0])/256.0*1000.0+1000.0;
 
      }   
      if(!turn_passthru){
         pwm_value_turn = ((float)incoming[1])/256.0*1000.0+1000.0;
      } 
    }      
}
 
 
void readFromPWM(){
   if(throttle_passthru){
    pwm_value_throttle = pulseIn(THROTTLE, HIGH);
    throttle_samples.add(pwm_value_throttle);
    pwm_value_throttle = throttle_samples.getMedian();   
  } 

  if(turn_passthru){  
    pwm_value_turn = pulseIn(TURN, HIGH);
    turn_samples.add(pwm_value_turn);  
    pwm_value_turn = turn_samples.getMedian();
     
  } 
  pwm_value_mode = pulseIn(MODE, HIGH);
} 
void loop() {
  
 
  readFromPWM();

  readFromSerial();

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

