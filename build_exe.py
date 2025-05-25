#!/usr/bin/env python3
"""
PyInstaller를 사용하여 exe 파일 생성 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """exe 파일 빌드"""
    
    # 현재 디렉토리
    current_dir = Path.cwd()
    
    print("🚀 음성파일 전사 프로그램 빌드 시작...")
    
    # PyInstaller 명령어 구성
    cmd = [
        "pyinstaller",
        "--onefile",  # 단일 exe 파일 생성
        "--windowed",  # 콘솔 창 숨기기 (GUI 앱)
        "--name=음성파일전사프로그램",  # exe 파일명
        "--icon=icon.ico",  # 아이콘 파일 (있다면)
        "--add-data=requirements.txt;.",  # 추가 데이터 파일
        "--hidden-import=whisper",
        "--hidden-import=pyannote.audio",
        "--hidden-import=torch",
        "--hidden-import=torchaudio",
        "--hidden-import=PyQt5",
        "--hidden-import=librosa",
        "--hidden-import=soundfile",
        "--hidden-import=pydub",
        "--clean",  # 빌드 전 정리
        "audio_transcriber.py"
    ]
    
    try:
        print("📦 PyInstaller 실행 중...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 빌드 성공!")
            print(f"📁 생성된 exe 파일: {current_dir}/dist/음성파일전사프로그램.exe")
            
            # 파일 크기 확인
            exe_path = current_dir / "dist" / "음성파일전사프로그램.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📏 파일 크기: {size_mb:.1f} MB")
            
        else:
            print("❌ 빌드 실패!")
            print("오류 내용:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ PyInstaller가 설치되지 않았습니다.")
        print("설치 명령어: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ 빌드 중 오류 발생: {e}")
        return False
    
    return result.returncode == 0

def create_spec_file():
    """더 세밀한 제어를 위한 spec 파일 생성"""
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# 데이터 파일들
datas = [
    ('requirements.txt', '.'),
]

# 숨겨진 import들
hiddenimports = [
    'whisper',
    'pyannote.audio',
    'torch',
    'torchaudio', 
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtWidgets',
    'PyQt5.QtGui',
    'librosa',
    'soundfile',
    'pydub',
    'numpy',
    'pandas',
    'matplotlib',
    'csv',
    'json',
    'pathlib',
]

a = Analysis(
    ['audio_transcriber.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='음성파일전사프로그램',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)
'''
    
    with open('audio_transcriber.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("📝 Spec 파일이 생성되었습니다: audio_transcriber.spec")

def main():
    print("=" * 50)
    print("🎵 음성파일 전사 프로그램 빌드 도구")
    print("=" * 50)
    
    print("\n📋 빌드 옵션:")
    print("1. 기본 빌드 (권장)")
    print("2. Spec 파일 생성 후 빌드")
    print("3. Spec 파일만 생성")
    
    choice = input("\n선택하세요 (1-3): ").strip()
    
    if choice == "1":
        # 기본 빌드
        if build_exe():
            print("\n🎉 빌드가 완료되었습니다!")
            print("\n📌 사용법:")
            print("1. dist 폴더의 exe 파일을 원하는 위치에 복사")
            print("2. exe 파일을 실행하여 프로그램 사용")
            print("3. 처음 실행시 모델 다운로드로 시간이 걸릴 수 있음")
        
    elif choice == "2":
        # Spec 파일 생성 후 빌드
        create_spec_file()
        print("\n🔧 Spec 파일로 빌드 중...")
        try:
            result = subprocess.run([
                "pyinstaller", 
                "--clean", 
                "audio_transcriber.spec"
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ Spec 파일 빌드 성공!")
            else:
                print("❌ Spec 파일 빌드 실패!")
                print(result.stderr)
        except Exception as e:
            print(f"❌ 빌드 중 오류: {e}")
    
    elif choice == "3":
        # Spec 파일만 생성
        create_spec_file()
        print("\n✅ Spec 파일이 생성되었습니다.")
        print("수동 빌드 명령어: pyinstaller --clean audio_transcriber.spec")
    
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main() 