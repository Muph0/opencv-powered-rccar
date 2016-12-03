
#include <Servo.h>

Servo servo;
Servo motor;

volatile long last_rps_update = 0, last_delta = 1, number_o_cycles = 0, desired_cycles = 0;
volatile double RPS = 0;
volatile bool stuck = false;

long last_writed = 0, last_received = 0;
bool busy = false;

void setup() 
{
  servo.attach(9);
  motor.attach(5);

  attachInterrupt(digitalPinToInterrupt(3), interrupt_3, CHANGE);

  Serial.begin(115200);
}

double X = 0, Y = 0;

double start_y_fwd = 0.4, start_y_bwd = -0.4;
double speed_limit = 1;

void setServo(double value)
{
  // clamp value to (-1, 1)
  value = constrain(value, -1.0, 1.0);

  // calculate servo degrees
  int degrees = 102 + int(value * 33);

  // tell servo library to send pulses corresponding to given angle
  servo.write(degrees);
}

void setMotor(double value)
{
  // clamp value to (-1, 1)
  value = constrain(value, -1.0, 1.0);

  // skip the deadzone, which is 100us
  int deadzone = 0 * (value > 0 ? 80 : (value < 0 ? -120 : 0));

  // calculate the length of the pulse
  int micros = 1500 + int(deadzone + value * 150);

  // tell servo library to send pulses of given length
  motor.writeMicroseconds(micros);
}

void interrupt_3()
{
  long delta_t = micros() - last_rps_update;
  last_rps_update = micros();
  
  if (delta_t > 20100 && delta_t != 20000 && last_delta != 20000)
  {
    number_o_cycles++;
    if (abs(desired_cycles) > 0)
    {
      int sign = abs(desired_cycles)/desired_cycles;
      desired_cycles -= sign;
    }
    
    double new_rps = 1000000.0 / (delta_t * 4);
  
    double change = abs(new_rps - RPS);
    double value = 1.0 / (pow(change*0.8, 2) + 1);
  
    RPS = new_rps*value + RPS*(1-value);
  }
  else stuck = true;
  last_delta = delta_t;
}

void loop()
{
  while (Serial.available() > 0)
  {
    int first_byte = Serial.read();
    last_received = millis();

    if (first_byte == 'X')
    {
      // set the steering right away
      int x = Serial.parseInt();   
      X = x / 100.0;   
    }

    if (first_byte == 'C')
    {
      // set the cycles
      int c = Serial.parseInt();
      // motor is kinda accurate for small numbers,
      // but for c > 10, it overshoots with 5 to 20 cycles
      // since the speed is constant, i'm going to
      // gradually decrease c by 13
      if (c > 0)
        c = int(1 + c - 13.0 / (pow(2, 4-0.3*c) + 1));
      desired_cycles = c;
    }

    if (first_byte == 'S')
    {
      // update speed limit
      speed_limit = Serial.parseFloat();
    }
  }

  setServo(X);

  if (abs(desired_cycles) > 0)
  {
    busy = true;
    double step_y = 0.0001;
    
    if (desired_cycles > 0)
    {
      if (Y < 0.01) 
        Y = start_y_fwd;
      else if (abs(RPS) < speed_limit && abs(Y) < .85)
      {
        Y += step_y;
        start_y_fwd = Y *0.8;
      }
    }
    else
    {
      if (Y > -0.01) 
        Y = start_y_bwd;
      else if (abs(RPS) < speed_limit && abs(Y) < .85)
      {
        Y -= step_y;
        start_y_bwd = Y *0.8;
      }
    }
  }
  else
  {
    Y = 0;
    busy = false;
  }

  if (stuck || (desired_cycles == 0 && int(RPS * 100 + 0.1) == 1250))
  {
    Y = .8;
    stuck = false;
  }
  
  setMotor(Y);

  
  
  
  double potentially_new_rps = 1000000.0 / (micros() - last_rps_update) / 4.0;
  if (abs(potentially_new_rps) < abs(RPS) && micros() - last_rps_update > 5000)
  {
    if (micros() - last_rps_update > last_delta)
    {
      RPS = potentially_new_rps;
    }
  }

  if (millis() >= last_writed + 20)
  {
    last_writed = millis();

    if (busy)
    {
      Serial.println("busy");
    }
    else
    {
      Serial.println("free");
    }
  }
}









