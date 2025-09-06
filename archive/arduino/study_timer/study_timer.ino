#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2); // LCD 포트번호 설정

// 버튼 포트 전역변수 설정
const int startBTN = 2;
const int resetBTN = 3;

// 타이머 초 변수
unsigned long startTime = 0;
unsigned long totalTime = 0;
bool isRunning = false;

// 버튼 이전상태 변수 (눌렀다 땠을 때 눌림 방지용)
bool lastStartState = HIGH;
bool lastResetState = HIGH;

void setup() {
  // 핀 세팅
  lcd.init();
  lcd.backlight();
  pinMode(startBTN, INPUT_PULLUP);
  pinMode(resetBTN, INPUT_PULLUP);
}

void loop() {
  
}