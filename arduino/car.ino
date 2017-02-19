#include <AccelStepper.h>

AccelStepper stepper1(AccelStepper::FULL2WIRE, 5, 4);
AccelStepper stepper2(AccelStepper::FULL2WIRE, 9, 8);

const int PIN_SONAR = A0;
const int READS_SONAR=10;
const int SONAR_READ_PERIOD_MS=20;

unsigned long lastSonarReadTime=0;
int nbReadsSonar=0;
int sonarValue=0;

bool stepper1Stop=true;
bool stepper2Moving=false;

void setup()
{  
    Serial.begin(9600);
  
    pinMode(PIN_SONAR, INPUT);
  
    stepper1.setEnablePin(12);
    stepper2.setEnablePin(13);
    
    stepper2.setMaxSpeed(1500.0);

    stepper1.setAcceleration(4000.0);
    stepper2.setAcceleration(4000.0);

    stepper1.disableOutputs();
    stepper2.disableOutputs();

}

void move(int speed) {
    long dir=100000;
    if(speed<0) {
      dir=-100000;
      speed=-speed;
    }
    if(speed>30)
      speed=30;
    stepper1.enableOutputs();
    stepper1.setMaxSpeed((float)speed * 100.0);          
    stepper1.moveTo(stepper1.currentPosition() - dir);
    stepper1Stop=false;
}

void loop()
{
        
    if (Serial.available()>1)  { //command byte and parameter byte available
        char command = Serial.read();
        int p1=Serial.read();//read data param
    
        if (command == 'R'){//turn right
          stepper2.enableOutputs();
          stepper2.moveTo(-100);
          stepper2Moving=true;
        }
        else if (command == 'L'){//turn left
          stepper2.enableOutputs();
          stepper2.moveTo(100);
          stepper2Moving=true;
        }
        else if (command == 'S'){//go straight
          stepper2.enableOutputs();
          stepper2.moveTo(0);
          stepper2Moving=true;
        }
        else if (command == 'F'){//move forward
          move(p1);
        }
        else if (command == 'B'){//move backward
          move(-p1);
        }
        else if (command == 'H'){//stop
          stepper1Stop=true;
          stepper1.setMaxSpeed(0.0);
        }
        
    }

    if(stepper1Stop && stepper1.speed() <= 10.0) {
          stepper1.moveTo(0);
          stepper1.disableOutputs();
          stepper1Stop=false;
    }
    
    if(stepper2Moving && stepper2.distanceToGo() == 0.0) {
          stepper2.disableOutputs();
          stepper2Moving=false;
    }

    stepper1.run();
    stepper2.run();
    
    if(millis() - lastSonarReadTime >= SONAR_READ_PERIOD_MS) {
      sonarValue += analogRead(PIN_SONAR)/2;
      nbReadsSonar ++;
      lastSonarReadTime = millis();

      if(nbReadsSonar >= READS_SONAR) {
        Serial.println(sonarValue * 2.54 / READS_SONAR);
        sonarValue=0;
        nbReadsSonar=0;
      }
    }

}
