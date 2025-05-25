# 🚀 음성파일 전사 프로그램 - 완전 설치 가이드

이 가이드는 **완전 초보자**도 쉽게 따라할 수 있도록 **모든 단계**를 상세히 설명합니다.

## 📋 목차
1. [시스템 확인](#1-시스템-확인)
2. [Python 설치](#2-python-설치)
3. [프로그램 다운로드](#3-프로그램-다운로드)
4. [의존성 설치](#4-의존성-설치)
5. [HuggingFace 계정 생성](#5-huggingface-계정-생성)
6. [첫 실행](#6-첫-실행)
7. [EXE 파일 빌드](#7-exe-파일-빌드)
8. [문제 해결](#8-문제-해결)

---

## 1. 시스템 확인

### ✅ 최소 시스템 요구사항
- **운영체제**: Windows 10/11 (64-bit)
- **RAM**: 8GB 이상
- **저장공간**: 10GB 이상 여유공간
- **인터넷**: 모델 다운로드용 (처음에만 필요)

### 🔍 내 컴퓨터 사양 확인법
1. `Windows 키 + R` 누르기
2. `dxdiag` 입력 후 엔터
3. 시스템 탭에서 메모리(RAM) 확인
4. `설정` → `시스템` → `정보`에서 Windows 버전 확인

---

## 2. Python 설치

### 🐍 Python 설치 단계

1. **Python 공식 사이트 방문**
   - [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Python 3.11 다운로드** (가장 안정적)
   - "Download Python 3.11.x" 버튼 클릭
   - **중요**: 3.12 이상은 일부 라이브러리 호환성 문제 가능

3. **설치 실행**
   - 다운로드한 `.exe` 파일 실행
   - ✅ **"Add Python to PATH" 체크박스 반드시 체크**
   - "Install Now" 클릭

4. **설치 확인**
   ```cmd
   # CMD 창에서 실행
   python --version
   pip --version
   ```
   
   **결과 예시:**
   ```
   Python 3.11.7
   pip 23.3.1
   ```

### ⚠️ 설치 시 주의사항
- **PATH 추가 필수**: 체크하지 않으면 명령어가 작동하지 않음
- **관리자 권한**: 설치 시 관리자 권한으로 실행
- **기존 Python**: 다른 버전이 있다면 제거 후 설치 권장

---

## 3. 프로그램 다운로드

### 📁 GitHub에서 다운로드

1. **저장소 방문**
   - GitHub 주소로 이동

2. **코드 다운로드**
   - 녹색 "Code" 버튼 클릭
   - "Download ZIP" 선택
   - 압축 해제

3. **폴더 구조 확인**
   ```
   audio-transcriber/
   ├── audio_transcriber.py
   ├── build_exe.py
   ├── requirements.txt
   ├── README.md
   └── setup_guide.md
   ```

---

## 4. 의존성 설치

### 🔧 필수 라이브러리 설치

1. **명령 프롬프트(CMD) 열기**
   - `Windows 키 + R`
   - `cmd` 입력 후 엔터

2. **프로젝트 폴더로 이동**
   ```cmd
   cd C:\Users\사용자명\Downloads\audio-transcriber
   ```

3. **가상환경 생성 (권장)**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **성공 시 화면:**
   ```
   (venv) C:\Users\사용자명\Downloads\audio-transcriber>
   ```

4. **의존성 설치**
   ```cmd
   pip install -r requirements.txt
   ```

### ⏰ 설치 시간 안내
- **총 소요시간**: 10-30분 (인터넷 속도에 따라)
- **용량**: 약 3-4GB
- **주요 구성요소**:
  - PyTorch (딥러닝 프레임워크)
  - Whisper (음성인식 모델)
  - pyannote-audio (화자분리)
  - PyQt5 (GUI 인터페이스)

### 🚨 설치 오류 해결

**오류 1: pip 버전 문제**
```cmd
python -m pip install --upgrade pip
```

**오류 2: CUDA 관련 오류**
```cmd
# CPU 버전으로 PyTorch 재설치
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**오류 3: Visual Studio Build Tools 오류**
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 설치

---

## 5. HuggingFace 계정 생성

### 🤗 화자 분리 기능을 위한 필수 단계

1. **HuggingFace 계정 생성**
   - [https://huggingface.co/join](https://huggingface.co/join) 방문
   - 이메일로 회원가입

2. **토큰 생성**
   - 로그인 후 프로필 아이콘 클릭
   - "Settings" → "Access Tokens"
   - "New token" 클릭
   - 토큰 이름 입력 (예: "audio-transcriber")
   - Role: "Read" 선택
   - "Generate token" 클릭

3. **토큰 저장**
   - 생성된 토큰을 **안전한 곳에 복사해서 저장**
   - 예시: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### ⚠️ 토큰 관련 주의사항
- **토큰은 한 번만 표시됨**: 반드시 복사해서 저장
- **개인정보**: 다른 사람과 공유하지 말 것
- **용도**: 화자 분리 기능에만 사용 (선택사항)

---

## 6. 첫 실행

### 🎵 프로그램 실행하기

1. **가상환경 활성화** (이전에 생성했다면)
   ```cmd
   venv\Scripts\activate
   ```

2. **프로그램 실행**
   ```cmd
   python audio_transcriber.py
   ```

3. **첫 실행 시 발생하는 일**
   - GUI 창이 열림
   - 백그라운드에서 Whisper 모델 자동 다운로드
   - 모델 크기에 따라 5-10분 소요 가능

### 🎯 첫 번째 전사 테스트

1. **테스트용 음성 파일 준비**
   - 짧은 MP3/WAV 파일 (1-2분 권장)
   - 명확한 음성이 포함된 파일

2. **기본 전사 실행**
   - "파일 선택" → 음성 파일 선택
   - 모델: "small" 선택 (빠른 테스트용)
   - 화자 분리: 체크 해제 (첫 테스트)
   - "전사 시작" 클릭

3. **결과 확인**
   - 진행률 표시줄 확인
   - 완료 후 결과 텍스트 확인
   - "TXT 저장" 클릭하여 파일 저장

---

## 7. EXE 파일 빌드

### 📦 실행 파일 만들기

1. **빌드 스크립트 실행**
   ```cmd
   python build_exe.py
   ```

2. **빌드 옵션 선택**
   - "1. 기본 빌드 (권장)" 선택
   - 빌드 시간: 10-20분

3. **결과 확인**
   - `dist` 폴더에 `음성파일전사프로그램.exe` 생성
   - 파일 크기: 약 500MB-1GB

### 🎁 EXE 파일 배포

1. **EXE 파일 위치**
   ```
   프로젝트폴더/dist/음성파일전사프로그램.exe
   ```

2. **다른 컴퓨터에서 사용**
   - EXE 파일만 복사하면 즉시 실행 가능
   - Python 설치 불필요
   - 첫 실행 시 모델 다운로드 필요

---

## 8. 문제 해결

### 🔧 자주 발생하는 문제들

#### 문제 1: "python이 내부 또는 외부 명령으로 인식되지 않습니다"
**원인**: Python이 PATH에 추가되지 않음
**해결**:
1. Python 재설치 시 "Add Python to PATH" 체크
2. 또는 수동으로 PATH 추가

#### 문제 2: 메모리 부족 오류
**원인**: RAM 부족 또는 큰 모델 사용
**해결**:
1. 작은 모델 사용 (tiny, small)
2. 다른 프로그램 종료
3. 가상 메모리 늘리기

#### 문제 3: GPU 관련 오류
**원인**: CUDA 드라이버 문제
**해결**:
1. 처리 장치를 "CPU"로 변경
2. GPU 드라이버 업데이트

#### 문제 4: 화자 분리 실패
**원인**: HuggingFace 토큰 문제
**해결**:
1. 토큰 재발급
2. 화자 분리 기능 비활성화

### 📞 추가 도움이 필요한 경우

1. **에러 메시지 캡처**: 정확한 오류 내용 확인
2. **시스템 정보 수집**: 운영체제, Python 버전 등
3. **GitHub Issues**: 문제 보고 및 해결책 검색

---

## 🎉 완료!

축하합니다! 이제 음성파일 전사 프로그램을 완전히 설치하고 사용할 수 있습니다.

### 🚀 다음 단계
1. **다양한 모델 테스트**: 품질과 속도 비교
2. **화자 분리 기능 사용**: HF 토큰으로 더 고급 기능 활용
3. **EXE 파일 배포**: 다른 사람들과 공유

### 💡 사용 팁
- **GPU 사용**: NVIDIA GPU가 있다면 반드시 활용
- **모델 선택**: medium 모델이 품질과 속도의 균형점
- **파일 관리**: 결과 파일을 체계적으로 관리

**즐거운 음성 전사 되세요! 🎵** 