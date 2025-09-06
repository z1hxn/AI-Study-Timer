#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int startBTN = 2;
const int resetBTN = 3;

unsigned long startTime = 0;
unsigned long totalTime = 0;

bool lastStartState = HIGH;
bool lastResetState = HIGH;

enum TimerState { WAITING, RUNNING, PAUSED };
TimerState state = WAITING;
TimerState lastDisplayState = WAITING;  // 직전 출력 상태 기억용

void setup() {
  lcd.init();
  lcd.backlight();
  pinMode(startBTN, INPUT_PULLUP);
  pinMode(resetBTN, INPUT_PULLUP);

  // 첫 출력
  lcd.setCursor(0, 0);
  lcd.print("Waiting");
  lcd.setCursor(0, 1);
  lcd.print("Press to Start");
}

void loop() {
  bool startPressed = digitalRead(startBTN);
  bool resetPressed = digitalRead(resetBTN);

  // 시작/정지 버튼 처리
  if (lastStartState == HIGH && startPressed == LOW) {
    if (state == WAITING || state == PAUSED) {
      startTime = millis();
      state = RUNNING;
    } else if (state == RUNNING) {
      totalTime += millis() - startTime;
      state = PAUSED;
    }
    delay(200);
  }

  // 리셋 버튼 처리 (PAUSED일 때만)
  if (lastResetState == HIGH && resetPressed == LOW) {
    if (state == PAUSED) {
      totalTime = 0;
      state = WAITING;

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Paused");
      lcd.setCursor(0, 1);
      lcd.print("Time Reset");
      delay(700);
    }
    delay(200);
  }

  lastStartState = startPressed;
  lastResetState = resetPressed;

  // 시간 계산
  unsigned long displayTime = (state == RUNNING) ? totalTime + (millis() - startTime) : totalTime;
  unsigned int hours = displayTime / 3600000;
  unsigned int minutes = (displayTime % 3600000) / 60000;
  unsigned int seconds = (displayTime % 60000) / 1000;

  // 상태 변경이 있을 때만 LCD 갱신
  if (state != lastDisplayState) {
    lcd.clear();
    if (state == WAITING) {
      lcd.setCursor(0, 0);
      lcd.print("Waiting");
      lcd.setCursor(0, 1);
      lcd.print("Press to Start");
    } else if (state == RUNNING) {
      lcd.setCursor(0, 0);
      lcd.print("Studying");
    } else if (state == PAUSED) {
      lcd.setCursor(0, 0);
      lcd.print("Paused");
    }
    lastDisplayState = state;
  }

  // 시간 출력 (WAITING 상태일 땐 생략)
  if (state != WAITING) {.
    lcd.setCursor(0, 1);
    lcd.print(hours);
    lcd.print(":");
    lcd.print(minutes);
    lcd.print(":");
    if (seconds < 10) lcd.print("0");
    lcd.print(seconds);
    lcd.print("   ");
  }

  delay(100);
}